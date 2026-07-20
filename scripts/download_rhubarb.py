import urllib.request
import zipfile
import os
import shutil

RHUBARB_URL = "https://github.com/DanielSWolf/rhubarb-lip-sync/releases/download/v1.13.0/Rhubarb-Lip-Sync-1.13.0-Windows.zip"
TOOLS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "backend", "tools")
ZIP_PATH = os.path.join(TOOLS_DIR, "rhubarb.zip")
EXTRACT_DIR = os.path.join(TOOLS_DIR, "rhubarb_extracted")

def download_and_extract():
    if not os.path.exists(TOOLS_DIR):
        os.makedirs(TOOLS_DIR)
        
    print("Downloading Rhubarb Lip Sync...")
    urllib.request.urlretrieve(RHUBARB_URL, ZIP_PATH)
    
    print("Extracting...")
    with zipfile.ZipFile(ZIP_PATH, 'r') as zip_ref:
        zip_ref.extractall(EXTRACT_DIR)
        
    # The zip contains a folder inside it, usually 'Rhubarb-Lip-Sync-1.13.0-Windows'
    # Let's find rhubarb.exe
    rhubarb_exe = None
    for root, dirs, files in os.walk(EXTRACT_DIR):
        if "rhubarb.exe" in files:
            rhubarb_exe = os.path.join(root, "rhubarb.exe")
            break
            
    if rhubarb_exe:
        print(f"Rhubarb downloaded and extracted successfully to:\n{rhubarb_exe}")
        # Cleanup zip
        os.remove(ZIP_PATH)
    else:
        print("Failed to find rhubarb.exe in the extracted files.")

if __name__ == "__main__":
    download_and_extract()
