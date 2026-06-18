import joblib
import torch
import torch.nn as nn
from pathlib import Path

BASE_DIR  = Path(__file__).resolve().parent
MODEL_DIR = BASE_DIR.parent / "models"


# ─── GRU architecture (must match the saved state_dict) ──────────────────────
# Inferred from state_dict shapes:
#   gru.weight_ih_l0: [144, 2]  → input_size=2, hidden=48
#   head.0.weight:    [24, 48]
#   head.3.weight:    [1, 24]   → indices 1,2 are activation/dropout (no weights)

class _GRUNet(nn.Module):
    def __init__(self, input_size: int = 2, hidden_size: int = 48):
        super().__init__()
        self.gru  = nn.GRU(input_size, hidden_size, batch_first=True)
        self.head = nn.Sequential(
            nn.Linear(hidden_size, 24),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(24, 1),
        )

    def forward(self, x):
        _, h = self.gru(x)          # h: [1, batch, hidden]
        return self.head(h.squeeze(0)).squeeze(-1)  # [batch]


# ─── Module-level singletons ─────────────────────────────────────────────────
_gru_bundle  = None   # dict: state_dict, seq_mu, seq_sd, maxlen, seq_feats
_gru_model   = None   # _GRUNet instance (eval mode)
_risk_bundle = None   # dict: model, label_encoder, features, class_weights


def _load():
    global _gru_bundle, _gru_model, _risk_bundle

    gru_path  = MODEL_DIR / "next_gpa_gru.pt"
    risk_path = MODEL_DIR / "risk_xgboost.joblib"

    if not gru_path.exists() or not risk_path.exists():
        print(f"[model] model files missing in {MODEL_DIR} — run train.py first")
        return

    _gru_bundle = torch.load(str(gru_path), map_location="cpu", weights_only=False)
    net = _GRUNet()
    net.load_state_dict(_gru_bundle["state_dict"])
    net.eval()
    _gru_model = net

    _risk_bundle = joblib.load(str(risk_path))
    print("[model] next_gpa_gru.pt + risk_xgboost.joblib loaded")


_load()


def get_gru():
    """Returns (model, seq_mu, seq_sd, maxlen, seq_feats)."""
    return (
        _gru_model,
        _gru_bundle["seq_mu"],
        _gru_bundle["seq_sd"],
        _gru_bundle["maxlen"],
        _gru_bundle["seq_feats"],
    )


def get_risk():
    """Returns (xgb_classifier, label_encoder, feature_names, class_weights)."""
    return (
        _risk_bundle["model"],
        _risk_bundle["label_encoder"],
        _risk_bundle["features"],
        _risk_bundle["class_weights"],
    )


def is_loaded() -> bool:
    return _gru_model is not None and _risk_bundle is not None
