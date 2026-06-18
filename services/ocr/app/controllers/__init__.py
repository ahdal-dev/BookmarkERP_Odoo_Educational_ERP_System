import importlib


def __getattr__(name):
    if name == "ocr_controller":
        module = importlib.import_module(f"{__name__}.ocr_controller")
        globals()[name] = module
        return module
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")
