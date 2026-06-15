import numpy as np

def extract_summary_features(summary):
    sem_gpas = summary["semester_gpas"]

    avg_gpa = np.mean(sem_gpas)
    gpa_slope = sem_gpas[-1] - sem_gpas[0] if len(sem_gpas) > 1 else 0
    last_gpa = sem_gpas[-1]
    volatility = np.std(sem_gpas)

    credit_eff = summary["total_credits_completed"] / max(summary["total_credits_attempted"], 1)

    weakest_domain = min(summary["domain_gpas"].values())

    return np.array([
        avg_gpa,
        gpa_slope,
        last_gpa,
        volatility,
        credit_eff,
        summary["fail_withdrawal_count"],
        weakest_domain
    ])