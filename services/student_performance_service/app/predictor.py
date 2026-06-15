# -*- coding: utf-8 -*-
"""Combined inference: GRU next-sem GPA + XGBoost risk + alerts/recommendations."""
import numpy as np
import torch

from app.model import RISK_BUNDLE, GRU_MODEL, GRU_META
from app.features import features_from_summary, gpa_sequence, slope

FEATURES = RISK_BUNDLE["features"]
LE = RISK_BUNDLE["label_encoder"]
CLF = RISK_BUNDLE["model"]

_MU = GRU_META["seq_mu"]
_SD = GRU_META["seq_sd"]
_MAXLEN = GRU_META["maxlen"]


def _pad(seq):
    seq = (seq - _MU) / _SD
    p = np.zeros((_MAXLEN, seq.shape[1]), dtype=np.float32)
    p[-len(seq):] = seq
    return p


def _next_gpa(semester_gpas):
    seq = gpa_sequence(semester_gpas)
    x = torch.tensor(_pad(seq), dtype=torch.float32).unsqueeze(0)
    with torch.no_grad():
        return float(GRU_MODEL(x).item())


def predict(summary):
    g = list(summary["semester_gpas"])
    Xf = features_from_summary(summary, FEATURES)

    next_gpa = round(min(4.0, max(0.0, _next_gpa(g))), 2)

    completed = summary.get("total_credits_completed", len(g) * 15)
    remaining = max(0, 120 - completed)
    grad_gpa = round((summary["cumulative_gpa"] * completed + next_gpa * remaining)
                     / max(completed + remaining, 1), 2)

    proba = CLF.predict_proba(Xf)[0]
    p = {LE.classes_[k]: float(proba[k]) for k in range(len(proba))}
    risk_level = max(p, key=p.get)
    risk_score = round(p.get("High", 0.0) * 1.0 + p.get("Medium", 0.0) * 0.5, 2)

    sl = slope(g)
    trajectory = "Improving" if sl > 0.15 else "Declining" if sl < -0.15 else "Stable"

    alerts = []
    drop = g[0] - g[-1]
    if drop >= 0.4:
        alerts.append(f"GPA dropped {round(drop, 1)} points over {len(g)} semesters")
    if summary.get("fail_withdrawal_count", 0) >= 2:
        alerts.append(f"{summary['fail_withdrawal_count']} withdrawals/failures detected, "
                      "possible course-load issue")
    if int(Xf["consecutive_poor_semesters"].iloc[0]) >= 2:
        alerts.append("Two or more consecutive semesters below 2.0 GPA")
    dom = summary.get("domain_gpas", {}) or {}
    weak = min(dom.items(), key=lambda kv: kv[1]) if dom else ("-", 3.0)
    if weak[1] < 2.5:
        alerts.append(f"Weak performance in {weak[0]} domain (avg {weak[1]})")

    recs = []
    if risk_level in ("High", "Medium") or next_gpa < 2.3:
        recs.append("Reduce credit load to 12-15 credits next semester")
    if weak[1] < 3.0:
        recs.append(f"Advising session recommended for {weak[0]} domain weakness")
    if trajectory == "Declining":
        recs.append("Schedule early check-in with academic advisor on declining trend")
    if not recs:
        recs.append("On track, maintain current study plan")

    return {
        "predictions": {
            "next_semester_gpa": next_gpa,
            "predicted_graduation_gpa": grad_gpa,
            "trajectory": trajectory,
            "risk_level": risk_level,
            "risk_score": risk_score,
        },
        "alerts": alerts,
        "recommendations": recs,
    }
