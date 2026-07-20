import os

BLENDER_EXECUTABLE = os.environ.get("BLENDER_EXECUTABLE", r"D:\aa\Blender\4.5 lts\blender-launcher.exe")
BLEND_FILE = os.environ.get("BLEND_FILE", None)

TOOLS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tools")
DEFAULT_RHUBARB = os.path.join(TOOLS_DIR, "rhubarb_extracted", "Rhubarb-Lip-Sync-1.13.0-Windows", "rhubarb.exe")
RHUBARB_EXECUTABLE = os.environ.get("RHUBARB_EXECUTABLE", DEFAULT_RHUBARB)
