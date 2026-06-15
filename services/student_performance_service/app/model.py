# -*- coding: utf-8 -*-
"""Loads the trained artifacts (XGBoost risk classifier + GRU GPA regressor)."""
from pathlib import Path

import joblib
import torch
import torch.nn as nn

MODELS = Path(__file__).resolve().parent.parent / "models"


class GRURegressor(nn.Module):
    """Must match the architecture used in train.py."""
    def __init__(self, n_in=2, hid=48):
        super().__init__()
        self.gru = nn.GRU(n_in, hid, batch_first=True)
        self.head = nn.Sequential(nn.Linear(hid, 24), nn.ReLU(),
                                  nn.Dropout(0.1), nn.Linear(24, 1))

    def forward(self, x):
        _, h = self.gru(x)
        return self.head(h[-1])


def _load():
    risk_path = MODELS / "risk_xgboost.joblib"
    gru_path = MODELS / "next_gpa_gru.pt"
    if not risk_path.exists() or not gru_path.exists():
        raise FileNotFoundError(
            f"Model artifacts missing in {MODELS}. Run `python train.py` first.")

    risk = joblib.load(risk_path)

    ckpt = torch.load(gru_path, map_location="cpu", weights_only=False)
    gru = GRURegressor(len(ckpt["seq_feats"]))
    gru.load_state_dict(ckpt["state_dict"])
    gru.eval()
    return risk, gru, ckpt


# Loaded once at import time
RISK_BUNDLE, GRU_MODEL, GRU_META = _load()
