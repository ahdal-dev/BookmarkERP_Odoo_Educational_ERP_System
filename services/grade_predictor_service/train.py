#!/usr/bin/env python3
"""
Grade Predictor — training script.

Reproduces the full pipeline from train.ipynb:
  1. Load & merge course catalog
  2. Load transcripts
  3. Feature engineering
  4. Student-level train / cal / test split (leakage-free)
  5. Optuna hyperparameter search (falls back to RandomizedSearchCV)
  6. XGBRegressor + calibrated XGBClassifier
  7. Conformal grade-interval calibration
  8. Save bundle to models/grade_predictor_v3.pkl

Usage:
    python train.py [--data path/to/transcripts.json] [--out models/grade_predictor_v3.pkl]
"""

import argparse
import json
import os
import random
import re
import sys
import warnings
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import joblib
import mlflow
import mlflow.sklearn
import numpy as np
import pandas as pd
from sklearn.calibration import CalibratedClassifierCV
from sklearn.frozen import FrozenEstimator
from sklearn.metrics import accuracy_score, mean_absolute_error, mean_squared_error
from sklearn.model_selection import GroupShuffleSplit, RandomizedSearchCV, StratifiedGroupKFold
from sklearn.preprocessing import LabelEncoder
from xgboost import XGBClassifier, XGBRegressor

warnings.filterwarnings("ignore")

# ── Try Optuna ────────────────────────────────────────────────────────────────
try:
    import optuna
    optuna.logging.set_verbosity(optuna.logging.WARNING)
    OPTUNA_AVAILABLE = True
    print("Optuna available — hyperparameter search will run for real.")
except ImportError:
    OPTUNA_AVAILABLE = False
    print("Optuna not found — falling back to RandomizedSearchCV.")

# ─────────────────────────────────────────────────────────────────────────────
# 1. CONSTANTS & GRADE UTILITIES
# ─────────────────────────────────────────────────────────────────────────────

GRADE_TO_POINTS: Dict[str, float] = {
    "A": 4.00, "A-": 3.70,
    "B+": 3.30, "B": 3.00, "B-": 2.70,
    "C+": 2.50, "C": 2.00, "C-": 1.70,
    "D": 1.00, "F": 0.00,
}
LETTER_GRADES = ["A", "A-", "B+", "B", "B-", "C+", "C", "C-", "D", "F"]
GRADE_IDX: Dict[str, int] = {g: i for i, g in enumerate(LETTER_GRADES)}
_THRESHOLDS = sorted(GRADE_TO_POINTS.items(), key=lambda x: x[1], reverse=True)

DOMAIN_MAP: Dict[str, str] = {
    "MATH": "MATH", "PHYS": "PHYS", "CHEM": "CHEM", "BIOL": "BIOL",
    "CSCI": "CS", "CSAI": "CS", "DSAI": "CS",
    "SW": "CS", "SWAPD": "CS", "SWGCG": "CS", "SWHCI": "CS",
    "IT": "CS", "ITNS": "CS", "ITCC": "CS",
    "CIE": "ENG", "NANENG": "ENG", "REE": "ENG", "SPC": "ENG",
    "ENV": "ENG", "ENGR": "ENG",
    "BMS": "BIO", "NANOSC": "BIO", "MATSCI": "SCI",
    "ENGL": "HUM", "SCH": "HUM",
    "BGEN": "BUS", "ECON": "BUS", "FINC": "BUS", "MGMT": "BUS",
    "MKTG": "BUS", "SCHN": "BUS", "BLAW": "BUS", "BACT": "BUS",
    "BENT": "BUS", "BDAT": "BUS", "BMAT": "BUS", "BCSE": "BUS",
    "BIFT": "BUS", "BTEM": "BUS", "SUST": "BUS", "BUS": "BUS",
    "AIE": "CS",
}
SEASON_ORDER = {"spring": 0, "summer": 1, "fall": 2}

FEATURE_COLS = [
    "prereq_grade", "prereq_missing_flag", "domain_avg_grade",
    "domain_avg_missing", "cumulative_gpa", "credit_load",
    "fail_withdrawal_count", "grade_trend", "courses_completed",
    "retake_flag", "course_credits", "prereq_count",
    "prereqs_satisfied_count", "prereqs_missing_count",
    "last_semester_gpa", "last_2_semesters_gpa", "recent_domain_avg",
    "historical_course_avg", "course_fail_rate", "course_std",
    "satisfied_prereq_ratio", "avg_all_prereq_grade", "prereq_chain_depth",
    "previous_attempts_count", "retake_count", "improvement_after_retake",
    "decay_weighted_gpa",
]

LOW_CONF_THRESHOLD = 0.40
LIMITED_HISTORY_MIN = 3
CONFORMAL_ALPHA = 0.10


def numeric_to_letter(gpa: float) -> str:
    for letter, pts in _THRESHOLDS:
        if gpa >= pts - 0.15:
            return letter
    return "F"


def clean_grade(raw: str) -> Optional[str]:
    g = raw.strip().upper().replace("[", "").replace("]", "")
    return g if g in GRADE_TO_POINTS else None


def grade_to_gpa(raw: str) -> Optional[float]:
    g = clean_grade(raw)
    return GRADE_TO_POINTS.get(g) if g else None


def is_passing(raw: str) -> bool:
    g = clean_grade(raw)
    return g is not None and GRADE_TO_POINTS[g] >= 1.0


def is_withdrawn(raw: str) -> bool:
    return raw.strip().upper() in ("W", "[W]")


def is_in_progress(raw: str) -> bool:
    return raw.strip().upper() in ("IP", "[IP]")


def semester_sort_key(term_name: str) -> Tuple[int, int]:
    parts = term_name.strip().split()
    year = next((int(p) for p in parts if p.isdigit()), 9999)
    season = next((p.lower() for p in parts if p.lower() in SEASON_ORDER), "fall")
    return (year, SEASON_ORDER[season])


def get_domain(course_id: str) -> str:
    prefix = re.split(r"[\s\d]", course_id)[0]
    return DOMAIN_MAP.get(prefix.upper(), "OTHER")


# ─────────────────────────────────────────────────────────────────────────────
# 2. COURSE CATALOG
# ─────────────────────────────────────────────────────────────────────────────

_INLINE_CATALOG = {
    "MATH 101": {"name": "Calculus I", "credits": 3, "prerequisites": []},
    "MATH 102": {"name": "Calculus II", "credits": 3, "prerequisites": ["MATH 101"]},
    "MATH 103": {"name": "Calculus for Computational Sciences", "credits": 3, "prerequisites": []},
    "MATH 104": {"name": "Linear Algebra", "credits": 3, "prerequisites": []},
    "MATH 105": {"name": "Probability and Statistics", "credits": 3, "prerequisites": ["MATH 103"]},
    "MATH 201": {"name": "Linear Algebra and Vector Geometry", "credits": 3, "prerequisites": []},
    "MATH 202": {"name": "Ordinary Differential Equations", "credits": 3, "prerequisites": ["MATH 101"]},
    "MATH 301": {"name": "Real Analysis", "credits": 3, "prerequisites": ["MATH 102"]},
    "PHYS 101": {"name": "General Physics I", "credits": 3, "prerequisites": []},
    "PHYS 102": {"name": "General Physics II", "credits": 3, "prerequisites": ["PHYS 101"]},
    "PHYS 201": {"name": "Modern Physics", "credits": 3, "prerequisites": ["PHYS 102"]},
    "CHEM 101": {"name": "General Chemistry I", "credits": 3, "prerequisites": []},
    "CHEM 111": {"name": "General Chemistry Lab I", "credits": 1, "prerequisites": []},
    "BIOL 101": {"name": "Biology I", "credits": 3, "prerequisites": []},
    "BIOL 111": {"name": "Biology Lab I", "credits": 1, "prerequisites": []},
    "ENGL 152": {"name": "Academic Writing", "credits": 3, "prerequisites": []},
    "CSCI 101": {"name": "Introduction to Computing", "credits": 3, "prerequisites": []},
    "CSAI 100": {"name": "Introduction to Computing", "credits": 3, "prerequisites": []},
    "CSAI 101": {"name": "Programming I", "credits": 3, "prerequisites": []},
    "CSAI 102": {"name": "Programming II", "credits": 3, "prerequisites": ["CSAI 101"]},
    "CSAI 151": {"name": "Data Structures", "credits": 3, "prerequisites": ["CSAI 101"]},
    "CSAI 201": {"name": "Object-Oriented Programming", "credits": 3, "prerequisites": ["CSAI 101"]},
    "CSAI 202": {"name": "Database Systems", "credits": 3, "prerequisites": ["CSAI 101"]},
    "CSAI 203": {"name": "Software Engineering", "credits": 3, "prerequisites": ["CSAI 151"]},
    "CSAI 204": {"name": "Operating Systems", "credits": 3, "prerequisites": ["CSAI 201"]},
    "CSAI 205": {"name": "Computer Networks", "credits": 3, "prerequisites": ["CSAI 101"]},
    "CSAI 251": {"name": "Algorithms", "credits": 3, "prerequisites": ["CSAI 151"]},
    "CSAI 252": {"name": "Computer Organization", "credits": 3, "prerequisites": []},
    "CSAI 253": {"name": "Machine Learning", "credits": 3, "prerequisites": ["CSAI 202", "MATH 105"]},
    "CSAI 301": {"name": "Artificial Intelligence", "credits": 3, "prerequisites": ["CSAI 253"]},
    "CSAI 302": {"name": "Advanced AI", "credits": 3, "prerequisites": ["CSAI 301"]},
    "CSAI 498": {"name": "Senior Design Project I", "credits": 1, "prerequisites": []},
    "CSAI 499": {"name": "Senior Design Project II", "credits": 3, "prerequisites": ["CSAI 498"]},
}


def _normalize_cid(raw: str) -> str:
    if not raw:
        return ""
    s = " ".join(str(raw).strip().split())
    m = re.match(r"^([A-Za-z]+)\s*(\d.*)$", s)
    if m:
        s = f"{m.group(1).upper()} {m.group(2)}"
    return s


def _try_load_generator_catalog(service_dir: Path) -> dict:
    candidates = [
        service_dir / "Transcript_generator__1_.py",
        service_dir.parent.parent / "Transcript_generator(1).py",
        service_dir.parent.parent / "Transcript_generator__1_.py",
    ]
    for candidate in candidates:
        if not candidate.exists():
            continue
        try:
            src = candidate.read_text(encoding="utf-8")
            start = src.index("COURSE_CATALOG = {")
            i = src.index("{", start)
            depth = 0
            for j in range(i, len(src)):
                if src[j] == "{":
                    depth += 1
                elif src[j] == "}":
                    depth -= 1
                    if depth == 0:
                        end = j + 1
                        break
            ns = {}
            exec("COURSE_CATALOG = " + src[i:end], ns)
            raw = ns["COURSE_CATALOG"]
            flat = {}
            for key, val in raw.items():
                if not isinstance(val, dict):
                    continue
                first_v = next(iter(val.values()), None) if val else None
                if isinstance(first_v, dict) and "name" in first_v:
                    for cid, info in val.items():
                        flat[_normalize_cid(cid)] = {
                            "name": info.get("name", cid),
                            "credits": info.get("credits", 3),
                            "prerequisites": [_normalize_cid(p) for p in info.get("prerequisites", [])],
                        }
                elif "name" in val:
                    flat[_normalize_cid(key)] = {
                        "name": val.get("name", key),
                        "credits": val.get("credits", 3),
                        "prerequisites": [_normalize_cid(p) for p in val.get("prerequisites", [])],
                    }
            print(f"  Full catalog parsed from: {candidate} ({len(flat)} courses)")
            return flat
        except Exception as e:
            print(f"  Could not parse {candidate}: {e}")
    return {}


def build_catalog(service_dir: Path) -> Tuple[Dict, Dict, set]:
    course_info = _try_load_generator_catalog(service_dir)
    if not course_info:
        print("  Generator not found — using inline snapshot.")
        course_info = {_normalize_cid(k): v for k, v in _INLINE_CATALOG.items()}
    else:
        for cid, info in _INLINE_CATALOG.items():
            course_info.setdefault(_normalize_cid(cid), {
                "name": info["name"],
                "credits": info["credits"],
                "prerequisites": [_normalize_cid(p) for p in info["prerequisites"]],
            })
    prerequisite_map = {cid: info["prerequisites"] for cid, info in course_info.items()}
    catalog_ids = set(course_info)
    return course_info, prerequisite_map, catalog_ids


# ─────────────────────────────────────────────────────────────────────────────
# 3. TRANSCRIPT HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def flatten_courses_before_semester(semesters: list, before_sem_index: int) -> list:
    courses = []
    for sem in semesters[:before_sem_index]:
        for c in sem["courses"]:
            raw = c.get("grade", "")
            courses.append({
                "course_id": c["course_id"],
                "grade": raw,
                "grade_clean": clean_grade(raw),
                "gpa_pts": grade_to_gpa(raw),
                "credits": c.get("credits", 3),
                "semester": sem["term_name"],
                "is_passing": is_passing(raw),
                "is_w": is_withdrawn(raw),
            })
    return courses


def best_grade_for_course(records: list, course_id: str):
    recs = [r for r in records if r["course_id"] == course_id]
    if not recs:
        return None
    passing = [r for r in recs if r["is_passing"]]
    return max(passing, key=lambda r: r["gpa_pts"]) if passing else recs[-1]


def check_all_prerequisites(records: list, target: str, prereq_map: dict, course_info: dict) -> dict:
    prereqs = prereq_map.get(target, [])
    satisfied, missing = [], []
    for pid in prereqs:
        rec = best_grade_for_course(records, pid)
        if rec and rec["is_passing"]:
            satisfied.append({
                "course_id": pid,
                "course_name": course_info.get(pid, {}).get("name", pid),
                "grade": rec["grade_clean"],
                "gpa_pts": rec["gpa_pts"],
            })
        else:
            missing.append(pid)
    best_gpa = max((s["gpa_pts"] for s in satisfied), default=None)
    return {
        "prereqs": prereqs,
        "satisfied": satisfied,
        "missing": missing,
        "best_grade": best_gpa,
        "has_prereqs": len(prereqs) > 0,
    }


def get_prerequisite_chain_depth(course_id: str, prereq_map: dict, visited=None) -> int:
    if visited is None:
        visited = set()
    if course_id in visited:
        return 0
    visited.add(course_id)
    prereqs = prereq_map.get(course_id, [])
    if not prereqs:
        return 0
    return 1 + max(get_prerequisite_chain_depth(p, prereq_map, visited.copy()) for p in prereqs)


def compute_gpa_trend(semesters: list, before_sem_index: int) -> float:
    gpas = []
    for sem in semesters[:before_sem_index]:
        tgpa = sem.get("term_statistics", {}).get("term_gpa")
        if tgpa is not None:
            gpas.append(tgpa)
    gpas = gpas[-3:]
    if len(gpas) < 2:
        return 0.0
    x = np.arange(len(gpas), dtype=float)
    return float(np.polyfit(x, gpas, 1)[0])


def decay_weighted_avg(prior_courses: list, decay: float = 0.85) -> Optional[float]:
    sorted_c = sorted(prior_courses, key=lambda r: semester_sort_key(r["semester"]))
    gpas = [r["gpa_pts"] for r in sorted_c if r["gpa_pts"] is not None]
    if not gpas:
        return None
    weights = [decay ** i for i in range(len(gpas) - 1, -1, -1)]
    return float(np.average(gpas, weights=weights))


def build_course_stats(transcripts: list) -> dict:
    course_grades: Dict[str, list] = defaultdict(list)
    course_fails: Dict[str, list] = defaultdict(lambda: [0, 0])
    for student in transcripts:
        for sem in student["semesters"]:
            for c in sem["courses"]:
                raw = c.get("grade", "")
                label = grade_to_gpa(raw)
                if label is None and not is_withdrawn(raw):
                    continue
                cid = c["course_id"]
                val = label if label is not None else 0.0
                course_grades[cid].append(val)
                course_fails[cid][1] += 1
                if val < 1.0:
                    course_fails[cid][0] += 1
    stats = {}
    for cid, grades in course_grades.items():
        stats[cid] = {
            "avg": float(np.mean(grades)),
            "std": float(np.std(grades)) if len(grades) > 1 else 0.0,
            "fail_rate": course_fails[cid][0] / max(1, course_fails[cid][1]),
        }
    return stats


# ─────────────────────────────────────────────────────────────────────────────
# 4. FEATURE EXTRACTION
# ─────────────────────────────────────────────────────────────────────────────

def extract_features(student: dict, target_course: str, sem_index: int,
                     prereq_map: dict, course_info: dict, course_stats: dict,
                     label_gpa=None) -> dict:
    semesters = student["semesters"]
    prior = flatten_courses_before_semester(semesters, sem_index)
    domain = get_domain(target_course)
    cs = course_stats

    prereq_result = check_all_prerequisites(prior, target_course, prereq_map, course_info)
    if prereq_result["has_prereqs"]:
        prereq_gpa = prereq_result["best_grade"] if prereq_result["best_grade"] is not None else 0.0
        prereq_missing_flag = 0 if prereq_result["best_grade"] is not None else 1
    else:
        cum = (semesters[sem_index - 1]["running_totals"]["cumulative_gpa"]
               if sem_index > 0 else student.get("cumulative_gpa", 2.5))
        prereq_gpa = cum
        prereq_missing_flag = -1

    domain_grades = [r["gpa_pts"] for r in prior
                     if get_domain(r["course_id"]) == domain and r["gpa_pts"] is not None]
    domain_avg = float(np.mean(domain_grades)) if domain_grades else None
    domain_avg_flag = 0 if domain_avg is not None else 1
    if domain_avg is None:
        cum = (semesters[sem_index - 1]["running_totals"]["cumulative_gpa"]
               if sem_index > 0 else student.get("cumulative_gpa", 2.5))
        domain_avg = cum

    cum_gpa = (semesters[sem_index - 1]["running_totals"].get("cumulative_gpa", student.get("cumulative_gpa", 2.5))
               if sem_index > 0 else student.get("cumulative_gpa", 2.5))

    credit_load = (semesters[sem_index]["term_statistics"].get("attempted_credits", 15)
                   if sem_index < len(semesters) else 15)

    fw_count = sum(1 for r in prior if r["grade_clean"] == "F" or r["is_w"])
    trend = compute_gpa_trend(semesters, sem_index)
    completed = sum(1 for r in prior if r["is_passing"])
    decay_gpa = decay_weighted_avg(prior)
    if decay_gpa is None:
        decay_gpa = cum_gpa
    retake = int(sum(1 for r in prior if r["course_id"] == target_course) > 0)
    course_credits = course_info.get(target_course, {}).get("credits", 3)

    sem_gpa_list = [s.get("term_statistics", {}).get("term_gpa")
                    for s in semesters[:sem_index]
                    if s.get("term_statistics", {}).get("term_gpa") is not None]
    last_sem_gpa = sem_gpa_list[-1] if sem_gpa_list else cum_gpa
    last_2_sem_gpa = float(np.mean(sem_gpa_list[-2:])) if sem_gpa_list else cum_gpa

    recent_domain = []
    for s in semesters[max(0, sem_index - 2):sem_index]:
        for c in s["courses"]:
            if get_domain(c["course_id"]) == domain:
                v = grade_to_gpa(c.get("grade", ""))
                if v is not None:
                    recent_domain.append(v)
    recent_domain_avg = float(np.mean(recent_domain)) if recent_domain else domain_avg

    cstat = cs.get(target_course, {})
    hist_course_avg = cstat.get("avg", cum_gpa)
    course_fail_rate = cstat.get("fail_rate", 0.1)
    course_std = cstat.get("std", 0.5)

    n_prereqs = len(prereq_result["prereqs"])
    satisfied_ratio = len(prereq_result["satisfied"]) / n_prereqs if n_prereqs > 0 else 1.0
    all_prereq_gpas = [s["gpa_pts"] for s in prereq_result["satisfied"]]
    avg_all_prereq_grade = float(np.mean(all_prereq_gpas)) if all_prereq_gpas else prereq_gpa
    prereq_chain_depth = get_prerequisite_chain_depth(target_course, prereq_map)

    target_records = [r for r in prior if r["course_id"] == target_course]
    previous_attempts = len(target_records)
    retake_count = max(0, previous_attempts - 1)
    improvement = 0.0
    if retake_count > 0 and len(target_records) >= 2:
        first_v = target_records[0]["gpa_pts"]
        last_v = target_records[-1]["gpa_pts"]
        if first_v is not None and last_v is not None:
            improvement = last_v - first_v

    feat = {
        "prereq_grade": prereq_gpa,
        "prereq_missing_flag": prereq_missing_flag,
        "domain_avg_grade": domain_avg,
        "domain_avg_missing": domain_avg_flag,
        "cumulative_gpa": cum_gpa,
        "credit_load": credit_load,
        "fail_withdrawal_count": fw_count,
        "grade_trend": trend,
        "courses_completed": completed,
        "retake_flag": retake,
        "course_credits": course_credits,
        "prereq_count": n_prereqs,
        "prereqs_satisfied_count": len(prereq_result["satisfied"]),
        "prereqs_missing_count": len(prereq_result["missing"]),
        "last_semester_gpa": last_sem_gpa,
        "last_2_semesters_gpa": last_2_sem_gpa,
        "recent_domain_avg": recent_domain_avg,
        "historical_course_avg": hist_course_avg,
        "course_fail_rate": course_fail_rate,
        "course_std": course_std,
        "satisfied_prereq_ratio": satisfied_ratio,
        "avg_all_prereq_grade": avg_all_prereq_grade,
        "prereq_chain_depth": prereq_chain_depth,
        "previous_attempts_count": previous_attempts,
        "retake_count": retake_count,
        "improvement_after_retake": improvement,
        "decay_weighted_gpa": decay_gpa,
        "_student_id": student["student_id"],
        "_target_course": target_course,
        "_domain": domain,
    }
    if label_gpa is not None:
        feat["label"] = label_gpa
    return feat


# ─────────────────────────────────────────────────────────────────────────────
# 5. DATASET CONSTRUCTION
# ─────────────────────────────────────────────────────────────────────────────

def build_dataset(transcripts: list, prereq_map: dict, course_info: dict,
                  course_stats: dict) -> Tuple[pd.DataFrame, pd.DataFrame]:
    rows = []
    skipped = 0
    for student in transcripts:
        semesters = student["semesters"]
        for sem_idx, sem in enumerate(semesters):
            if sem_idx == 0:
                continue
            for course in sem["courses"]:
                raw = course.get("grade", "")
                if is_in_progress(raw) or raw.strip().upper() in ("P", "[P]"):
                    skipped += 1
                    continue
                label = 0.0 if is_withdrawn(raw) else grade_to_gpa(raw)
                if label is None:
                    skipped += 1
                    continue
                feat = extract_features(
                    student, course["course_id"], sem_idx,
                    prereq_map, course_info, course_stats, label_gpa=label,
                )
                rows.append(feat)

    print(f"  Dataset rows: {len(rows):,}  (skipped: {skipped:,})")
    df_raw = pd.DataFrame(rows)
    meta_cols = ["_student_id", "_target_course", "_domain"]
    df_meta = df_raw[meta_cols].copy()
    df = df_raw[FEATURE_COLS + ["label"]].copy()
    return df, df_meta


# ─────────────────────────────────────────────────────────────────────────────
# 6. MODEL TRAINING
# ─────────────────────────────────────────────────────────────────────────────

DET = dict(random_state=42, n_jobs=1, tree_method="hist")


def _ece(conf: np.ndarray, correct: np.ndarray, nbins: int = 10) -> float:
    edges = np.linspace(0, 1, nbins + 1)
    e = 0.0
    for b in range(nbins):
        m = (conf > edges[b]) & (conf <= edges[b + 1])
        if m.sum():
            e += m.mean() * abs(conf[m].mean() - correct[m].mean())
    return float(e)


def _eval_letters(pred: list, true: list) -> Tuple[float, float]:
    exact = np.mean(np.array(pred) == np.array(true))
    w1 = np.mean([abs(GRADE_IDX[a] - GRADE_IDX[b]) <= 1 for a, b in zip(pred, true)])
    return float(exact), float(w1)


def train(transcripts_path: Path, output_path: Path, service_dir: Path,
          mlflow_uri: str = None, experiment: str = "Grade_Predictor_Service"):
    print("\n=== 1. Building course catalog ===")
    course_info, prereq_map, catalog_ids = build_catalog(service_dir)
    print(f"  Courses: {len(course_info):,}  |  With prerequisites: {sum(1 for v in prereq_map.values() if v)}")

    print("\n=== 2. Loading transcripts ===")
    with open(transcripts_path, "r", encoding="utf-8") as f:
        raw_transcripts = json.load(f)
    transcripts = []
    for t in raw_transcripts:
        d = dict(t)
        d["semesters"] = sorted(t.get("semesters", []), key=lambda s: semester_sort_key(s["term_name"]))
        transcripts.append(d)
    print(f"  Loaded {len(transcripts):,} student transcripts.")

    print("\n=== 3. Train / test split ===")
    all_ids = list(set(t["student_id"] for t in transcripts))
    random.seed(42)
    random.shuffle(all_ids)
    n_test = max(1, int(len(all_ids) * 0.20))
    test_ids = set(all_ids[:n_test])
    train_ids = set(all_ids[n_test:])
    print(f"  Students — train: {len(train_ids)}  test: {len(test_ids)}")

    print("\n=== 4. Building course stats (train-only) ===")
    train_transcripts = [t for t in transcripts if t["student_id"] in train_ids]
    course_stats = build_course_stats(train_transcripts)
    print(f"  Course stats computed for {len(course_stats):,} courses.")

    print("\n=== 5. Feature engineering ===")
    df, df_meta = build_dataset(transcripts, prereq_map, course_info, course_stats)
    print(f"  Feature matrix shape: {df.shape}")

    print("\n=== 6. Splitting into fit / cal / test ===")
    LE = LabelEncoder()
    LE.fit(LETTER_GRADES)
    X = df[FEATURE_COLS].values
    y_num = df["label"].values
    y_let = np.array([numeric_to_letter(v) for v in y_num])
    y_enc = LE.transform(y_let)
    sid_all = df_meta["_student_id"].values

    train_mask = np.array([s in train_ids for s in sid_all])
    test_mask = np.array([s in test_ids for s in sid_all])
    tr_pos = np.where(train_mask)[0]
    gss = GroupShuffleSplit(n_splits=1, test_size=0.25, random_state=42)
    fit_rel, cal_rel = next(gss.split(X[tr_pos], y_enc[tr_pos], groups=sid_all[tr_pos]))
    fit_pos = tr_pos[fit_rel]
    cal_pos = tr_pos[cal_rel]
    test_pos = np.where(test_mask)[0]

    assert set(sid_all[fit_pos]).isdisjoint(sid_all[cal_pos]), "fit/cal student leak"
    assert set(sid_all[fit_pos]).isdisjoint(sid_all[test_pos]), "fit/test student leak"
    assert set(sid_all[cal_pos]).isdisjoint(sid_all[test_pos]), "cal/test student leak"

    X_fit, y_fit, ye_fit = X[fit_pos], y_num[fit_pos], y_enc[fit_pos]
    X_cal, y_cal, ye_cal = X[cal_pos], y_num[cal_pos], y_enc[cal_pos]
    X_test, y_test, ye_test = X[test_pos], y_num[test_pos], y_enc[test_pos]
    letters_true = [numeric_to_letter(v) for v in y_test]
    sid_train = sid_all[fit_pos]
    print(f"  Rows — fit: {len(y_fit):,}  cal: {len(y_cal):,}  test: {len(y_test):,}")

    letter_fit = np.array([numeric_to_letter(v) for v in y_fit])
    class_counts = pd.Series(letter_fit).value_counts()
    n_classes = len(class_counts)
    sample_weights = np.array([len(letter_fit) / (n_classes * class_counts.get(g, 1)) for g in letter_fit])
    sample_weights /= sample_weights.min()

    gkf_search = StratifiedGroupKFold(n_splits=3)

    print("\n=== 7. Hyperparameter search (regressor) ===")
    if OPTUNA_AVAILABLE:
        import optuna as _optuna

        def _reg_objective(trial):
            params = dict(
                n_estimators=trial.suggest_int("n_estimators", 250, 500),
                max_depth=trial.suggest_int("max_depth", 3, 6),
                learning_rate=trial.suggest_float("learning_rate", 0.03, 0.12, log=True),
                subsample=trial.suggest_float("subsample", 0.7, 1.0),
                colsample_bytree=trial.suggest_float("colsample_bytree", 0.6, 1.0),
                min_child_weight=trial.suggest_int("min_child_weight", 1, 8),
                reg_alpha=trial.suggest_float("reg_alpha", 1e-3, 1.0, log=True),
                reg_lambda=trial.suggest_float("reg_lambda", 1e-2, 5.0, log=True),
                eval_metric="mae", **DET,
            )
            maes = []
            for tr_i, va_i in gkf_search.split(X_fit, ye_fit, groups=sid_train):
                m = XGBRegressor(**params)
                m.fit(X_fit[tr_i], y_fit[tr_i], sample_weight=sample_weights[tr_i], verbose=False)
                maes.append(mean_absolute_error(y_fit[va_i], np.clip(m.predict(X_fit[va_i]), 0, 4)))
            return float(np.mean(maes))

        study = _optuna.create_study(direction="minimize",
                                     sampler=_optuna.samplers.TPESampler(seed=42))
        study.optimize(_reg_objective, n_trials=15, show_progress_bar=False)
        BEST_REG_PARAMS = study.best_params
        BEST_REG_PARAMS.update({"eval_metric": "mae", **DET})
        print(f"  Best CV MAE: {study.best_value:.4f}  params: {BEST_REG_PARAMS}")
    else:
        from scipy.stats import loguniform, randint, uniform
        param_dist = {
            "n_estimators": randint(200, 700), "max_depth": randint(3, 8),
            "learning_rate": loguniform(0.02, 0.15), "subsample": uniform(0.6, 0.4),
            "colsample_bytree": uniform(0.5, 0.5), "min_child_weight": randint(1, 11),
            "reg_alpha": loguniform(1e-3, 2.0), "reg_lambda": loguniform(1e-3, 5.0),
        }
        rs = RandomizedSearchCV(
            XGBRegressor(eval_metric="mae", **DET), param_dist,
            n_iter=20, cv=3, scoring="neg_mean_absolute_error",
            random_state=42, n_jobs=1, verbose=0,
        )
        rs.fit(X_fit, y_fit, sample_weight=sample_weights)
        BEST_REG_PARAMS = dict(rs.best_params_)
        BEST_REG_PARAMS.update({"eval_metric": "mae", **DET})
        print(f"  Best CV MAE: {-rs.best_score_:.4f}")

    print("\n=== 8. Training models ===")
    MODEL_REG = XGBRegressor(**BEST_REG_PARAMS)
    MODEL_REG.fit(X_fit, y_fit, sample_weight=sample_weights, verbose=False)
    print("  XGBRegressor trained.")

    CLF_PARAMS = dict(
        n_estimators=BEST_REG_PARAMS.get("n_estimators", 400),
        max_depth=BEST_REG_PARAMS.get("max_depth", 5),
        learning_rate=BEST_REG_PARAMS.get("learning_rate", 0.05),
        subsample=BEST_REG_PARAMS.get("subsample", 0.85),
        colsample_bytree=BEST_REG_PARAMS.get("colsample_bytree", 0.8),
        min_child_weight=BEST_REG_PARAMS.get("min_child_weight", 3),
        reg_alpha=BEST_REG_PARAMS.get("reg_alpha", 0.1),
        reg_lambda=BEST_REG_PARAMS.get("reg_lambda", 1.0),
        eval_metric="mlogloss", num_class=len(LETTER_GRADES), **DET,
    )
    BASE_CLF = XGBClassifier(**CLF_PARAMS)
    BASE_CLF.fit(X_fit, ye_fit, sample_weight=sample_weights)
    print("  XGBClassifier trained.")

    print("\n=== 9. Calibration comparison ===")
    candidates = {
        "none": BASE_CLF,
        "sigmoid": CalibratedClassifierCV(FrozenEstimator(BASE_CLF), method="sigmoid"),
        "isotonic": CalibratedClassifierCV(FrozenEstimator(BASE_CLF), method="isotonic"),
    }
    scoreboard = {}
    print(f"  {'calibration':>11} | {'exact':>6} {'within1':>7} | {'ECE':>6}")
    for name, est in candidates.items():
        if name != "none":
            est.fit(X_cal, ye_cal)
        p = est.predict_proba(X_test)
        lp = LE.inverse_transform(np.argmax(p, axis=1))
        conf = p.max(axis=1)
        ex, w1 = _eval_letters(list(lp), letters_true)
        correct = (lp == np.array(letters_true)).astype(float)
        ece = _ece(conf, correct)
        scoreboard[name] = dict(est=est, exact=ex, within1=w1, ece=ece)
        print(f"  {name:>11} | {ex:>6.3f} {w1:>7.3f} | {ece:>6.3f}")

    best_calib = max(scoreboard, key=lambda k: scoreboard[k]["exact"] - scoreboard[k]["ece"])
    MODEL_CLF = scoreboard[best_calib]["est"]
    CALIB_METHOD = best_calib
    print(f"  Selected calibration: '{best_calib}'")

    print("\n=== 10. Evaluation ===")
    y_pred_reg = np.clip(MODEL_REG.predict(X_test), 0.0, 4.0)
    letters_pred_reg = [numeric_to_letter(v) for v in y_pred_reg]
    proba = MODEL_CLF.predict_proba(X_test)
    letters_pred_clf = list(LE.inverse_transform(np.argmax(proba, axis=1)))
    y_pred_clf_num = np.array([GRADE_TO_POINTS[g] for g in letters_pred_clf])

    mae_reg = mean_absolute_error(y_test, y_pred_reg)
    exact_reg, w1_reg = _eval_letters(letters_pred_reg, letters_true)
    mae_clf = mean_absolute_error(y_test, y_pred_clf_num)
    exact_clf, w1_clf = _eval_letters(letters_pred_clf, letters_true)
    ece_clf = _ece(proba.max(axis=1), (np.array(letters_pred_clf) == np.array(letters_true)).astype(float))

    def _score(exact, w1, ece): return 0.6 * exact + 0.3 * w1 - 0.1 * ece
    USE_CLASSIFIER = _score(exact_clf, w1_clf, ece_clf) >= _score(exact_reg, w1_reg, 0.0)

    if USE_CLASSIFIER:
        letters_pred_best = letters_pred_clf
        y_pred_best = y_pred_clf_num
    else:
        letters_pred_best = letters_pred_reg
        y_pred_best = y_pred_reg

    mae_best = mean_absolute_error(y_test, y_pred_best)
    rmse_best = float(np.sqrt(mean_squared_error(y_test, y_pred_best)))
    exact_best, w1_best = _eval_letters(letters_pred_best, letters_true)

    print(f"  Active model: {'Classifier' if USE_CLASSIFIER else 'Regressor'}")
    print(f"  MAE: {mae_best:.4f}  RMSE: {rmse_best:.4f}  "
          f"Exact: {exact_best:.2%}  Within-1: {w1_best:.2%}")

    print("\n=== 11. Conformal interval calibration ===")
    cal_letters_pred = list(LE.inverse_transform(np.argmax(MODEL_CLF.predict_proba(X_cal), axis=1)))
    cal_letters_true = [numeric_to_letter(v) for v in y_cal]
    scores = np.array([abs(GRADE_IDX[a] - GRADE_IDX[b])
                       for a, b in zip(cal_letters_pred, cal_letters_true)])
    n = len(scores)
    qlevel = min(1.0, np.ceil((n + 1) * (1 - CONFORMAL_ALPHA)) / n)
    CONFORMAL_K = int(np.quantile(scores, qlevel, method="higher"))
    print(f"  Conformal radius k = {CONFORMAL_K} at {1 - CONFORMAL_ALPHA:.0%} coverage (cal n={n})")

    print("\n=== 12. MLflow logging & saving bundle ===")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    bundle = {
        "model_reg": MODEL_REG,
        "model_clf": MODEL_CLF,
        "use_classifier": USE_CLASSIFIER,
        "label_encoder": LE,
        "course_stats": course_stats,
        "feature_cols": FEATURE_COLS,
        "course_info": course_info,
        "prerequisite_map": prereq_map,
        "catalog_ids": catalog_ids,
        "conformal_k": CONFORMAL_K,
        "conformal_alpha": CONFORMAL_ALPHA,
        "calib_method": CALIB_METHOD,
        "best_reg_params": BEST_REG_PARAMS,
        "thresholds": {"low_conf": LOW_CONF_THRESHOLD, "limited_history_min": LIMITED_HISTORY_MIN},
        "metrics": {
            "mae": float(mae_best), "rmse": float(rmse_best),
            "within_1": float(w1_best), "exact_acc": float(exact_best),
        },
    }
    joblib.dump(bundle, output_path)
    size_mb = output_path.stat().st_size / 1e6
    print(f"  Saved to {output_path}  ({size_mb:.1f} MB)")

    if mlflow_uri:
        mlflow.set_tracking_uri(mlflow_uri)
    mlflow.set_experiment(experiment)

    with mlflow.start_run(run_name="grade_predictor_train"):
        # params
        mlflow.log_param("n_students_train", len(train_ids))
        mlflow.log_param("n_students_test", len(test_ids))
        mlflow.log_param("n_rows_fit", len(y_fit))
        mlflow.log_param("n_rows_cal", len(y_cal))
        mlflow.log_param("n_rows_test", len(y_test))
        mlflow.log_param("feature_count", len(FEATURE_COLS))
        mlflow.log_param("use_classifier", USE_CLASSIFIER)
        mlflow.log_param("calib_method", CALIB_METHOD)
        mlflow.log_param("conformal_k", CONFORMAL_K)
        mlflow.log_param("conformal_alpha", CONFORMAL_ALPHA)
        mlflow.log_param("optuna_used", OPTUNA_AVAILABLE)
        mlflow.log_param("git_commit", os.getenv("GITHUB_SHA", "local"))
        for k, v in BEST_REG_PARAMS.items():
            if k not in ("random_state", "n_jobs", "tree_method", "eval_metric"):
                mlflow.log_param(f"reg_{k}", v)

        # metrics
        mlflow.log_metric("MAE", float(mae_best))
        mlflow.log_metric("RMSE", float(rmse_best))
        mlflow.log_metric("exact_letter_acc", float(exact_best))
        mlflow.log_metric("within_1_acc", float(w1_best))

        # artifacts
        mlflow.log_artifact(str(output_path), artifact_path="model")
        mlflow.sklearn.log_model(MODEL_REG, "model_reg")

        print(f"  MLflow run logged to experiment '{experiment}'")

    print("\nDone.")


# ─────────────────────────────────────────────────────────────────────────────
# ENTRY POINT
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    SERVICE_DIR = Path(__file__).resolve().parent

    # default data path: look in service dir then project data/
    _default_data = (SERVICE_DIR / "transcripts.json"
                     if (SERVICE_DIR / "transcripts.json").exists()
                     else SERVICE_DIR.parent.parent / "data" / "transcripts.json")
    print(f"Default transcripts.json path: {_default_data}")
    parser = argparse.ArgumentParser(description="Train the grade predictor model.")
    parser.add_argument("--data", type=Path, default=_default_data,
                        help="Path to transcripts.json")
    parser.add_argument("--out", type=Path,
                        default=SERVICE_DIR / "models" / "grade_predictor_v3.pkl",
                        help="Output path for the model bundle")
    parser.add_argument("--mlflow-uri", type=str,
                        default=os.getenv("MLFLOW_TRACKING_URI"),
                        help="MLflow tracking URI (defaults to MLFLOW_TRACKING_URI env var)")
    parser.add_argument("--experiment", type=str,
                        default="Grade_Predictor_Service",
                        help="MLflow experiment name")
    args = parser.parse_args()

    if not args.data.exists():
        print(f"ERROR: transcripts.json not found at {args.data}")
        print("Pass the correct path with --data path/to/transcripts.json")
        sys.exit(1)

    train(args.data, args.out, SERVICE_DIR,
          mlflow_uri=args.mlflow_uri, experiment=args.experiment)
