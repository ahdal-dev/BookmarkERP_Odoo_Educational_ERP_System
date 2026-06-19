import pickle
import xgboost as xgb
from pathlib import Path

BASE_DIR  = Path(__file__).resolve().parent
MODEL_DIR = BASE_DIR.parent / "models"

_prep    = None   # preprocessors.pkl dict
_reg     = None   # XGBRegressor  (next semester GPA, tail-weighted)
_clf     = None   # XGBClassifier (P(next term GPA < 2.0))
_cqr_lo  = None   # XGBRegressor  (lower quantile bound)
_cqr_hi  = None   # XGBRegressor  (upper quantile bound)


def _load():
    global _prep, _reg, _clf, _cqr_lo, _cqr_hi

    prep_path = MODEL_DIR / "preprocessors.pkl"
    if not prep_path.exists():
        print(f"[model] preprocessors.pkl not found in {MODEL_DIR} — run train.py first")
        return

    with open(prep_path, "rb") as f:
        _prep = pickle.load(f)

    _reg    = xgb.XGBRegressor();  _reg.load_model(str(MODEL_DIR / "xgb_next_gpa.json"))
    _clf    = xgb.XGBClassifier(); _clf.load_model(str(MODEL_DIR / "xgb_at_risk.json"))
    _cqr_lo = xgb.XGBRegressor();  _cqr_lo.load_model(str(MODEL_DIR / "cqr_lo.json"))
    _cqr_hi = xgb.XGBRegressor();  _cqr_hi.load_model(str(MODEL_DIR / "cqr_hi.json"))
    print("[model] All notebook models loaded (xgb_next_gpa, xgb_at_risk, cqr_lo, cqr_hi)")


_load()


def get_models():
    return _prep, _reg, _clf, _cqr_lo, _cqr_hi


def is_loaded() -> bool:
    return _prep is not None
