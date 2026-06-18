import logging
import os
try:
    from ultralytics import YOLO
except ImportError:
    YOLO = None
try:
    import torch
except ImportError:
    torch = None

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

if torch is not None:
    # PyTorch 2.6+ compatibility: Patch torch.load to disable weights_only for trusted sources
    _original_torch_load = torch.load

    def patched_torch_load(f, *args, **kwargs):
        """Patched torch.load that disables weights_only for known safe sources."""
        # Set weights_only=False for .pt files (model files)
        if isinstance(f, str) and f.endswith('.pt'):
            kwargs['weights_only'] = False
        elif hasattr(f, 'name') and f.name.endswith('.pt'):
            kwargs['weights_only'] = False
        return _original_torch_load(f, *args, **kwargs)

    # Apply the patch
    torch.load = patched_torch_load
    logger.info("Applied PyTorch 2.6+ compatibility patch for .pt files")
else:
    logger.warning("PyTorch is not installed; OCR detection models disabled")

# Load models with error handling
try:
    if YOLO is None:
        raise ImportError("ultralytics is not installed")
    model_id_card_path = os.path.join(BASE_DIR, 'models', 'detect_id_card.pt')
    if not os.path.exists(model_id_card_path):
        raise FileNotFoundError(f"Model file not found: {model_id_card_path}")
    model_id_card = YOLO(model_id_card_path)
    logger.info("✅ ID card detection model loaded successfully")
except Exception as e:
    logger.error(f"Failed to load ID card model: {str(e)}")
    model_id_card = None

try:
    if YOLO is None:
        raise ImportError("ultralytics is not installed")
    model_job_path = os.path.join(BASE_DIR, 'models', 'detect_objects.pt')
    if not os.path.exists(model_job_path):
        raise FileNotFoundError(f"Model file not found: {model_job_path}")
    model_job = YOLO(model_job_path)
    logger.info("✅ Object detection model loaded successfully")
except Exception as e:
    logger.error(f"Failed to load object detection model: {str(e)}")
    model_job = None