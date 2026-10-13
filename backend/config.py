"""Central, environment-driven configuration for the backend.

Every setting can be overridden with an environment variable (or a ``.env``
file loaded by your shell / process manager). Defaults are chosen so the API
starts on a fresh Linux, macOS or Windows machine without any edits.

See ``backend/.env.example`` for a documented list of variables.
"""

import os
import platform
import shutil

BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))


def _env_path(name: str, default: str) -> str:
    """Return an absolute path from ``$name`` or ``default`` (relative to backend/)."""
    value = os.environ.get(name, default)
    if not os.path.isabs(value):
        value = os.path.join(BACKEND_DIR, value)
    return value


def _env_int(name: str, default: int) -> int:
    raw = os.environ.get(name)
    if raw is None or raw.strip() == "":
        return default
    try:
        return int(raw)
    except ValueError as exc:
        raise ValueError(f"Environment variable {name} must be an integer, got {raw!r}") from exc


def _env_list(name: str, default: list[str]) -> list[str]:
    raw = os.environ.get(name)
    if raw is None or raw.strip() == "":
        return list(default)
    return [item.strip() for item in raw.split(",") if item.strip()]


# --- Blender -----------------------------------------------------------------
# Path to the Blender binary used for headless validation. Defaults to whatever
# `blender` is on PATH; set BLENDER_EXECUTABLE explicitly on Windows installs.
BLENDER_EXECUTABLE = os.environ.get("BLENDER_EXECUTABLE") or shutil.which("blender") or "blender"
BLEND_FILE = os.environ.get("BLEND_FILE") or None
BLENDER_VALIDATION_TIMEOUT = _env_int("BLENDER_VALIDATION_TIMEOUT", 30)

# TCP endpoint of the blender-mcp add-on used for live script execution.
BLENDER_HOST = os.environ.get("BLENDER_HOST", "127.0.0.1")
BLENDER_PORT = _env_int("BLENDER_PORT", 8123)

# --- Rhubarb lip sync --------------------------------------------------------
TOOLS_DIR = _env_path("TOOLS_DIR", "tools")
if platform.system() == "Windows":
    # Location used by scripts/download_rhubarb.py
    DEFAULT_RHUBARB = os.path.join(
        TOOLS_DIR, "rhubarb_extracted", "Rhubarb-Lip-Sync-1.13.0-Windows", "rhubarb.exe"
    )
else:
    DEFAULT_RHUBARB = shutil.which("rhubarb") or ""
RHUBARB_EXECUTABLE = os.environ.get("RHUBARB_EXECUTABLE", DEFAULT_RHUBARB)

# --- LLM planner (Ollama) ----------------------------------------------------
OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://127.0.0.1:11434/api/generate")
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "qwen3:4b")
OLLAMA_TIMEOUT = _env_int("OLLAMA_TIMEOUT", 120)

# --- Storage -----------------------------------------------------------------
CHROMA_DB_DIR = _env_path("CHROMA_DB_DIR", "chroma_db")
CHROMA_COLLECTION = os.environ.get("CHROMA_COLLECTION", "knowledge_store")
DATASET_DIR = _env_path("DATASET_DIR", "datasets")
LORA_OUTPUT_DIR = _env_path("LORA_OUTPUT_DIR", "lora_output")

# --- API ---------------------------------------------------------------------
# Comma-separated list of allowed browser origins for CORS.
CORS_ORIGINS = _env_list(
    "CORS_ORIGINS",
    ["http://localhost:5173", "http://127.0.0.1:5173"],
)
LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO").upper()
