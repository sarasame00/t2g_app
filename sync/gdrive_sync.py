import threading
import os
from pathlib import Path

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

from sync.config import SERVICE_ACCOUNT_FILE, LOCAL_DATA_FOLDER, GDRIVE_FOLDER_IDS

# === Google Drive API Config ===
SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]


def get_drive_service():
    """Authenticate and return a Google Drive service object.

    Returns
    -------
    googleapiclient.discovery.Resource
        Authenticated Google Drive API service.

    Raises
    ------
    ConnectionError
        If authentication fails.
    """
    try:
        creds = service_account.Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE, scopes=SCOPES
        )
        return build("drive", "v3", credentials=creds)
    except Exception as e:
        print(f"❌ Failed to authenticate Google Drive service: {e}")
        raise ConnectionError("Google Drive authentication failed.")


def list_files_in_folder(service, folder_id):
    """List all files in a given Google Drive folder.

    Parameters
    ----------
    service : googleapiclient.discovery.Resource
        Authenticated Google Drive API service.
    folder_id : str
        ID of the Google Drive folder.

    Returns
    -------
    list of dict
        List of file metadata dictionaries (id, name).

    Raises
    ------
    ConnectionError
        If the file listing fails.
    """
    query = f"'{folder_id}' in parents and trashed = false"
    files = []
    page_token = None

    try:
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
    except Exception as e:
        print(f"❌ Google Drive error while listing folder: {e}")
        raise ConnectionError("Google Drive service is currently unavailable.")

    return files


def download_metadata_csv(model):
    """Download the metadata CSV for a model ('lat' or 'ss') from Drive.

    Parameters
    ----------
    model : str
        Either 'lat' or 'ss'.

    Returns
    -------
    Path or None
        Local path to downloaded file, or None if download failed.

    Raises
    ------
    FileNotFoundError
        If the CSV file is not found on Drive.
    IOError
        If the file cannot be saved locally.
    """
    assert model in ["lat", "ss"], "Model must be 'lat' or 'ss'"

    service = get_drive_service()
    folder_id = GDRIVE_FOLDER_IDS[model]
    metadata_filename = f"simulated_values_{model}.csv"
    local_path = LOCAL_DATA_FOLDER / f"{model}_data" / metadata_filename

    try:
        all_drive_files = list_files_in_folder(service, folder_id)
    except ConnectionError as e:
        print(e)
        return

    file_lookup = {f["name"]: f["id"] for f in all_drive_files}

    if metadata_filename not in file_lookup:
        raise FileNotFoundError(f"{metadata_filename} not found in Google Drive.")

    print(f"📅 Downloading metadata: {metadata_filename}")
    request = service.files().get_media(fileId=file_lookup[metadata_filename])

    local_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        with open(local_path, "wb") as f:
            downloader = MediaIoBaseDownload(f, request)
            done = False
            while not done:
                status, done = downloader.next_chunk()
                if status:
                    print(f"   Download {int(status.progress() * 100)}%")
    except Exception as e:
        raise IOError(f"Failed to download metadata: {e}")

    return local_path


_download_progress = ""
_download_thread = None


def download_specific_files(model_name, filenames):
    """Download specific simulation files for a given model.

    Parameters
    ----------
    model_name : str
        Model name ('lat' or 'ss').
    filenames : list of str
        List of filenames to download.
    """
    global _download_progress

    if not filenames:
        _download_progress = "⚠️ No filenames provided for download."
        return

    service = get_drive_service()
    folder_id = GDRIVE_FOLDER_IDS[model_name]
    local_dir = LOCAL_DATA_FOLDER / f"{model_name}_data"
    local_dir.mkdir(parents=True, exist_ok=True)

    print(f"📂 Saving downloaded files to: {local_dir}")

    drive_files = list_files_in_folder(service, folder_id)
    drive_lookup = {f['name']: f['id'] for f in drive_files}
    total_files = len(filenames)

    for idx, filename in enumerate(filenames, start=1):
        local_path = local_dir / filename

        if local_path.exists():
            _download_progress = f"✅ [{idx}/{total_files}] {filename} already exists"
            continue

        if filename not in drive_lookup:
            _download_progress = f"❌ [{idx}/{total_files}] {filename} not found in Drive"
            continue

        _download_progress = f"⬇️ [{idx}/{total_files}] Downloading {filename}"

        file_id = drive_lookup[filename]
        request = service.files().get_media(fileId=file_id)

        try:
            with open(local_path, "wb") as f:
                downloader = MediaIoBaseDownload(f, request)
                done = False
                while not done:
                    status, done = downloader.next_chunk()
        except Exception as e:
            _download_progress = f"❌ Failed to download {filename}: {e}"
            continue

    _download_progress = "✅ Download finished."


def start_download_thread(model_name, filenames):
    """Start downloading files in a background thread.

    Parameters
    ----------
    model_name : str
        Model name ('lat' or 'ss').
    filenames : list of str
        Files to download.
    """
    global _download_thread
    _download_thread = threading.Thread(target=download_specific_files, args=(model_name, filenames))
    _download_thread.start()


def get_progress_log():
    """Return the current download progress message.

    Returns
    -------
    str
        Current download status string.
    """
    global _download_progress
    return _download_progress
