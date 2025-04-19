from pathlib import Path

# === Google Drive Setup ===
SERVICE_ACCOUNT_FILE = Path(__file__).parents[1] / "drive_service_account.json"
SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]

# === Google Drive Folder IDs ===
GDRIVE_FOLDER_IDS = {
    "lat": "1-UDQwKXUsjsOpKgKBeGaIO1Acv7T8wm6",
    "ss": "1VPQ4HARo7HJVXoXWRhVYYn79Svs3IZWq",
}

# === Local Data Paths ===
LOCAL_DATA_FOLDER = Path(__file__).parents[1] / "data"  # e.g. t2g_app/data/
