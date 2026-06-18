import re

import numpy as np
import torch

from app.model import get_gru, get_risk, is_loaded

GRADE_POINTS = {
    "A": 4.0, "A-": 3.7, "B+": 3.3, "B": 3.0, "B-": 2.7,
    "C+": 2.3, "C": 2.0, "C-": 1.7, "D+": 1.3, "D": 1.0, "F": 0.0,
}
DOMAIN_PREFIXES = {
    "MATH": ["MATH", "STAT", "CALC"],
    "CS":   ["CSAI", "CS", "AI", "ML", "DATA", "DSAI", "IT", "SW"],
    "PHYS": ["PHYS", "CHEM", "BIOL"],
    "ENG":  ["ENG", "ECE", "ME", "CE", "MECH", "ELEC"],
    "BUS":  ["BUS", "MGT", "FIN", "ACCT", "ECON"],
    "HUM":  ["ENGL", "HUM", "SOC", "PHIL", "ARAB"],
}


def _grade_pts(grade: str) -> float | None:
    g = (grade or "").strip().strip("[]")
    if g in ("W", "WF", "WD", "IP", "P", "NP", "I", "AU"):
        return None
    return GRADE_POINTS.get(g)


def _tag_domain(course_id: str) -> str:
    prefix = course_id.split()[0].upper() if course_id else ""
    for dom, prefixes in DOMAIN_PREFIXES.items():
        if any(prefix.startswith(p) for p in prefixes):
            return dom
    return "other"


def _parse_term_order(term_name: str):
    parts = term_name.strip().split()
    season = {"Spring": 0, "Summer": 1, "Fall": 2}
    return (int(parts[0]), season.get(parts[1], 3))


# ─── Feature builders ────────────────────────────────────────────────────────

def _build_gru_sequence(semesters: list, seq_feats: list, seq_mu, seq_sd, maxlen: int):
    """
    Build a zero-padded sequence tensor for the GRU.
    seq_feats = ['term_gpa', 'running_cum']
    Shape: [1, maxlen, len(seq_feats)]
    """
    rows = []
    for s in semesters:
        tgpa = s.get("term_gpa")
        cgpa = s.get("cumulative_gpa")
        if tgpa is None or cgpa is None:
            continue
        rows.append([tgpa, cgpa])

    if not rows:
        raise ValueError("No semesters with valid GPA found")

    # Keep last maxlen steps, pad at front with zeros if shorter
    rows = rows[-maxlen:]
    seq = np.zeros((maxlen, len(seq_feats)), dtype=np.float32)
    seq[-len(rows):] = rows

    # Normalize
    mu = np.array(seq_mu, dtype=np.float32)
    sd = np.array(seq_sd, dtype=np.float32)
    sd[sd == 0] = 1.0
    seq = (seq - mu) / sd

    return torch.tensor(seq, dtype=torch.float32).unsqueeze(0)  # [1, maxlen, 2]


def _build_risk_features(semesters: list, feature_names: list) -> np.ndarray:
    """
    Build the 13 scalar features expected by risk_xgboost.joblib:
    n_semesters, last_gpa, first_gpa, min_term_gpa, n_poor_terms,
    gpa_trend_slope, gpa_volatility, gpa_drop, fail_rate,
    credit_completion_rate, consecutive_poor_semesters, dom_MATH, dom_min
    """
    term_gpas  = [s["term_gpa"] for s in semesters if s.get("term_gpa") is not None]
    if not term_gpas:
        raise ValueError("No valid term GPAs in transcript")

    n = len(term_gpas)
    first_gpa = term_gpas[0]
    last_gpa  = term_gpas[-1]
    min_gpa   = min(term_gpas)

    # GPA trend slope
    if n >= 2:
        xs = np.arange(n, dtype=float)
        slope = float(np.polyfit(xs, term_gpas, 1)[0])
    else:
        slope = 0.0

    volatility = float(np.std(term_gpas)) if n > 1 else 0.0

    # Max GPA drop between consecutive sems
    drops = [term_gpas[i] - term_gpas[i + 1] for i in range(n - 1)]
    gpa_drop = float(max(drops)) if drops else 0.0

    # Poor terms (< 2.5)
    n_poor = sum(1 for g in term_gpas if g < 2.5)

    # Consecutive poor semesters
    consec = 0; max_consec = 0
    for g in term_gpas:
        if g < 2.5:
            consec += 1; max_consec = max(max_consec, consec)
        else:
            consec = 0

    # Fail/withdrawal rate + credit completion
    total_courses = 0; fail_count = 0
    total_attempted = 0; total_earned = 0
    domain_grades: dict[str, list] = {}

    for s in semesters:
        total_attempted += s.get("attempted_credits", 0)
        total_earned    += s.get("earned_credits", 0)
        for c in s.get("courses", []):
            grade = c.get("grade", "")
            total_courses += 1
            g = (grade or "").strip().strip("[]")
            if g in ("F", "WF", "W", "WD"):
                fail_count += 1
            gpts = _grade_pts(grade)
            if gpts is not None:
                dom = _tag_domain(c.get("course_id", ""))
                domain_grades.setdefault(dom, []).append(gpts)

    fail_rate           = fail_count / max(total_courses, 1)
    credit_completion   = total_earned / max(total_attempted, 1)
    dom_math            = float(np.mean(domain_grades["MATH"])) if "MATH" in domain_grades else 3.0
    all_dom_means       = [float(np.mean(v)) for v in domain_grades.values() if v]
    dom_min             = min(all_dom_means) if all_dom_means else 3.0

    feature_map = {
        "n_semesters":               float(n),
        "last_gpa":                  float(last_gpa),
        "first_gpa":                 float(first_gpa),
        "min_term_gpa":              float(min_gpa),
        "n_poor_terms":              float(n_poor),
        "gpa_trend_slope":           slope,
        "gpa_volatility":            volatility,
        "gpa_drop":                  gpa_drop,
        "fail_rate":                 fail_rate,
        "credit_completion_rate":    credit_completion,
        "consecutive_poor_semesters": float(max_consec),
        "dom_MATH":                  dom_math,
        "dom_min":                   dom_min,
    }

    return np.array([feature_map[f] for f in feature_names], dtype=np.float32).reshape(1, -1)


# ─── Main predict function ────────────────────────────────────────────────────

def predict(req_dict: dict) -> dict:
    if not is_loaded():
        raise RuntimeError("Models not loaded — run train.py first")

    gru_model, seq_mu, seq_sd, maxlen, seq_feats = get_gru()
    risk_clf, le, feat_names, class_weights       = get_risk()

    # Sort semesters chronologically
    semesters = sorted(req_dict["semesters"], key=lambda s: _parse_term_order(s["term_name"]))

    # ── GRU: predict next semester GPA ───────────────────────────────────────
    x_seq = _build_gru_sequence(semesters, seq_feats, seq_mu, seq_sd, maxlen)
    with torch.no_grad():
        raw = gru_model(x_seq).item()
    predicted_gpa = float(np.clip(raw, 0.0, 4.0))

    # ── XGBoost: predict risk level ──────────────────────────────────────────
    x_risk = _build_risk_features(semesters, feat_names)
    proba  = risk_clf.predict_proba(x_risk)[0]
    classes = list(le.classes_)
    risk_probs = {cls: round(float(p), 3) for cls, p in zip(classes, proba)}
    risk_level = le.inverse_transform(risk_clf.predict(x_risk))[0]

    # ── Trajectory from last 2–3 term GPAs ──────────────────────────────────
    term_gpas = [s["term_gpa"] for s in semesters if s.get("term_gpa") is not None]
    if len(term_gpas) >= 2:
        slope = term_gpas[-1] - term_gpas[-2]
    else:
        slope = 0.0
    trajectory = "Improving" if slope > 0.15 else "Declining" if slope < -0.15 else "Stable"

    cum_gpa = semesters[-1].get("cumulative_gpa") or (sum(term_gpas) / len(term_gpas))

    reasoning = {
        "n_semesters_completed":  len(term_gpas),
        "last_term_gpa":          round(term_gpas[-1], 3) if term_gpas else None,
        "cumulative_gpa":         round(float(cum_gpa), 3),
        "gpa_trend":              f"{slope:+.3f}",
        "risk_level":             risk_level,
    }

    return {
        "predicted_gpa":     round(predicted_gpa, 3),
        "risk_level":        risk_level,
        "risk_probabilities": risk_probs,
        "trajectory":        trajectory,
        "reasoning":         reasoning,
    }
