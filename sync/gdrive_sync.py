import os
from pathlib import Path
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
import io
from sync.config import SERVICE_ACCOUNT_FILE, LOCAL_DATA_FOLDER, GDRIVE_FOLDER_IDS

SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]

def get_drive_service():
    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES
    )
    return build("drive", "v3", credentials=creds)

def list_files_in_folder(service, folder_id):
    query = f"'{folder_id}' in parents and trashed = false"
    files = []
    page_token = None

    while True:
        response = service.files().list(
            q=query,
            spaces='drive',
            fields='nextPageToken, files(id, name)',
            pageToken=page_token
        ).execute()
        files.extend(response.get('files', []))
        page_token = response.get('nextPageToken', None)
        if page_token is None:
            break

    return files

def download_metadata_csv(model):
    assert model in ["lat", "ss"], "Model must be 'lat' or 'ss'"

    service = get_drive_service()
    folder_id = GDRIVE_FOLDER_IDS[model]
    metadata_filename = f"simulated_values_{model}.csv"
    local_path = LOCAL_DATA_FOLDER / f"{model}_data" / metadata_filename

    all_drive_files = list_files_in_folder(service, folder_id)
    file_lookup = {f["name"]: f["id"] for f in all_drive_files}

    if metadata_filename not in file_lookup:
        raise FileNotFoundError(f"{metadata_filename} not found in Google Drive.")

    print(f"📥 Downloading metadata: {metadata_filename}")
    request = service.files().get_media(fileId=file_lookup[metadata_filename])
    local_path.parent.mkdir(parents=True, exist_ok=True)

    with open(local_path, "wb") as f:
        downloader = MediaIoBaseDownload(f, request)
        done = False
        while not done:
            status, done = downloader.next_chunk()
            print(f"   Download {int(status.progress() * 100)}%")

    return local_path

def download_files_from_drive(filenames, model):
    service = get_drive_service()
    folder_id = GDRIVE_FOLDER_IDS[model]

    # List all files in the GDrive model folder
    all_drive_files = list_files_in_folder(service, folder_id)

    # Create a lookup dictionary for fast access
    drive_files_dict = {f["name"]: f["id"] for f in all_drive_files}

    local_dir = LOCAL_DATA_FOLDER / f"{model}_data"
    local_dir.mkdir(parents=True, exist_ok=True)

    downloaded_count = 0

    for filename in filenames:
        if filename not in drive_files_dict:
            print(f"❌ File not found in Drive: {filename}")
            continue

        file_id = drive_files_dict[filename]
        local_path = local_dir / filename

        if local_path.exists():
            print(f"✅ Already downloaded: {filename}")
            continue

        print(f"⬇️ Downloading {filename}")
        request = service.files().get_media(fileId=file_id)
        with open(local_path, "wb") as f:
            downloader = MediaIoBaseDownload(f, request)
            done = False
            while not done:
                status, done = downloader.next_chunk()
        downloaded_count += 1

    print(f"✅ Download complete. {downloaded_count} new file(s) downloaded.")
