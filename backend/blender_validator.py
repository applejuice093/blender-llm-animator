import os
import subprocess
import tempfile
from config import BLEND_FILE, BLENDER_EXECUTABLE, BLENDER_VALIDATION_TIMEOUT

def validate_script_headlessly(script_code: str) -> tuple[bool, str]:
    """
    Runs a blender script in a headless blender instance.
    Returns (True, "") if successful.
    Returns (False, error_traceback) if Blender throws an error.
    """
    
    # We append a sys.exit(0) at the end of the script to ensure Blender quits cleanly 
    # if it reaches the end without exceptions.
    safe_script = script_code + "\n\nimport sys\nsys.exit(0)\n"
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(safe_script)
        temp_path = f.name
        
    cmd = [BLENDER_EXECUTABLE, "-b"]
    
    if BLEND_FILE and os.path.exists(BLEND_FILE):
        cmd.append(BLEND_FILE)
        
    cmd.extend(["-P", temp_path])
    
    try:
        # Run blender
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=BLENDER_VALIDATION_TIMEOUT)
        
        # Cleanup temp file
        if os.path.exists(temp_path):
            os.remove(temp_path)
            
        if result.returncode == 0:
            return True, ""
            
        # If it failed, extract the traceback from stderr or stdout
        error_output = result.stderr if result.stderr else result.stdout
        return False, f"Blender exited with code {result.returncode}.\n{error_output}"
        
    except subprocess.TimeoutExpired:
        if os.path.exists(temp_path):
            os.remove(temp_path)
        return False, f"Blender validation timed out after {BLENDER_VALIDATION_TIMEOUT} seconds."
    except FileNotFoundError:
        if os.path.exists(temp_path):
            os.remove(temp_path)
        return False, (
            f"Blender executable not found at {BLENDER_EXECUTABLE!r}. "
            "Install Blender or set BLENDER_EXECUTABLE."
        )
    except Exception as e:
        if os.path.exists(temp_path):
            os.remove(temp_path)
        return False, f"Failed to run Blender subprocess: {str(e)}"
