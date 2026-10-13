"""Wrapper around the Rhubarb Lip Sync CLI for viseme extraction."""

import json
import logging
import os
import subprocess
import tempfile
from typing import Optional

from config import RHUBARB_EXECUTABLE

logger = logging.getLogger(__name__)


def extract_visemes(audio_file_path: str, dialog_text: Optional[str] = None) -> list:
    """
    Runs Rhubarb Lip Sync on the given audio file and returns a list of viseme events.
    Returns format: [{"start": 0.0, "end": 0.2, "viseme": "A"}, ...]

    Returns an empty list (and logs why) if Rhubarb or the audio file is missing,
    the CLI fails, or its output cannot be parsed.
    """
    if not RHUBARB_EXECUTABLE or not os.path.exists(RHUBARB_EXECUTABLE):
        logger.warning("Rhubarb executable not found (RHUBARB_EXECUTABLE=%r).", RHUBARB_EXECUTABLE)
        return []
    if not audio_file_path or not os.path.exists(audio_file_path):
        logger.warning("Audio file not found: %r", audio_file_path)
        return []

    cmd = [RHUBARB_EXECUTABLE, "-f", "json", audio_file_path]
    temp_txt = None
    try:
        if dialog_text:
            # Rhubarb takes the transcript as a file path.
            with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False, encoding="utf-8") as f:
                f.write(dialog_text)
                temp_txt = f.name
            cmd.extend(["-d", temp_txt])

        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        rhubarb_output = json.loads(result.stdout)

        return [
            {"start": cue["start"], "end": cue["end"], "viseme": cue["value"]}
            for cue in rhubarb_output.get("mouthCues", [])
        ]
    except subprocess.CalledProcessError as e:
        logger.error("Rhubarb failed with error: %s", e.stderr)
        return []
    except (json.JSONDecodeError, KeyError) as e:
        logger.error("Could not parse Rhubarb output: %s", e)
        return []
    finally:
        if temp_txt and os.path.exists(temp_txt):
            os.remove(temp_txt)
