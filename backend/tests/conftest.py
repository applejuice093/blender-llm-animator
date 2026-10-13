"""Shared pytest setup: make backend/ importable and isolate side effects."""

import os
import sys
import tempfile

BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

# config.py reads these at import time, so set them before any backend import.
_TMP = tempfile.mkdtemp(prefix="animator-tests-")
os.environ.setdefault("DATASET_DIR", os.path.join(_TMP, "datasets"))
os.environ.setdefault("LORA_OUTPUT_DIR", os.path.join(_TMP, "lora_output"))
os.environ.setdefault("CHROMA_DB_DIR", os.path.join(_TMP, "chroma_db"))
os.environ["RHUBARB_EXECUTABLE"] = ""  # deterministic: never shell out to Rhubarb
os.environ.setdefault("OLLAMA_URL", "http://127.0.0.1:9/api/generate")  # unroutable -> mock fallback
os.environ.setdefault("OLLAMA_TIMEOUT", "1")

import pytest  # noqa: E402


@pytest.fixture
def sample_plan() -> dict:
    return {
        "character": "Aiko",
        "duration_seconds": 5.2,
        "emotion": {"primary": "nervous", "intensity": 0.6},
        "eye_behavior": {"target": "camera", "blink_rate": "increased", "eye_darts": True},
        "lip_sync": {"enabled": True, "audio_file": "line_04.wav", "transcript": "Hello everyone..."},
        "gestures": [
            {"start": 4.0, "end": 4.6, "type": "adjust_collar", "intensity": 1.0},
            {"start": 2.3, "end": 3.1, "type": "raise_right_hand", "intensity": 0.4},
        ],
        "camera": {"shot": "medium_close_up", "movement": "static"},
    }
