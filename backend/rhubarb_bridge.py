import os
import subprocess
import json
from config import RHUBARB_EXECUTABLE

def extract_visemes(audio_file_path: str, dialog_text: str = None) -> list:
    """
    Runs Rhubarb Lip Sync on the given audio file and returns a list of viseme events.
    Returns format: [{"start": 0.0, "end": 0.2, "viseme": "A"}, ...]
    """
    if not RHUBARB_EXECUTABLE or not os.path.exists(RHUBARB_EXECUTABLE):
        print("Rhubarb executable not found.")
        return []
        
    cmd = [RHUBARB_EXECUTABLE, "-f", "json", audio_file_path]
    if dialog_text:
        # Create a temp file for the dialog text if provided
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(dialog_text)
            temp_txt = f.name
        cmd.extend(["-d", temp_txt])
        
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        # Parse the JSON output from stdout
        rhubarb_output = json.loads(result.stdout)
        
        visemes = []
        mouth_cues = rhubarb_output.get("mouthCues", [])
        for i, cue in enumerate(mouth_cues):
            start = cue["start"]
            end = cue["end"]
            viseme = cue["value"]
            visemes.append({"start": start, "end": end, "viseme": viseme})
            
        return visemes
    except subprocess.CalledProcessError as e:
        print(f"Rhubarb failed with error: {e.stderr}")
        return []
    finally:
        if dialog_text and 'temp_txt' in locals() and os.path.exists(temp_txt):
            os.remove(temp_txt)
