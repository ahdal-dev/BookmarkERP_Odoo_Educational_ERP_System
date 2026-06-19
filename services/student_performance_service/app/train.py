#!/usr/bin/env python3
"""
Student Performance Service — V5 Training Script
Replicates the full train.ipynb pipeline with MLflow tracking.

Usage:
    python app/train.py --data ../../data/transcripts.json
    python app/train.py --data data/transcripts.json --mlflow-uri http://localhost:5000
"""

import argparse
import json
import os
import pickle
import random
import re
import sys
import warnings
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

from sklearn.impute import SimpleImputer
from sklearn.metrics import (
    mean_absolute_error, mean_squared_error, r2_score,
    f1_score, precision_score, recall_score,
    roc_auc_score, average_precision_score, brier_score_loss,
)
from sklearn.model_selection import GroupShuffleSplit
from sklearn.preprocessing import LabelEncoder

import xgboost as xgb
import optuna
import mlflow
import mlflow.xgboost

optuna.logging.set_verbosity(optuna.logging.WARNING)
warnings.filterwarnings("ignore")

SEED = 42
os.environ["PYTHONHASHSEED"] = str(SEED)
random.seed(SEED)
np.random.seed(SEED)


# ─── Config ───────────────────────────────────────────────────────────────────

@dataclass(frozen=True)
class Config:
    seed: int = 42
    cohort_split_year: int = 2022
    program_credits: int = 160
    optuna_trials_reg: int = 40
    conformal_alpha: float = 0.10
    cal_frac: float = 0.30
    min_test_rows: int = 10
    plan_max_courses: int = 8
    plan_max_credits: int = 24
    at_risk_threshold: float = 2.0


CONFIG = Config()


# ─── Grade/Domain Utilities ───────────────────────────────────────────────────

GRADE_POINTS = {
    "A": 4.0, "A-": 3.7, "B+": 3.3, "B": 3.0, "B-": 2.7,
    "C+": 2.3, "C": 2.0, "C-": 1.7, "D+": 1.3, "D": 1.0, "F": 0.0,
}
DOMAINS = ["mathematics", "cs_ai", "science", "engineering",
           "business", "humanities", "general", "other"]
DOMAIN_PREFIXES = {
    "mathematics": ["MATH", "STAT", "CALC"],
    "cs_ai":       ["CSAI", "CS", "AI", "ML", "DATA", "DSAI", "IT", "ITNS", "SW", "SWGCG", "SWAPD"],
    "science":     ["PHYS", "CHEM", "BIOL", "BIO", "NANO", "SCH", "MATSCI"],
    "engineering": ["ENG", "ECE", "ME", "CHE", "CE", "MECH", "ELEC", "NANENG", "BIOMED", "BENG"],
    "business":    ["BUS", "MGT", "MKTG", "FIN", "ACCT", "ECON", "ENTP", "MGMT", "OM"],
    "humanities":  ["ENGL", "HUM", "SOC", "PHIL", "ARAB", "HIST", "ART", "COMM"],
    "general":     ["GEN", "UNIV", "PE", "SPORT", "GE", "FOC", "UNI"],
}


def normalize_grade(grade):
    if grade is None:
        return None
    clean = grade.strip().strip("[]")
    if clean in ("W", "WF", "WD", "IP", "P", "NP", "I", "AU"):
        return None
    return GRADE_POINTS.get(clean, None)


def is_failure(grade):    return (grade or "").strip().strip("[]") in ("F", "WF")
def is_withdrawal(grade): return (grade or "").strip().strip("[]") in ("W", "WD", "WF")
def is_retake(grade):     return bool(grade and grade.strip().startswith("[") and grade.strip().endswith("]"))


def tag_domain(course_id):
    prefix = course_id.split()[0].upper() if course_id else ""
    for domain, prefixes in DOMAIN_PREFIXES.items():
        if any(prefix.startswith(p) for p in prefixes):
            return domain
    return "other"


def parse_term_order(term_name):
    parts = term_name.strip().split()
    season_map = {"Spring": 0, "Summer": 1, "Fall": 2}
    return (int(parts[0]), season_map.get(parts[1], 3))


def course_level(course_id):
    nums = re.findall(r"\d+", course_id or "")
    if nums:
        lvl = int(nums[0])
        if 100 <= lvl <= 500:
            return lvl
    return None


def plausible_semester(sem):
    nc = len(sem.get("courses", []))
    cr = sem.get("term_statistics", {}).get("attempted_credits", 0)
    return 1 <= nc <= CONFIG.plan_max_courses and cr <= CONFIG.plan_max_credits


# ─── History Feature Extraction ──────────────────────────────────────────────

def extract_features_up_to_semester(student: dict, up_to_idx: int) -> dict:
    semesters_all = sorted(
        student["semesters"],
        key=lambda x: parse_term_order(x["term_name"])
    )
    semesters_all = [s for s in semesters_all if s["term_statistics"]["term_gpa"] is not None]

    if up_to_idx >= len(semesters_all):
        return None

    semesters = semesters_all[: up_to_idx + 1]
    n_sem = len(semesters)

    term_gpas    = [s["term_statistics"]["term_gpa"]         for s in semesters]
    cum_gpas     = [s["running_totals"]["cumulative_gpa"]    for s in semesters]
    att_credits  = [s["term_statistics"]["attempted_credits"] for s in semesters]
    earn_credits = [s["term_statistics"]["earned_credits"]   for s in semesters]

    feat = {
        "student_id":    student["student_id"],
        "observation_t": up_to_idx + 1,
        "program":       student["program"],
        "school":        student["school"],
        "entry_year":    student["entry_year"],
    }

    # Block A — GPA Trend
    feat["n_semesters_completed"]  = n_sem
    feat["current_cumulative_gpa"] = cum_gpas[-1]
    feat["current_term_gpa"]       = term_gpas[-1]
    feat["initial_term_gpa"]       = term_gpas[0]
    feat["rolling_gpa_mean_2"]     = np.mean(term_gpas[-2:]) if n_sem >= 2 else term_gpas[0]
    feat["rolling_gpa_mean_3"]     = np.mean(term_gpas[-3:]) if n_sem >= 3 else np.mean(term_gpas)
    feat["rolling_gpa_mean_all"]   = np.mean(term_gpas)
    feat["gpa_volatility"]         = np.std(term_gpas) if n_sem > 1 else 0.0
    feat["gpa_min"]                = np.min(term_gpas)
    feat["gpa_max"]                = np.max(term_gpas)
    feat["gpa_range"]              = feat["gpa_max"] - feat["gpa_min"]

    if n_sem >= 2:
        xs = np.arange(n_sem, dtype=float)
        slope, _, r_val, _, _ = stats.linregress(xs, term_gpas)
        feat["gpa_slope"] = slope
        feat["gpa_r_sq"]  = r_val ** 2
    else:
        feat["gpa_slope"] = 0.0
        feat["gpa_r_sq"]  = 0.0

    if n_sem >= 2:
        deltas = np.diff(term_gpas)
        feat["last_gpa_delta"]    = float(deltas[-1])
        feat["avg_gpa_delta"]     = float(np.mean(deltas))
        feat["improvement_rate"]  = float(np.mean(deltas > 0))
    else:
        feat["last_gpa_delta"]    = 0.0
        feat["avg_gpa_delta"]     = 0.0
        feat["improvement_rate"]  = 0.5

    if n_sem >= 3:
        w = np.array([0.2, 0.3, 0.5])
        feat["performance_momentum"] = float(np.dot(w, term_gpas[-3:]))
    else:
        w = np.linspace(0.3, 1.0, n_sem); w /= w.sum()
        feat["performance_momentum"] = float(np.dot(w, term_gpas))

    feat["consistency_score"]     = max(0.0, 1.0 - feat["gpa_volatility"] / 4.0)
    feat["cumulative_gpa_growth"] = cum_gpas[-1] - cum_gpas[0]
    feat["gpa_lag1"] = term_gpas[-1]
    feat["gpa_lag2"] = term_gpas[-2] if n_sem >= 2 else np.nan
    feat["gpa_lag3"] = term_gpas[-3] if n_sem >= 3 else np.nan

    consec_low = 0; max_consec_low = 0
    for g in term_gpas:
        if g < 2.5:
            consec_low += 1
            max_consec_low = max(max_consec_low, consec_low)
        else:
            consec_low = 0
    feat["consecutive_low_gpa"] = max_consec_low
    feat["total_low_gpa_sems"]  = sum(1 for g in term_gpas if g < 2.5)
    feat["last_sem_below_2"]    = int(term_gpas[-1] < 2.0)
    feat["last_sem_below_2_5"]  = int(term_gpas[-1] < 2.5)

    # Block B — Credit Load
    feat["avg_credit_load"]           = np.mean(att_credits)
    feat["last_credit_load"]          = att_credits[-1]
    feat["max_credit_load"]           = np.max(att_credits)
    feat["min_credit_load"]           = np.min(att_credits)
    feat["total_credits_attempted"]   = sum(att_credits)
    feat["total_credits_earned"]      = sum(earn_credits)
    feat["heavy_load_count"]          = sum(1 for c in att_credits if c >= 18)
    feat["light_load_count"]          = sum(1 for c in att_credits if c <= 12)
    feat["credit_load_volatility"]    = np.std(att_credits) if n_sem > 1 else 0.0
    feat["completion_rate"]           = sum(earn_credits) / max(sum(att_credits), 1)
    feat["credits_per_semester"]      = feat["total_credits_earned"] / n_sem
    feat["pace_to_graduation"]        = feat["total_credits_earned"] / CONFIG.program_credits
    earned = feat["total_credits_earned"]
    cps    = max(feat["credits_per_semester"], 1)
    feat["estimated_sems_remaining"]  = max(0, (CONFIG.program_credits - earned) / cps)

    # Block C — Risk / Failure
    fail_count = 0; withdrawal_count = 0; retake_count = 0
    poor_grade_count = 0; total_courses = 0
    repeated_courses = set(); course_seen = set()
    for sem in semesters:
        for c in sem["courses"]:
            cid   = c["course_id"]
            grade = c["grade"]
            total_courses += 1
            if is_failure(grade):    fail_count       += 1
            if is_withdrawal(grade): withdrawal_count += 1
            if is_retake(grade):
                retake_count += 1
                repeated_courses.add(cid)
            gnum = normalize_grade(grade)
            if gnum is not None and gnum < 2.0:
                poor_grade_count += 1
            if cid in course_seen:
                repeated_courses.add(cid)
            course_seen.add(cid)
    feat["fail_count"]         = fail_count
    feat["withdrawal_count"]   = withdrawal_count
    feat["retake_count"]       = retake_count
    feat["poor_grade_count"]   = poor_grade_count
    feat["repeated_courses"]   = len(repeated_courses)
    feat["total_courses"]      = total_courses
    feat["fail_rate"]          = fail_count / max(total_courses, 1)
    feat["withdrawal_rate"]    = withdrawal_count / max(total_courses, 1)
    feat["risk_signal_count"]  = fail_count + withdrawal_count + retake_count

    # Block D — Domain GPA Vectors
    domain_grades  = {d: [] for d in DOMAINS}
    domain_credits = {d: 0  for d in DOMAINS}
    for sem in semesters:
        for c in sem["courses"]:
            gnum = normalize_grade(c["grade"])
            if gnum is not None and not is_withdrawal(c["grade"]):
                d = tag_domain(c["course_id"])
                domain_grades[d].append(gnum)
                domain_credits[d] += c.get("credits", 3)
    for d in DOMAINS:
        feat[f"avg_grade_{d}"] = np.mean(domain_grades[d]) if domain_grades[d] else np.nan
        feat[f"credits_{d}"]   = domain_credits[d]
        feat[f"n_courses_{d}"] = len(domain_grades[d])
    all_flat = [g for gs in domain_grades.values() for g in gs]
    overall_mean = np.mean(all_flat) if all_flat else 2.5
    feat["domain_strength_score"] = sum(
        (np.mean(gs) - overall_mean) * len(gs)
        for gs in domain_grades.values() if gs
    ) / max(total_courses, 1)

    # Block E — Curriculum Progression
    course_levels = []
    for sem in semesters:
        for c in sem["courses"]:
            nums = re.findall(r"\d+", c["course_id"])
            if nums:
                lvl = int(nums[0])
                if 100 <= lvl <= 500:
                    course_levels.append(lvl)
    feat["avg_course_level"]      = np.mean(course_levels) if course_levels else 200
    feat["curriculum_difficulty"] = feat["avg_course_level"] / 100.0
    feat["last_sem_course_level"] = np.mean([
        int(re.findall(r"\d+", c["course_id"])[0])
        for c in semesters[-1]["courses"]
        if re.findall(r"\d+", c["course_id"])
        and 100 <= int(re.findall(r"\d+", c["course_id"])[0]) <= 500
    ]) if semesters else 200

    # Block F — Semester Seasonality
    SEASON_MAP = {"Spring": 0, "Summer": 1, "Fall": 2}
    last_term_name  = semesters[-1]["term_name"]
    last_season_str = last_term_name.strip().split()[1] if len(last_term_name.strip().split()) > 1 else "Fall"
    feat["last_sem_season"]  = SEASON_MAP.get(last_season_str, 1)
    season_counts = {"Spring": 0, "Summer": 0, "Fall": 0}
    for s in semesters:
        sname = s["term_name"].strip().split()
        if len(sname) > 1:
            season_counts[sname[1]] = season_counts.get(sname[1], 0) + 1
    feat["spring_sem_count"] = season_counts["Spring"]
    feat["summer_sem_count"] = season_counts["Summer"]
    feat["fall_sem_count"]   = season_counts["Fall"]

    # Block G — Recent Momentum Window
    if n_sem >= 2:
        feat["weighted_recent_gpa"] = 0.6 * term_gpas[-1] + 0.4 * term_gpas[-2]
    else:
        feat["weighted_recent_gpa"] = term_gpas[-1]
    feat["is_recovering"] = int(n_sem >= 2 and term_gpas[-1] > term_gpas[-2])
    if n_sem >= 2:
        deltas_g = np.diff(term_gpas)
        feat["max_gpa_drop"] = float(abs(min(deltas_g)))
        feat["max_gpa_gain"] = float(max(deltas_g))
    else:
        feat["max_gpa_drop"] = 0.0
        feat["max_gpa_gain"] = 0.0

    return feat


# ─── Study-Plan Feature Extraction ───────────────────────────────────────────

def normalize_study_plan(planned_courses: list) -> list:
    return [
        {
            "course_id": c.get("course_id", ""),
            "title":     c.get("title", ""),
            "credits":   c.get("credits", 3),
            "subtype":   c.get("subtype", "LECTURE"),
        }
        for c in (planned_courses or [])
    ]


def extract_plan_features(planned_courses: list, hist_feat: dict, student_history: dict) -> dict:
    plan    = normalize_study_plan(planned_courses)
    n       = len(plan)
    credits = [c["credits"] for c in plan]
    levels  = [lv for lv in (course_level(c["course_id"]) for c in plan) if lv is not None]

    pf = {}
    pf["plan_n_courses"]        = n
    pf["plan_credit_load"]      = float(sum(credits))
    pf["plan_avg_course_level"] = float(np.mean(levels))  if levels else 200.0
    pf["plan_max_course_level"] = float(np.max(levels))   if levels else 200.0
    pf["plan_difficulty"]       = pf["plan_avg_course_level"] / 100.0
    pf["plan_lab_count"]        = sum(1 for c in plan if "LAB" in str(c["subtype"]).upper())
    pf["plan_is_heavy"]         = int(pf["plan_credit_load"] >= 18)
    pf["plan_is_light"]         = int(pf["plan_credit_load"] <= 12)

    plan_dom_credits = {d: 0 for d in DOMAINS}
    plan_dom_counts  = {d: 0 for d in DOMAINS}
    for c in plan:
        d = tag_domain(c["course_id"])
        plan_dom_credits[d] += c["credits"]
        plan_dom_counts[d]  += 1
    for d in DOMAINS:
        pf[f"plan_credits_{d}"] = plan_dom_credits[d]
    pf["plan_n_domains"] = sum(1 for d in DOMAINS if plan_dom_counts[d] > 0)

    overall_hist_gpa = hist_feat.get("current_cumulative_gpa", 2.5)
    weak_credits, new_domain_courses = 0.0, 0
    num, den = 0.0, 0.0
    for d in DOMAINS:
        if plan_dom_credits[d] == 0:
            continue
        hist_dom = hist_feat.get(f"avg_grade_{d}", np.nan)
        if hist_dom is None or (isinstance(hist_dom, float) and np.isnan(hist_dom)):
            new_domain_courses += plan_dom_counts[d]
            expectation = overall_hist_gpa
        else:
            expectation = hist_dom
            if hist_dom < overall_hist_gpa:
                weak_credits += plan_dom_credits[d]
        num += expectation * plan_dom_credits[d]
        den += plan_dom_credits[d]
    pf["plan_expected_gpa_from_history"] = (num / den) if den > 0 else overall_hist_gpa
    pf["plan_weak_domain_credits"]       = weak_credits
    pf["plan_new_domain_courses"]        = new_domain_courses
    pf["plan_strength_alignment"]        = pf["plan_expected_gpa_from_history"] - overall_hist_gpa
    pf["plan_load_vs_avg"]               = pf["plan_credit_load"] - hist_feat.get("avg_credit_load", pf["plan_credit_load"])
    pf["plan_difficulty_jump"]           = pf["plan_avg_course_level"] - hist_feat.get("avg_course_level", pf["plan_avg_course_level"])

    past_poor = set()
    for sem in student_history.get("semesters", []):
        if sem["term_statistics"]["term_gpa"] is None:
            continue
        for c in sem["courses"]:
            g = normalize_grade(c["grade"])
            if is_failure(c["grade"]) or is_withdrawal(c["grade"]) or (g is not None and g < 2.0):
                past_poor.add(c["course_id"])
    pf["plan_retake_risk_count"] = sum(1 for c in plan if c["course_id"] in past_poor)
    return pf


# ─── Temporal Panel Builder ───────────────────────────────────────────────────

def build_temporal_panel(transcripts):
    records, skipped = [], 0
    for student in transcripts:
        sems = sorted(student["semesters"], key=lambda x: parse_term_order(x["term_name"]))
        sems = [s for s in sems if s["term_statistics"]["term_gpa"] is not None]
        if len(sems) < 2:
            continue
        for obs_idx in range(len(sems) - 1):
            next_sem = sems[obs_idx + 1]
            if not plausible_semester(next_sem):
                skipped += 1
                continue
            feat = extract_features_up_to_semester(student, obs_idx)
            if feat is None:
                continue
            study_plan = normalize_study_plan(next_sem["courses"])
            feat.update(extract_plan_features(study_plan, feat, student))
            ng = next_sem["term_statistics"]["term_gpa"]
            feat["next_semester_gpa"] = ng
            feat["at_risk_next"]      = int(ng < CONFIG.at_risk_threshold)
            curr_cgpa = feat["current_cumulative_gpa"]
            earned    = feat["total_credits_earned"]
            remaining = max(CONFIG.program_credits - earned, 0)
            trend_adj = min(max(feat["gpa_slope"] * 2, -0.5), 0.5)
            proj      = min(max(curr_cgpa + trend_adj, 0), 4.0)
            feat["graduation_gpa_estimate"] = (curr_cgpa * earned + proj * remaining) / max(earned + remaining, 1)
            records.append(feat)

    df = pd.DataFrame(records)
    print(f"Panel: {df.shape[0]} observations from {df['student_id'].nunique()} students "
          f"({skipped} degenerate plans skipped)")
    return df


# ─── CQR Class ───────────────────────────────────────────────────────────────

class CQRPredictor:
    def __init__(self, alpha=0.10, params=None):
        self.alpha = alpha
        p = dict(n_estimators=400, learning_rate=0.05, max_depth=4,
                 subsample=0.8, colsample_bytree=0.8, random_state=SEED, verbosity=0)
        if params:
            p.update({k: v for k, v in params.items()
                      if k in ("n_estimators", "max_depth", "learning_rate",
                                "subsample", "colsample_bytree", "min_child_weight")})
        self.lo = xgb.XGBRegressor(objective="reg:quantileerror", quantile_alpha=alpha / 2, **p)
        self.hi = xgb.XGBRegressor(objective="reg:quantileerror", quantile_alpha=1 - alpha / 2, **p)
        self.Q  = 0.0

    def fit(self, X_fit, y_fit, X_cal, y_cal):
        self.lo.fit(X_fit, y_fit)
        self.hi.fit(X_fit, y_fit)
        E = np.maximum(self.lo.predict(X_cal) - y_cal, y_cal - self.hi.predict(X_cal))
        n = len(E)
        k = min(int(np.ceil((1 - self.alpha) * (n + 1))), n)
        self.Q = float(np.sort(E)[k - 1])
        return self

    def predict(self, X):
        lo = np.clip(self.lo.predict(X) - self.Q, 0.0, 4.0)
        hi = np.clip(self.hi.predict(X) + self.Q, 0.0, 4.0)
        return lo, hi


# ─── Main Training Function ───────────────────────────────────────────────────

def train(
    transcripts_path: str,
    model_dir: str,
    mlflow_uri: str = None,
    experiment: str = "Student_Performance_Service",
):
    transcripts_path = Path(transcripts_path)
    if not transcripts_path.exists():
        raise FileNotFoundError(f"Transcripts not found at {transcripts_path}")

    model_dir = Path(model_dir)
    model_dir.mkdir(parents=True, exist_ok=True)

    _mlflow_ok = False
    try:
        if mlflow_uri:
            mlflow.set_tracking_uri(mlflow_uri)
        elif os.environ.get("MLFLOW_TRACKING_URI"):
            mlflow.set_tracking_uri(os.environ["MLFLOW_TRACKING_URI"])
        mlflow.set_experiment(experiment)
        _mlflow_ok = True
    except Exception as _e:
        print(f"[mlflow] tracking unavailable ({_e}) — models will still be saved locally")

    print(f"Loading transcripts from {transcripts_path}")
    with open(transcripts_path, "r", encoding="utf-8") as f:
        raw_transcripts = json.load(f)
    print(f"Loaded {len(raw_transcripts)} students")

    # Build temporal panel
    df_panel = build_temporal_panel(raw_transcripts)

    # Feature columns
    META_COLS   = ["student_id", "program", "school", "entry_year", "observation_t"]
    TARGET_COLS = ["next_semester_gpa", "at_risk_next", "graduation_gpa_estimate"]
    EXCLUDE     = set(META_COLS + TARGET_COLS)

    numeric_cols = [c for c in df_panel.columns
                    if c not in EXCLUDE and df_panel[c].dtype in [np.float64, np.int64, float, int]]

    le_program = LabelEncoder()
    le_school  = LabelEncoder()
    df_panel["program_enc"] = le_program.fit_transform(df_panel["program"])
    df_panel["school_enc"]  = le_school.fit_transform(df_panel["school"])

    ML_FEAT_COLS   = list(dict.fromkeys(numeric_cols + ["program_enc", "school_enc", "entry_year", "observation_t"]))
    HIST_FEAT_COLS = [c for c in ML_FEAT_COLS if not c.startswith("plan_")]
    PLAN_FEAT_COLS = [c for c in ML_FEAT_COLS if c.startswith("plan_")]
    print(f"Features: {len(ML_FEAT_COLS)} total (history={len(HIST_FEAT_COLS)}, plan={len(PLAN_FEAT_COLS)})")

    # Cohort split
    TRAIN = df_panel["entry_year"] <= CONFIG.cohort_split_year
    TEST  = df_panel["entry_year"] >  CONFIG.cohort_split_year
    if TEST.sum() < CONFIG.min_test_rows:
        rng = np.random.RandomState(SEED)
        students = df_panel["student_id"].unique()
        test_students = set(rng.choice(students, max(int(len(students) * 0.2), 20), replace=False))
        TRAIN = ~df_panel["student_id"].isin(test_students)
        TEST  =  df_panel["student_id"].isin(test_students)

    df_train = df_panel[TRAIN].copy()
    df_test  = df_panel[TEST].copy()
    assert not (set(df_train["student_id"]) & set(df_test["student_id"])), "Student overlap in split!"
    print(f"Train: {len(df_train)} rows / {df_train['student_id'].nunique()} students")
    print(f"Test : {len(df_test)}  rows / {df_test['student_id'].nunique()}  students")

    # Impute
    imputer = SimpleImputer(strategy="median")
    X_train = imputer.fit_transform(df_train[ML_FEAT_COLS].values)
    X_test  = imputer.transform(df_test[ML_FEAT_COLS].values)
    y_train = df_train["next_semester_gpa"].values
    y_test  = df_test["next_semester_gpa"].values
    yc_train = df_train["at_risk_next"].values
    yc_test  = df_test["at_risk_next"].values

    # Grouped fit/cal split inside train
    gss = GroupShuffleSplit(n_splits=1, test_size=CONFIG.cal_frac, random_state=SEED)
    fit_idx, cal_idx = next(gss.split(X_train, y_train, groups=df_train["student_id"].values))
    X_fit, X_cal = X_train[fit_idx], X_train[cal_idx]
    y_fit, y_cal = y_train[fit_idx], y_train[cal_idx]

    # Optuna tuning on cal fold
    print(f"Running Optuna ({CONFIG.optuna_trials_reg} trials)...")
    def xgb_objective(trial):
        params = dict(
            n_estimators     = trial.suggest_int("n_estimators", 200, 700),
            max_depth        = trial.suggest_int("max_depth", 3, 7),
            learning_rate    = trial.suggest_float("learning_rate", 0.01, 0.15, log=True),
            subsample        = trial.suggest_float("subsample", 0.6, 1.0),
            colsample_bytree = trial.suggest_float("colsample_bytree", 0.5, 1.0),
            min_child_weight = trial.suggest_int("min_child_weight", 3, 15),
            reg_alpha        = trial.suggest_float("reg_alpha", 0.0, 1.0),
            reg_lambda       = trial.suggest_float("reg_lambda", 0.5, 3.0),
            random_state=SEED, verbosity=0,
        )
        m = xgb.XGBRegressor(**params).fit(X_fit, y_fit)
        return np.sqrt(mean_squared_error(y_cal, m.predict(X_cal)))

    study = optuna.create_study(direction="minimize", sampler=optuna.samplers.TPESampler(seed=SEED))
    study.optimize(xgb_objective, n_trials=CONFIG.optuna_trials_reg, show_progress_bar=False)
    best_params = study.best_params
    print(f"Best val RMSE: {study.best_value:.4f}  params: {best_params}")

    # Tail-weighted regressor (deploy model)
    w_train = np.where(y_train < 2.0, 4.0, np.where(y_train < 3.0, 2.0, 1.0))
    deploy_reg = xgb.XGBRegressor(**best_params, random_state=SEED, verbosity=0)
    deploy_reg.fit(X_train, y_train, sample_weight=w_train)
    p_test = deploy_reg.predict(X_test)

    test_rmse = float(np.sqrt(mean_squared_error(y_test, p_test)))
    test_mae  = float(mean_absolute_error(y_test, p_test))
    test_r2   = float(r2_score(y_test, p_test))
    within_03 = float(np.mean(np.abs(y_test - p_test) <= 0.3))
    print(f"Regressor — RMSE={test_rmse:.4f}  MAE={test_mae:.4f}  R²={test_r2:.4f}  within±0.3={within_03:.3f}")

    # CQR interval model
    cqr = CQRPredictor(alpha=CONFIG.conformal_alpha, params=best_params)
    cqr.fit(X_fit, y_fit, X_cal, y_cal)
    lo_test, hi_test = cqr.predict(X_test)
    coverage   = float(np.mean((y_test >= lo_test) & (y_test <= hi_test)))
    mean_width = float(np.mean(hi_test - lo_test))
    print(f"CQR — coverage={coverage:.3f} (target {1 - CONFIG.conformal_alpha:.0%})  mean_width={mean_width:.3f}")

    # Forward classifier P(at-risk)
    spw = (yc_train == 0).sum() / max((yc_train == 1).sum(), 1)
    clf = xgb.XGBClassifier(
        n_estimators=300, learning_rate=0.05, max_depth=4,
        subsample=0.8, colsample_bytree=0.8,
        scale_pos_weight=spw, random_state=SEED, verbosity=0, eval_metric="logloss",
    )
    clf.fit(X_train, yc_train)
    prob = clf.predict_proba(X_test)[:, 1]
    pred = (prob >= 0.5).astype(int)
    clf_metrics = {
        "clf_F1":       float(f1_score(yc_test, pred, zero_division=0)),
        "clf_precision":float(precision_score(yc_test, pred, zero_division=0)),
        "clf_recall":   float(recall_score(yc_test, pred, zero_division=0)),
        "clf_ROC_AUC":  float(roc_auc_score(yc_test, prob)),
        "clf_PR_AUC":   float(average_precision_score(yc_test, prob)),
        "clf_Brier":    float(brier_score_loss(yc_test, prob)),
    }
    print(f"Classifier — F1={clf_metrics['clf_F1']:.3f}  ROC_AUC={clf_metrics['clf_ROC_AUC']:.3f}")

    # Save model files
    deploy_reg.save_model(str(model_dir / "xgb_next_gpa.json"))
    clf.save_model(str(model_dir / "xgb_at_risk.json"))
    cqr.lo.save_model(str(model_dir / "cqr_lo.json"))
    cqr.hi.save_model(str(model_dir / "cqr_hi.json"))

    prep = {
        "ml_feat_cols":     ML_FEAT_COLS,
        "hist_feat_cols":   HIST_FEAT_COLS,
        "plan_feat_cols":   PLAN_FEAT_COLS,
        "imputer":          imputer,
        "le_program":       le_program,
        "le_school":        le_school,
        "cqr_Q":            cqr.Q,
        "conformal_alpha":  CONFIG.conformal_alpha,
        "cv_rmse":          test_rmse,
        "at_risk_threshold": CONFIG.at_risk_threshold,
    }
    prep_path = model_dir / "preprocessors.pkl"
    with open(prep_path, "wb") as f:
        pickle.dump(prep, f)

    model_card = {
        "schema_version": "5.0",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "task": "plan-conditioned next-semester GPA prediction (+ CQR interval + P(at-risk))",
        "seed": SEED,
        "n_students_train": int(df_train["student_id"].nunique()),
        "n_students_test":  int(df_test["student_id"].nunique()),
        "features": {"total": len(ML_FEAT_COLS), "plan": len(PLAN_FEAT_COLS), "history": len(HIST_FEAT_COLS)},
        "regressor": {"params": best_params, "test_RMSE": round(test_rmse, 4),
                      "test_R2": round(test_r2, 4), "test_MAE": round(test_mae, 4)},
        "interval":  {"method": "CQR", "target_coverage": 1 - CONFIG.conformal_alpha,
                      "empirical_coverage": round(coverage, 3), "mean_width": round(mean_width, 3)},
        "classifier": {k: round(v, 3) for k, v in clf_metrics.items()},
    }
    card_path = model_dir / "model_card.json"
    with open(card_path, "w") as f:
        json.dump(model_card, f, indent=2)

    # MLflow run (skipped gracefully if tracking is unavailable)
    if _mlflow_ok:
        try:
            run_name = f"student_perf_v5_{os.environ.get('GITHUB_SHA', 'local')[:8]}"
            with mlflow.start_run(run_name=run_name) as run:
                mlflow.log_param("n_students_train",  int(df_train["student_id"].nunique()))
                mlflow.log_param("n_students_test",   int(df_test["student_id"].nunique()))
                mlflow.log_param("n_train_rows",      int(len(df_train)))
                mlflow.log_param("n_test_rows",       int(len(df_test)))
                mlflow.log_param("n_features",        len(ML_FEAT_COLS))
                mlflow.log_param("n_plan_features",   len(PLAN_FEAT_COLS))
                mlflow.log_param("conformal_alpha",   CONFIG.conformal_alpha)
                mlflow.log_param("cohort_split_year", CONFIG.cohort_split_year)
                mlflow.log_param("optuna_trials",     CONFIG.optuna_trials_reg)
                mlflow.log_param("at_risk_threshold", CONFIG.at_risk_threshold)
                for k, v in best_params.items():
                    mlflow.log_param(f"xgb_{k}", v)

                mlflow.log_metric("test_RMSE",      test_rmse)
                mlflow.log_metric("test_MAE",       test_mae)
                mlflow.log_metric("test_R2",        test_r2)
                mlflow.log_metric("within_0_3",     within_03)
                mlflow.log_metric("cqr_coverage",   coverage)
                mlflow.log_metric("cqr_mean_width", mean_width)
                mlflow.log_metric("cqr_Q",          cqr.Q)
                for k, v in clf_metrics.items():
                    mlflow.log_metric(k, v)

                mlflow.log_artifact(str(model_dir / "xgb_next_gpa.json"), artifact_path="model")
                mlflow.log_artifact(str(model_dir / "xgb_at_risk.json"),  artifact_path="model")
                mlflow.log_artifact(str(model_dir / "cqr_lo.json"),       artifact_path="model")
                mlflow.log_artifact(str(model_dir / "cqr_hi.json"),       artifact_path="model")
                mlflow.log_artifact(str(prep_path),                        artifact_path="model")
                mlflow.log_artifact(str(card_path),                        artifact_path="model")
                mlflow.xgboost.log_model(deploy_reg, artifact_path="xgboost_regressor")
                print(f"MLflow run id: {run.info.run_id}")
        except Exception as _e:
            print(f"[mlflow] logging failed ({_e}) — models were still saved locally")
    else:
        print("[mlflow] skipped (tracking unavailable)")

    print(f"Models saved to {model_dir}")
    return model_card


# ─── CLI ─────────────────────────────────────────────────────────────────────

def _find_transcripts() -> Path:
    base = Path(__file__).resolve().parent
    for candidate in [base, *base.parents]:
        p = candidate / "data" / "transcripts.json"
        if p.exists():
            return p
    cwd = Path.cwd()
    for candidate in [cwd, *cwd.parents]:
        p = candidate / "data" / "transcripts.json"
        if p.exists():
            return p
    return Path("data/transcripts.json")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train student performance V5 model")
    parser.add_argument("--data",       default=None, help="Path to transcripts.json")
    parser.add_argument("--out",        default=None, help="Output model directory")
    parser.add_argument("--mlflow-uri", default=None, help="MLflow tracking URI")
    parser.add_argument("--experiment", default="Student_Performance_Service")
    args = parser.parse_args()

    data_path = args.data or str(_find_transcripts())

    if args.out:
        out_dir = Path(args.out)
    else:
        out_dir = Path(__file__).resolve().parent.parent / "models"

    sys.exit(0 if train(
        transcripts_path=data_path,
        model_dir=str(out_dir),
        mlflow_uri=args.mlflow_uri,
        experiment=args.experiment,
    ) else 1)
