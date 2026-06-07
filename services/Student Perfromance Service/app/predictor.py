import numpy as np
from app.model import model
from app.features import extract_summary_features


def predict(summary_input):

    X = extract_summary_features(summary_input).reshape(1, -1)
    next_gpa = float(model.predict(X)[0])

    sem_gpas = summary_input["semester_gpas"]

    trend = sem_gpas[-1] - sem_gpas[0]

    trajectory = (
        "Improving" if trend > 0.2 else
        "Declining" if trend < -0.2 else
        "Stable"
    )

    predicted_grad = (summary_input["cumulative_gpa"] + next_gpa) / 2

    risk_score = (
        (3.0 - next_gpa) * 0.4 +
        summary_input["fail_withdrawal_count"] * 0.2 +
        max(0, 3.0 - summary_input["domain_gpas"]["MATH"]) * 0.2 +
        np.std(sem_gpas) * 0.3
    )

    risk_score = max(0, min(1, risk_score))

    risk_level = (
        "Low" if risk_score < 0.3 else
        "Medium" if risk_score < 0.7 else
        "High"
    )

    return {
        "next_semester_gpa": round(next_gpa, 2),
        "predicted_graduation_gpa": round(predicted_grad, 2),
        "trajectory": trajectory,
        "risk_level": risk_level,
        "risk_score": round(risk_score, 2)
    }