from pathlib import Path
import sys, os

def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

# === Google Drive Setup ===
SERVICE_ACCOUNT_FILE = Path(resource_path("drive_service_account.json"))
SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]

# === Google Drive Folder IDs ===
GDRIVE_FOLDER_IDS = {
    "lat": "1-UDQwKXUsjsOpKgKBeGaIO1Acv7T8wm6",
    "ss": "1VPQ4HARo7HJVXoXWRhVYYn79Svs3IZWq",
}

# === Local Data Paths (writeable, not bundled!)
LOCAL_DATA_FOLDER = Path("data")  # Do NOT use resource_path here
