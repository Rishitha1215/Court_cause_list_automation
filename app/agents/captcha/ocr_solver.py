"""Importable wrapper for the OCR solver implementation."""
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path


_implementation_path = Path(__file__).with_name("ocr_solver..py")
_spec = spec_from_file_location("app.agents.captcha._ocr_solver_impl", _implementation_path)
if _spec is None or _spec.loader is None:
    raise ImportError(f"Could not load CAPTCHA solver from {_implementation_path}")

_module = module_from_spec(_spec)
_spec.loader.exec_module(_module)
OCRCaptchaSolver = _module.OCRCaptchaSolver

# Short alias
OCRSolver = OCRCaptchaSolver

__all__ = ["OCRCaptchaSolver", "OCRSolver"]
