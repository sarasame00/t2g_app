from pathlib import Path

# === Google Drive Setup ===
SERVICE_ACCOUNT_FILE = Path(__file__).parents[1] / "drive_service_account.json"
SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]

# === Google Drive Folder IDs ===
GDRIVE_FOLDER_IDS = {
    "lat": "11iE39rc67cgmxzWcNpTn2TnBWPXYhK6u",
    "ss": "1lfVuc2xSYqTm2Xn4cjzY_wDl-EnN3yZW",
}

# === Local Data Paths ===
LOCAL_DATA_FOLDER = Path(__file__).parents[1] / "data"  # e.g. t2g_app/data/
