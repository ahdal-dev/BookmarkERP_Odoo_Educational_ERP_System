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
    if not sems:
        raise ValueError("No completed semesters with valid GPA found")

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

    reasoning = {
        "n_semesters_completed":     int(feat.get("n_semesters_completed", 0)),
        "cumulative_gpa":            round(float(curr_cgpa), 3),
        "last_term_gpa":             round(float(feat.get("current_term_gpa", curr_cgpa)), 3),
        "gpa_slope":                 round(float(slope), 4),
        "plan_expected_gpa":         round(float(feat.get("plan_expected_gpa_from_history", curr_cgpa)), 3),
        "plan_credit_load":          float(feat.get("plan_credit_load", 0)),
        "plan_weak_domain_credits":  float(feat.get("plan_weak_domain_credits", 0)),
        "at_risk_threshold":         at_risk_thr,
    }

    return {
        "predicted_gpa":           round(predicted_gpa, 3),
        "interval_lo":             round(interval_lo, 3),
        "interval_hi":             round(interval_hi, 3),
        "at_risk_probability":     round(at_risk_prob, 3),
        "at_risk":                 at_risk,
        "trajectory":              trajectory,
        "graduation_gpa_estimate": round(float(grad_gpa), 3),
        "reasoning":               reasoning,
    }
