"""Headless Blender check used by the dataset factory's validate/repair loop."""

import os
import subprocess
import tempfile

from config import BLEND_FILE, BLENDER_EXECUTABLE, BLENDER_VALIDATION_TIMEOUT

# Blender can print thousands of lines of add-on noise; the repair prompt only
# needs the tail, where the Python traceback is.
MAX_ERROR_CHARS = 4000


def _tail(text: str, limit: int = MAX_ERROR_CHARS) -> str:
    text = text or ""
    if len(text) <= limit:
        return text
    return "...(truncated)...\n" + text[-limit:]


def validate_script_headlessly(script_code: str) -> tuple[bool, str]:
    """Run ``script_code`` in a background Blender instance.

    Returns ``(True, "")`` if the script finished cleanly, otherwise
    ``(False, message)`` where ``message`` ends with Blender's traceback.
    """
    # Appending sys.exit(0) makes Blender quit cleanly when the script reaches
    # the end without raising; an exception leaves a non-zero exit code.
    safe_script = script_code + "\n\nimport sys\nsys.exit(0)\n"

    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False, encoding="utf-8") as f:
        f.write(safe_script)
        temp_path = f.name

    cmd = [BLENDER_EXECUTABLE, "-b"]
    if BLEND_FILE and os.path.exists(BLEND_FILE):
        cmd.append(BLEND_FILE)
    cmd.extend(["-P", temp_path])

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=BLENDER_VALIDATION_TIMEOUT)
    except subprocess.TimeoutExpired:
        return False, f"Blender validation timed out after {BLENDER_VALIDATION_TIMEOUT} seconds."
    except FileNotFoundError:
        return False, (
            f"Blender executable not found at {BLENDER_EXECUTABLE!r}. "
            "Install Blender or set BLENDER_EXECUTABLE."
        )
    except OSError as e:
        return False, f"Failed to run Blender subprocess: {e}"
    finally:
        try:
            os.remove(temp_path)
        except OSError:
            pass

    if result.returncode == 0:
        return True, ""
    error_output = result.stderr or result.stdout
    return False, f"Blender exited with code {result.returncode}.\n{_tail(error_output)}"
