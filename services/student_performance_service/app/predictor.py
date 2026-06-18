"""
Inference logic matching the notebook's predict_point_interval() exactly.

Notebook pipeline (cell 39):
  feat = extract_features_up_to_semester(history, obs_idx)
  feat.update(extract_plan_features(study_plan, feat, history))
  feat['program_enc'] / feat['school_enc']  (label-encoded)
  X = pd.DataFrame([feat]).reindex(columns=ML_FEAT_COLS, fill_value=np.nan)
  X = imputer.transform(X)
  point  = DEPLOY_REG.predict(X)        # tail-weighted XGBRegressor
  lo, hi = cqr.predict(X)               # CQRPredictor (quantile XGB + Q adjustment)
  p_risk = clf.predict_proba(X)[0, 1]   # XGBClassifier P(GPA < 2.0)
"""

import numpy as np
import pandas as pd

from app.model import get_models, is_loaded
from app.llm_advisor import refine_recommendations
from app.train import (
    extract_features_up_to_semester,
    extract_plan_features,
    normalize_study_plan,
    parse_term_order,
    CONFIG,
)


def _to_student_dict(req: dict) -> dict:
    """Convert the API request dict into the raw transcript format the feature extractors expect."""
    semesters = []
    for s in req["semesters"]:
        semesters.append({
            "term_name": s["term_name"],
            "term_statistics": {
                "term_gpa":          s.get("term_gpa"),
                "earned_credits":    s.get("earned_credits", 0),
                "attempted_credits": s.get("attempted_credits", 0),
            },
            "running_totals": {
                "cumulative_gpa": s.get("cumulative_gpa"),
            },
            "courses": [
                {
                    "course_id": c["course_id"],
                    "grade":     c["grade"],
                    "credits":   c.get("credits", 3),
                    "title":     c.get("title", ""),
                    "subtype":   c.get("subtype", "LECTURE"),
                }
                for c in s.get("courses", [])
            ],
        })
    return {
        "student_id": req["student_id"],
        "program":    req.get("program", "Computer Science"),
        "school":     req.get("school", "Engineering"),
        "entry_year": req.get("entry_year", 2020),
        "semesters":  semesters,
    }


def predict(req: dict) -> dict:
    if not is_loaded():
        raise RuntimeError("Models not loaded — run train.py first")

    prep, reg, clf, cqr_lo, cqr_hi = get_models()
    ML_FEAT_COLS = prep["ml_feat_cols"]
    imputer      = prep["imputer"]
    le_program   = prep["le_program"]
    le_school    = prep["le_school"]
    cqr_Q        = prep["cqr_Q"]
    at_risk_thr  = prep["at_risk_threshold"]

    student = _to_student_dict(req)

    # Sort & filter valid semesters (matches build_temporal_panel logic)
    sems = sorted(student["semesters"], key=lambda x: parse_term_order(x["term_name"]))
    sems = [s for s in sems if s["term_statistics"]["term_gpa"] is not None]
    if len(sems) < 2:
        raise ValueError("At least 2 completed semesters with valid GPA are required for a reliable prediction")

    obs_idx = len(sems) - 1  # observe all available history

    # ── History features (notebook cell 12) ──────────────────────────────────
    feat = extract_features_up_to_semester(student, obs_idx)
    if feat is None:
        raise ValueError("Could not extract history features from the provided transcript")

    # ── Plan features (notebook cell 14) — this is what conditions the prediction ──
    study_plan = req.get("study_plan", [])
    feat.update(extract_plan_features(study_plan, feat, student))

    # ── Encode program / school ───────────────────────────────────────────────
    feat["program_enc"] = (
        int(le_program.transform([feat["program"]])[0])
        if feat["program"] in le_program.classes_ else -1
    )
    feat["school_enc"] = (
        int(le_school.transform([feat["school"]])[0])
        if feat["school"] in le_school.classes_ else -1
    )

    # ── Cohort features: unknown at single-student inference time →
    #    imputer will fill with training median (same as notebook behavior for new data)
    feat.setdefault("gpa_vs_cohort_mean", np.nan)
    feat.setdefault("gpa_vs_cohort_z",    np.nan)

    # ── Build feature matrix (notebook cell 39: predict_point_interval) ──────
    X = pd.DataFrame([feat]).reindex(columns=ML_FEAT_COLS, fill_value=np.nan).values
    X = imputer.transform(X)

    # ── Point prediction (DEPLOY_REG = tail-weighted XGBRegressor) ───────────
    predicted_gpa = float(np.clip(reg.predict(X)[0], 0.0, 4.0))

    # ── CQR interval (cqr.predict: lo = cqr_lo - Q, hi = cqr_hi + Q) ────────
    interval_lo = float(np.clip(cqr_lo.predict(X)[0] - cqr_Q, 0.0, 4.0))
    interval_hi = float(np.clip(cqr_hi.predict(X)[0] + cqr_Q, 0.0, 4.0))

    # ── At-risk probability P(next term GPA < 2.0) ────────────────────────────
    at_risk_prob = float(clf.predict_proba(X)[0][1])
    at_risk      = bool(at_risk_prob >= 0.5)

    # ── Graduation GPA accounting estimate (notebook cell 16) ────────────────
    curr_cgpa  = feat["current_cumulative_gpa"]
    earned     = feat["total_credits_earned"]
    remaining  = max(CONFIG.program_credits - earned, 0)
    trend_adj  = min(max(feat["gpa_slope"] * 2, -0.5), 0.5)
    proj       = float(np.clip(curr_cgpa + trend_adj, 0.0, 4.0))
    grad_gpa   = (curr_cgpa * earned + proj * remaining) / max(earned + remaining, 1)

    # ── Trajectory ───────────────────────────────────────────────────────────
    slope = feat.get("gpa_slope", 0.0)
    trajectory = "Improving" if slope > 0.10 else "Declining" if slope < -0.10 else "Stable"

    # ── Plan analysis (notebook cell 55: load / difficulty / alignment) ───────
    plan_feat      = {k: v for k, v in feat.items() if k.startswith("plan_")}
    load_delta     = float(plan_feat.get("plan_load_vs_avg", 0.0))
    diff_jump      = float(plan_feat.get("plan_difficulty_jump", 0.0))
    align          = float(plan_feat.get("plan_strength_alignment", 0.0))
    plan_is_heavy  = bool(plan_feat.get("plan_is_heavy", False))
    retake_risk    = int(plan_feat.get("plan_retake_risk_count", 0))
    weak_cr        = float(plan_feat.get("plan_weak_domain_credits", 0.0))
    new_domain     = int(plan_feat.get("plan_new_domain_courses", 0))
    plan_n_courses = int(plan_feat.get("plan_n_courses", 0))
    plan_credits   = int(plan_feat.get("plan_credit_load", 0))

    load_assessment  = ("heavier than usual" if load_delta >= 2
                        else "lighter than usual" if load_delta <= -2
                        else "in line with your usual load")
    difficulty_note  = ("a notable step up in level" if diff_jump >= 50
                        else "a step down in level" if diff_jump <= -50
                        else "a similar level to before")
    alignment_note   = ("plays to your strengths" if align > 0.1
                        else "leans on weaker subjects" if align < -0.1
                        else "is balanced across your subjects")

    plan_analysis = {
        "load_assessment":            load_assessment,
        "load_vs_personal_avg":       round(load_delta, 1),
        "difficulty_note":            difficulty_note,
        "difficulty_jump":            round(diff_jump, 1),
        "strength_alignment":         alignment_note,
        "expected_grade_in_plan":     round(float(plan_feat.get("plan_expected_gpa_from_history", curr_cgpa)), 2),
        "credits_in_weak_subjects":   int(weak_cr),
        "repeated_difficult_courses": retake_risk,
        "new_subject_courses":        new_domain,
    }

    # ── Risk flags (notebook cell 55) ─────────────────────────────────────────
    fail_c = int(feat.get("fail_count", 0))
    with_c = int(feat.get("withdrawal_count", 0))
    flags: list[str] = []
    if fail_c >= 2:                           flags.append("two_course_failures")
    elif fail_c == 1:                         flags.append("one_course_failure")
    if int(feat.get("consecutive_low_gpa", 0)) >= 2: flags.append("consecutive_gpa_decline")
    if with_c > 0:                            flags.append("withdrawal_in_last_term")
    if feat.get("last_sem_below_2", 0):       flags.append("last_gpa_below_probation")
    if slope < -0.2:                          flags.append("steep_downward_trend")
    if plan_is_heavy:                         flags.append("heavy_planned_load")
    if retake_risk > 0:                       flags.append("plan_includes_repeat_difficulty")
    if weak_cr >= 6:                          flags.append("plan_heavy_in_weak_subjects")

    # ── Recommendations (notebook cell 55 rule engine) ────────────────────────
    recommendations: list[str] = []
    if plan_is_heavy:
        recommendations.append(
            f"Your plan is {plan_credits} credits ({load_assessment}). "
            "Consider whether a lighter load would protect your GPA.")
    if retake_risk > 0:
        recommendations.append(
            "You're repeating course(s) you previously struggled with. "
            "Line up tutoring or office hours early.")
    if weak_cr >= 6:
        recommendations.append(
            "A large share of this plan is in subjects that have been harder for you — "
            "try to balance it with a course you tend to do well in.")
    if new_domain > 0:
        recommendations.append(
            f"{new_domain} course(s) are in brand-new subject areas — "
            "budget extra time while you find your footing.")
    if not recommendations:
        recommendations.append(
            "This plan looks well matched to your record — keep your current habits.")

    # ── Student message (notebook cell 55 by risk_label) ─────────────────────
    risk_label = ("High"   if (at_risk_prob >= 0.5 or predicted_gpa < 2.0)
                  else "Medium" if (at_risk_prob >= 0.2 or predicted_gpa < 2.7)
                  else "Low")
    lo_r, hi_r = round(interval_lo, 2), round(interval_hi, 2)
    pg = round(predicted_gpa, 2)
    if risk_label == "High":
        student_message = {
            "summary": (f"Your projected GPA is between {lo_r} and {hi_r} (about {pg}), "
                        f"with an estimated {at_risk_prob:.0%} chance of a difficult term. "
                        f"This plan {alignment_note} and is {load_assessment}."),
            "detail":  ("Several signals warrant attention before you finalise this plan. "
                        "Adjusting your course mix now is easier than recovering later."),
            "suggested_action": "Please review this plan with your academic advisor before registering.",
            "tone": "supportive",
        }
    elif risk_label == "Medium":
        student_message = {
            "summary": (f"With this study plan, your GPA is projected between {lo_r} and {hi_r} (about {pg}). "
                        f"The plan {alignment_note} and is {load_assessment}."),
            "detail":  "There are a few things to watch, but with steady effort this plan is workable.",
            "suggested_action": "Consider reviewing your plan at the student support centre.",
            "tone": "supportive",
        }
    else:
        student_message = {
            "summary": (f"This study plan projects a GPA between {lo_r} and {hi_r} (about {pg}). "
                        f"It {alignment_note} and is {load_assessment}."),
            "detail":  "This is a solid plan that fits your record well. Maintaining your current habits should serve you well.",
            "suggested_action": "You're set — register with confidence, and use office hours to stretch further.",
            "tone": "encouraging",
        }

    reasoning = {
        "n_semesters_completed":     int(feat.get("n_semesters_completed", 0)),
        "cumulative_gpa":            round(float(curr_cgpa), 3),
        "last_term_gpa":             round(float(feat.get("current_term_gpa", curr_cgpa)), 3),
        "gpa_slope":                 round(float(slope), 4),
        "plan_expected_gpa":         round(float(plan_feat.get("plan_expected_gpa_from_history", curr_cgpa)), 3),
        "plan_credit_load":          float(plan_credits),
        "plan_weak_domain_credits":  float(weak_cr),
        "at_risk_threshold":         at_risk_thr,
    }

    result = {
        "predicted_gpa":           round(predicted_gpa, 3),
        "interval_lo":             round(interval_lo, 3),
        "interval_hi":             round(interval_hi, 3),
        "at_risk_probability":     round(at_risk_prob, 3),
        "at_risk":                 at_risk,
        "risk_level":              risk_label,
        "trajectory":              trajectory,
        "graduation_gpa_estimate": round(float(grad_gpa), 3),
        "reasoning":               reasoning,
        "plan_analysis":           plan_analysis,
        "flags":                   flags,
        "recommendations":         recommendations,
        "student_message":         student_message,
    }

    # Pass the study plan courses so the LLM can reference them by ID
    result["_study_plan_courses"] = [
        {"course_id": c.get("course_id", ""), "title": c.get("title", ""), "credits": c.get("credits", 3)}
        for c in study_plan
    ]

    # LLM-refined recommendations (falls back to rule-based if key absent or call fails)
    llm_recs = refine_recommendations(result)
    result["llm_recommendations"] = llm_recs if llm_recs is not None else recommendations
    del result["_study_plan_courses"]  # internal field, not exposed in response

    return result
