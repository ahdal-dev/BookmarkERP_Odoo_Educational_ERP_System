from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import joblib
import numpy as np
import os
import warnings
from typing import List

warnings.filterwarnings("ignore")

app = FastAPI()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")
model_path = os.path.join(BASE_DIR, "models", "grade_predictor_v3.pkl")

bundle = None
if os.path.exists(model_path):
    try:
        bundle = joblib.load(model_path)
        MODEL_REG       = bundle["model_reg"]
        MODEL_CLF       = bundle["model_clf"]
        USE_CLASSIFIER  = bundle["use_classifier"]
        LE              = bundle["label_encoder"]
        COURSE_STATS    = bundle["course_stats"]
        FEATURE_COLS    = bundle["feature_cols"]
        COURSE_INFO     = bundle["course_info"]
        PREREQUISITE_MAP = bundle["prerequisite_map"]
        CATALOG_IDS     = bundle["catalog_ids"]
        CONFORMAL_K     = bundle["conformal_k"]
        CONFORMAL_ALPHA = bundle["conformal_alpha"]
        CALIB_METHOD    = bundle["calib_method"]
        print("Model loaded successfully!")
    except Exception as e:
        print(f"Error loading model: {e}")
        bundle = None
else:
    print(f"Model not found at {model_path}")

LETTER_GRADES = ["A", "A-", "B+", "B", "B-", "C+", "C", "C-", "D+", "D", "F"]
GRADE_TO_POINTS = {
    "A": 4.0, "A-": 3.7, "B+": 3.3, "B": 3.0, "B-": 2.7,
    "C+": 2.3, "C": 2.0, "C-": 1.7, "D+": 1.3, "D": 1.0, "F": 0.0
}
GRADE_IDX = {g: i for i, g in enumerate(LETTER_GRADES)}

DOMAIN_MAP = {
    "MATH": "Math", "PHYS": "Physics", "CHEM": "Chemistry",
    "BIOL": "Biology", "CSAI": "CS", "ENGL": "English",
    "MGMT": "Management", "ECON": "Economics",
}


def normalize_course_id(raw: str) -> str:
    return " ".join(raw.strip().upper().split())


def is_off_catalog(cid: str) -> bool:
    return cid not in CATALOG_IDS


def get_domain(cid: str) -> str:
    prefix = cid.split()[0] if cid else ""
    return DOMAIN_MAP.get(prefix, prefix)


def get_course_info(cid: str) -> dict:
    return COURSE_INFO.get(cid, {"name": cid, "credits": 3, "domain": get_domain(cid)})


def grade_to_gpa(raw: str):
    if not raw:
        return None
    g = raw.strip().upper()
    if g in ("W", "WP", "WF", "IP", "I", "TR"):
        return None
    return GRADE_TO_POINTS.get(g)


def is_passing(raw: str) -> bool:
    gpa = grade_to_gpa(raw)
    return gpa is not None and gpa >= 1.0


def is_withdrawn(raw: str) -> bool:
    return raw.strip().upper() in ("W", "WP", "WF")


def semester_sort_key(sem: str):
    order = {"spring": 0, "summer": 1, "fall": 2}
    parts = sem.lower().split()
    season = order.get(parts[0], 0) if parts else 0
    year = int(parts[1]) if len(parts) > 1 and parts[1].isdigit() else 0
    return (year, season)


def build_history_lookup(transcript_history: list):
    records = []
    for item in transcript_history:
        cid = normalize_course_id(item.get("course", item.get("course_id", "")))
        raw = item.get("grade", "")
        gpa = grade_to_gpa(raw)
        records.append({
            "course_id": cid,
            "grade": raw,
            "gpa_pts": gpa,
            "credits": get_course_info(cid)["credits"],
            "semester": item.get("semester", ""),
            "is_passing": is_passing(raw),
            "is_w": is_withdrawn(raw),
        })
    return records


def check_prerequisites(prior: list, target: str) -> dict:
    prereqs = PREREQUISITE_MAP.get(target, [])
    if not prereqs:
        return {"has_prereqs": False, "satisfied": [], "missing": [], "best_grade": None}
    passed = {r["course_id"]: r["gpa_pts"] for r in prior if r["is_passing"] and r["gpa_pts"] is not None}
    satisfied, missing = [], []
    for p in prereqs:
        if p in passed:
            satisfied.append({"course_id": p, "grade": passed[p], "course_name": get_course_info(p)["name"]})
        else:
            missing.append(p)
    best = max(passed[s["course_id"]] for s in satisfied) if satisfied else None
    return {"has_prereqs": True, "satisfied": satisfied, "missing": missing, "best_grade": best}


def numeric_to_letter(gpa: float) -> str:
    for letter, pts in [("A",4.0),("A-",3.7),("B+",3.3),("B",3.0),("B-",2.7),
                         ("C+",2.3),("C",2.0),("C-",1.7),("D+",1.3),("D",1.0)]:
        if gpa >= pts - 0.15:
            return letter
    return "F"


def predict_grade(request: dict) -> dict:
    student_id = request.get("student_id", "unknown")
    raw_target = request.get("target_course", "")
    if not raw_target:
        return {"error": "missing target_course", "student_id": student_id}

    target = normalize_course_id(raw_target)

    try:
        cum_gpa = float(np.clip(float(request.get("cumulative_gpa", 2.5)), 0.0, 4.0))
    except (TypeError, ValueError):
        cum_gpa = 2.5

    try:
        credit_load = int(request.get("current_semester_credit_load", 15))
    except (TypeError, ValueError):
        credit_load = 15

    history = request.get("transcript_history", [])
    if not isinstance(history, list):
        history = []

    prior = build_history_lookup(history)

    off_catalog = is_off_catalog(target)
    domain = get_domain(target)
    domain_grades = [r["gpa_pts"] for r in prior
                     if get_domain(r["course_id"]) == domain and r["gpa_pts"] is not None]
    domain_avg = float(np.mean(domain_grades)) if domain_grades else cum_gpa
    domain_avg_missing = 0 if domain_grades else 1

    prereq_result = check_prerequisites(prior, target)
    if prereq_result["has_prereqs"]:
        prereq_gpa = prereq_result["best_grade"] if prereq_result["best_grade"] is not None else 0.0
        prereq_flag = 0 if prereq_result["best_grade"] is not None else 1
    else:
        prereq_gpa = cum_gpa
        prereq_flag = -1

    sorted_hist = sorted(prior, key=lambda r: semester_sort_key(r["semester"]))
    sem_gpas = {}
    for r in sorted_hist:
        if r["gpa_pts"] is not None:
            sem_gpas.setdefault(r["semester"], []).append(r["gpa_pts"])
    sem_avg_list = [np.mean(v) for v in sem_gpas.values()]
    if len(sem_avg_list) >= 2:
        x = np.arange(len(sem_avg_list[-3:]), dtype=float)
        trend = float(np.polyfit(x, sem_avg_list[-3:], 1)[0])
    else:
        trend = 0.0

    last_sem_gpa = sem_avg_list[-1] if sem_avg_list else cum_gpa
    last2_sem_gpa = float(np.mean(sem_avg_list[-2:])) if len(sem_avg_list) >= 2 else cum_gpa

    course_hist = [r for r in prior if r["course_id"] == target]
    prev_attempts = len(course_hist)
    retake_flag = 1 if prev_attempts > 0 else 0
    retake_count = prev_attempts
    best_attempt = max((r["gpa_pts"] for r in course_hist if r["gpa_pts"] is not None), default=None)
    improvement = float(best_attempt - course_hist[0]["gpa_pts"]) if (
        len(course_hist) >= 2 and course_hist[0]["gpa_pts"] is not None and best_attempt is not None
    ) else 0.0

    fw_count = sum(1 for r in prior if r["grade"] in ("F","WF","W","WP") or
                   (r["gpa_pts"] is not None and r["gpa_pts"] == 0.0))
    completed = sum(1 for r in prior if r["is_passing"])

    stats = COURSE_STATS.get(target, {})
    hist_avg = stats.get("mean", cum_gpa)
    fail_rate = stats.get("fail_rate", 0.1)
    course_std = stats.get("std", 0.5)
    course_credits = get_course_info(target)["credits"]

    prereqs_list = PREREQUISITE_MAP.get(target, [])
    prereq_count = len(prereqs_list)
    prereqs_satisfied = len(prereq_result["satisfied"])
    prereqs_missing = len(prereq_result["missing"])
    satisfied_ratio = (prereqs_satisfied / prereq_count) if prereq_count > 0 else 1.0
    avg_prereq_grade = prereq_gpa

    # estimate chain depth
    def chain_depth(cid, visited=None):
        if visited is None:
            visited = set()
        if cid in visited:
            return 0
        visited.add(cid)
        prs = PREREQUISITE_MAP.get(cid, [])
        return 1 + max((chain_depth(p, visited) for p in prs), default=0) if prs else 0
    prereq_chain = chain_depth(target)

    # recent domain avg (last 2 semesters)
    recent_sems = list(sem_gpas.keys())[-2:] if len(sem_gpas) >= 2 else list(sem_gpas.keys())
    recent_domain = [r["gpa_pts"] for r in prior
                     if r["semester"] in recent_sems and get_domain(r["course_id"]) == domain
                     and r["gpa_pts"] is not None]
    recent_domain_avg = float(np.mean(recent_domain)) if recent_domain else domain_avg

    # decay-weighted GPA (more recent = higher weight)
    if prior:
        all_gpas = [r["gpa_pts"] for r in sorted_hist if r["gpa_pts"] is not None]
        if all_gpas:
            weights = np.exp(np.linspace(0, 1, len(all_gpas)))
            decay_gpa = float(np.average(all_gpas, weights=weights))
        else:
            decay_gpa = cum_gpa
    else:
        decay_gpa = cum_gpa

    feature_vec = np.array([[
        prereq_gpa, prereq_flag, domain_avg, domain_avg_missing, cum_gpa,
        credit_load, fw_count, trend, completed, retake_flag,
        course_credits, prereq_count, prereqs_satisfied, prereqs_missing,
        last_sem_gpa, last2_sem_gpa, recent_domain_avg, hist_avg,
        fail_rate, course_std, satisfied_ratio, avg_prereq_grade,
        prereq_chain, prev_attempts, retake_count, improvement, decay_gpa
    ]], dtype=float)

    if bundle is None:
        return {"error": "model not loaded", "student_id": student_id, "target_course": target}

    if USE_CLASSIFIER:
        proba = MODEL_CLF.predict_proba(feature_vec)[0]
        best_idx = int(np.argmax(proba))
        pred_letter = LE.inverse_transform([best_idx])[0]
        pred_gpa = GRADE_TO_POINTS[pred_letter]
        confidence = float(np.clip(proba[best_idx], 0.05, 0.99))
    else:
        raw_pred = float(MODEL_REG.predict(feature_vec)[0])
        pred_gpa = float(np.clip(raw_pred, 0.0, 4.0))
        pred_letter = numeric_to_letter(pred_gpa)
        confidence = float(np.clip(
            max(0.0, 1.0 - abs(pred_gpa - cum_gpa) / 4.0) - (0.15 if prereq_flag == 1 else 0),
            0.05, 0.99
        ))

    idx = GRADE_IDX.get(pred_letter, 0)
    lo = max(0, idx - CONFORMAL_K)
    hi = min(len(LETTER_GRADES) - 1, idx + CONFORMAL_K)
    grade_interval = LETTER_GRADES[lo:hi + 1]

    prereq_str = (
        "No prerequisites." if not prereq_result["has_prereqs"]
        else ("Missing: " + ", ".join(prereq_result["missing"]) if prereq_result["missing"]
              else "All prerequisites satisfied.")
    )

    return {
        "student_id": student_id,
        "target_course": target,
        "predicted_grade": pred_letter,
        "predicted_numeric": round(pred_gpa, 3),
        "confidence": round(confidence, 3),
        "grade_interval": grade_interval,
        "reasoning": {
            "prerequisite_grade": prereq_str,
            "domain_avg": f"{domain_avg:.2f} in {domain} courses" if domain_grades else f"No prior {domain} grades",
            "gpa_trend": (f"Improving (+{trend:.3f})" if trend > 0.10
                          else f"Declining ({trend:.3f})" if trend < -0.10 else f"Stable ({trend:+.3f})"),
        },
        "off_catalog": off_catalog,
        "advisory_only": True,
    }


# ── Pydantic models ──────────────────────────────────────────────────────────

class TranscriptEntry(BaseModel):
    course: str
    grade: str
    semester: str = ""


class PredictRequest(BaseModel):
    student_id: str
    target_course: str
    cumulative_gpa: float = 2.5
    current_semester_credit_load: int = 15
    transcript_history: List[TranscriptEntry] = []


# ── Endpoints ────────────────────────────────────────────────────────────────

@app.post("/predict")
def predict(req: PredictRequest):
    data = req.model_dump()
    data["transcript_history"] = [
        {"course": e["course"], "grade": e["grade"], "semester": e["semester"]}
        for e in data["transcript_history"]
    ]
    return predict_grade(data)


@app.get("/health")
def health():
    return {"status": "healthy", "model_loaded": bundle is not None}


@app.get("/courses")
def list_courses():
    return {"courses": sorted(CATALOG_IDS) if bundle else []}


@app.get("/")
def home():
    return FileResponse(os.path.join(BASE_DIR, "static", "index.html"))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
