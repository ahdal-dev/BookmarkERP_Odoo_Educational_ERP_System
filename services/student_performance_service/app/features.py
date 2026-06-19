"""Rebuild the model feature vectors from a transcript summary (serving side).

Uses the same feature engineering as train.py so the inputs seen at inference
match what the models were trained on.
"""
import numpy as np
import pandas as pd


def slope(series):
    if len(series) < 2:
        return 0.0
    return float(np.polyfit(np.arange(len(series)), series, 1)[0])


def consecutive_poor(gpas):
    consec = mx = 0
    for g in gpas:
        consec = consec + 1 if g < 2.0 else 0
        mx = max(mx, consec)
    return mx


def features_from_summary(summary, feature_order):
    """Return a 1-row DataFrame with columns in `feature_order` (the FEATURES list)."""
    g = list(summary["semester_gpas"])
    dom = summary.get("domain_gpas", {}) or {}
    attempted = summary.get("total_credits_attempted", len(g) * 15)
    completed = summary.get("total_credits_completed", 0)
    n_courses_est = max(round(attempted / 3), 1)

    feats = dict(
        n_semesters=len(g),
        last_gpa=g[-1],
        first_gpa=g[0],
        min_term_gpa=min(g),
        n_poor_terms=sum(1 for x in g if x < 2.0),
        gpa_trend_slope=slope(g),
        gpa_volatility=float(np.std(g)),
        gpa_drop=(g[0] - g[-1]) if len(g) > 1 else 0.0,
        fail_rate=summary.get("fail_withdrawal_count", 0) / n_courses_est,
        credit_completion_rate=completed / max(attempted, 1),
        consecutive_poor_semesters=consecutive_poor(g),
        dom_MATH=float(dom.get("MATH", np.nan)),
        dom_min=min(dom.values()) if dom else np.nan,
    )
    return pd.DataFrame([feats])[feature_order].fillna(0.0)


def gpa_sequence(semester_gpas):
    """Build the [term_gpa, running_cum] sequence used by the GRU."""
    g = list(semester_gpas)
    run = np.cumsum(g) / np.arange(1, len(g) + 1)
    return np.stack([g, run], axis=1)
