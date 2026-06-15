"""
Train the two Student-Performance models and save them into ./models.

  - next_gpa_gru.pt      GRU regressor for next-semester GPA
  - risk_xgboost.joblib  XGBoost risk classifier (Low / Medium / High)

Usage:
    python train.py                       # uses the default data path
    python train.py path/to/transcripts.json
"""
import sys, json, math, warnings
from pathlib import Path
from collections import defaultdict

import numpy as np
import pandas as pd
import torch
import torch.nn as nn
import joblib
import xgboost as xgb
from sklearn.preprocessing import LabelEncoder

warnings.filterwarnings("ignore")
SEED = 42
np.random.seed(SEED); torch.manual_seed(SEED)

HERE = Path(__file__).resolve().parent
MODELS = HERE / "models"; MODELS.mkdir(exist_ok=True)

DEFAULT_DATA = HERE / ".." / ".." / "data" / "Data Generation" / "generated_data" / "transcripts.json"

GRADE_POINTS = {"A": 4.0, "A-": 3.7, "B+": 3.3, "B": 3.0, "B-": 2.7, "C+": 2.3,
                "C": 2.0, "C-": 1.7, "D": 1.0, "F": 0.0}
FEATURES = ["n_semesters", "last_gpa", "first_gpa", "min_term_gpa", "n_poor_terms",
            "gpa_trend_slope", "gpa_volatility", "gpa_drop", "fail_rate",
            "credit_completion_rate", "consecutive_poor_semesters", "dom_MATH", "dom_min"]
SEQ_FEATS = ["term_gpa", "running_cum"]
CLASS_W = {"High": 6.0, "Medium": 1.5, "Low": 1.0}


def grade_to_points(g): return GRADE_POINTS.get(g.strip("[]"))
def domain_of(cid): return cid.split()[0] if " " in cid else cid[:4]
def slope(s): return 0.0 if len(s) < 2 else float(np.polyfit(np.arange(len(s)), s, 1)[0])


def gpa_terms(t):
    out = []
    for s in t["semesters"]:
        ts = s.get("term_statistics", {})
        if ts.get("gpa_credits", 0) <= 0:
            continue
        out.append(float(ts.get("term_gpa") or 0.0))
    return out


def student_features(t):
    gpas = gpa_terms(t)
    dom = defaultdict(list)
    total_fail = total_courses = att = earned = 0
    for s in t["semesters"]:
        for c in s["courses"]:
            gp = grade_to_points(c["grade"])
            if gp is not None:
                dom[domain_of(c["course_id"])].append(gp)
            if c["grade"] in ("F", "W"):
                total_fail += 1
            total_courses += 1
        att += s.get("term_statistics", {}).get("attempted_credits", 0)
        earned += s.get("term_statistics", {}).get("earned_credits", 0)
    consec = mx = 0
    for g in gpas:
        consec = consec + 1 if g < 2.0 else 0
        mx = max(mx, consec)
    return dict(
        n_semesters=len(gpas),
        last_gpa=gpas[-1] if gpas else 0.0,
        first_gpa=gpas[0] if gpas else 0.0,
        min_term_gpa=min(gpas) if gpas else 0.0,
        n_poor_terms=sum(1 for g in gpas if g < 2.0),
        gpa_trend_slope=slope(gpas),
        gpa_volatility=float(np.std(gpas)) if gpas else 0.0,
        gpa_drop=(gpas[0] - gpas[-1]) if len(gpas) > 1 else 0.0,
        fail_rate=total_fail / max(total_courses, 1),
        credit_completion_rate=earned / max(att, 1),
        consecutive_poor_semesters=mx,
        dom_MATH=float(np.mean(dom.get("MATH", [np.nan]))),
        dom_min=min((float(np.mean(v)) for v in dom.values()), default=np.nan))


def risk_label(t):
    cg = t.get("cumulative_gpa", 0.0)
    if t["enrollment_status"] == "Academic Probation" or cg < 2.0:
        return "High"
    return "Medium" if cg < 2.7 else "Low"


class GRURegressor(nn.Module):
    def __init__(self, n_in=2, hid=48):
        super().__init__()
        self.gru = nn.GRU(n_in, hid, batch_first=True)
        self.head = nn.Sequential(nn.Linear(hid, 24), nn.ReLU(),
                                  nn.Dropout(0.1), nn.Linear(24, 1))

    def forward(self, x):
        _, h = self.gru(x)
        return self.head(h[-1])


def main(data_path):
    data_path = Path(data_path)
    assert data_path.exists(), f"transcripts.json not found at {data_path}"
    transcripts = json.loads(data_path.read_text(encoding="utf-8"))
    print(f"Loaded {len(transcripts)} transcripts")

    # ---------- XGBoost risk classifier ----------
    X = pd.DataFrame([student_features(t) for t in transcripts])[FEATURES].fillna(0.0)
    y = pd.Series([risk_label(t) for t in transcripts])
    le = LabelEncoder().fit(["High", "Low", "Medium"])
    y_enc = le.transform(y)
    sw = np.array([CLASS_W[lab] for lab in y])
    clf = xgb.XGBClassifier(n_estimators=300, max_depth=3, learning_rate=0.07,
                            subsample=0.9, colsample_bytree=0.9,
                            eval_metric="mlogloss", random_state=SEED)
    clf.fit(X, y_enc, sample_weight=sw)
    joblib.dump({"model": clf, "label_encoder": le, "features": FEATURES,
                 "class_weights": CLASS_W}, MODELS / "risk_xgboost.joblib")
    print("Saved risk_xgboost.joblib")

    # ---------- GRU next-semester GPA ----------
    # Honest evaluation: split by STUDENT (no shared windows across train/val/test),
    # fit the scaler on train windows only, early-stop on a validation set.
    seqs, targets, sids = [], [], []
    for si, t in enumerate(transcripts):
        g = gpa_terms(t)
        if len(g) < 2:
            continue
        run = np.cumsum(g) / np.arange(1, len(g) + 1)
        arr = np.stack([g, run], axis=1)
        for k in range(1, len(g)):
            seqs.append(arr[:k]); targets.append(g[k]); sids.append(si)
    targets = np.array(targets, dtype=np.float32)
    sids = np.array(sids)
    maxlen = max(len(s) for s in seqs)

    # group split: 70% / 15% / 15% of STUDENTS
    students = np.arange(len(transcripts)); np.random.RandomState(SEED).shuffle(students)
    n = len(students)
    s_tr = set(students[:int(.70 * n)])
    s_va = set(students[int(.70 * n):int(.85 * n)])
    s_te = set(students[int(.85 * n):])
    i_tr = np.array([i for i in range(len(sids)) if sids[i] in s_tr])
    i_va = np.array([i for i in range(len(sids)) if sids[i] in s_va])
    i_te = np.array([i for i in range(len(sids)) if sids[i] in s_te])

    # scaler fit on TRAIN windows only
    train_stack = np.vstack([seqs[i] for i in i_tr])
    mu, sd = train_stack.mean(0), train_stack.std(0) + 1e-8

    def pad(s):
        s = (s - mu) / sd
        p = np.zeros((maxlen, 2), dtype=np.float32); p[-len(s):] = s
        return p

    Xseq = np.array([pad(s) for s in seqs])
    tt = lambda a: torch.tensor(a, dtype=torch.float32)
    Xtr, ytr = tt(Xseq[i_tr]), tt(targets[i_tr]).unsqueeze(1)
    Xva, yva = tt(Xseq[i_va]), tt(targets[i_va]).unsqueeze(1)
    Xte, yte = tt(Xseq[i_te]), tt(targets[i_te]).unsqueeze(1)

    torch.manual_seed(SEED)
    net = GRURegressor(2)
    opt = torch.optim.Adam(net.parameters(), lr=5e-3, weight_decay=1e-4)
    lossf = nn.SmoothL1Loss()
    best_val, best_state = 9.9, None
    for _ in range(250):
        net.train(); perm = torch.randperm(Xtr.size(0))
        for i in range(0, Xtr.size(0), 64):
            b = perm[i:i + 64]
            opt.zero_grad(); lossf(net(Xtr[b]), ytr[b]).backward(); opt.step()
        net.eval()
        with torch.no_grad():                         # early stop on VALIDATION
            v = float(torch.sqrt(torch.mean((net(Xva) - yva) ** 2)))
        if v < best_val:
            best_val, best_state = v, {k: vv.clone() for k, vv in net.state_dict().items()}
    net.load_state_dict(best_state)

    net.eval()
    with torch.no_grad():
        test_rmse = float(torch.sqrt(torch.mean((net(Xte) - yte) ** 2)))
        base = Xseq[i_te][:, -1, 0] * sd[0] + mu[0]   # naive: next = last term GPA
        base_rmse = float(np.sqrt(np.mean((base - targets[i_te]) ** 2)))

    torch.save({"state_dict": net.state_dict(), "seq_mu": mu, "seq_sd": sd,
                "maxlen": maxlen, "seq_feats": SEQ_FEATS}, MODELS / "next_gpa_gru.pt")
    print(f"Saved next_gpa_gru.pt | students train/val/test = "
          f"{len(s_tr)}/{len(s_va)}/{len(s_te)}")
    print(f"  honest test RMSE = {test_rmse:.3f} (val {best_val:.3f}) | "
          f"naive baseline = {base_rmse:.3f}")
    print("Done. Artifacts in", MODELS)


if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_DATA
    main(path)
