import os
import sys
import shutil
import pandas as pd
import h5py
from pathlib import Path
from functools import lru_cache

from logic.inference import infer_ion_type
from sync.config import LOCAL_DATA_FOLDER
from sync.gdrive_sync import download_metadata_csv

# === PATH UTILITIES ===

def resource_path(relative_path):
    """Get absolute path to bundled resource (PyInstaller or dev)."""
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

def copy_bundled_data_if_missing(model: str):
    """
    On first launch, copy bundled CSVs and data files from the PyInstaller archive to the user's local folder.
    """
    bundled_dir = Path(resource_path(f"data/{model}_data"))
    target_dir = LOCAL_DATA_FOLDER / f"{model}_data"
    target_dir.mkdir(parents=True, exist_ok=True)

    for file in bundled_dir.glob("*"):
        target = target_dir / file.name
        if not target.exists():
            try:
                shutil.copy(file, target)
            except Exception as e:
                print(f"⚠️ Failed to copy bundled data: {file} → {target}: {e}")

# === METADATA LOADING ===

def load_simulation_metadata(model: str, force_download=False):
    assert model in ["lat", "ss"], "Model must be 'lat' or 'ss'"

    # Ensure bundled fallback data is in local folder
    copy_bundled_data_if_missing(model)

    file_path = LOCAL_DATA_FOLDER / f"{model}_data" / f"simulated_values_{model}.csv"

    if force_download or not file_path.exists():
        print(f"📥 Downloading metadata: {file_path.name}")
        download_metadata_csv(model)
    else:
        print(f"✅ Using cached metadata: {file_path.name}")

    if not file_path.exists():
        raise FileNotFoundError(f"Metadata CSV not found: {file_path}")

    df = pd.read_csv(file_path)

    for col in ["U", "J", "g", "lbd", "B", "N"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    df = df.dropna(subset=["N"])
    df["ion_type"] = df.apply(lambda row: safe_infer(row), axis=1)
    return df

def safe_infer(row):
    try:
        return infer_ion_type(row)
    except Exception:
        return "unknown"

# === FILE PRESENCE CHECK ===

def check_file_existence(df, model, extension=""):
    local_dir = LOCAL_DATA_FOLDER / f"{model}_data"
    df = df.copy()
    df["filename"] = df["timestamp"].astype(str) + extension
    df["downloaded"] = df["filename"].apply(lambda f: (local_dir / f).exists())
    return df, local_dir

# === METADATA FILTERING ===

def load_filtered_metadata(model: str, data_ext: str = "", force_download=False):
    df = load_simulation_metadata(model, force_download=force_download)
    df, data_dir = check_file_existence(df, model, data_ext)
    return df[df["downloaded"]], data_dir

@lru_cache(maxsize=2)
def load_cached_filtered_metadata(model: str, data_ext: str = ""):
    df, data_dir = load_filtered_metadata(model, data_ext, force_download=False)
    df["ion_type"] = df.apply(lambda row: safe_infer(row), axis=1)
    return df, data_dir

# === FILE DOWNLOADS ===

def get_files_to_download(df, selected_ion_types, model):
    ext = { "lat": ".hdf5", "ss": "" }[model]
    filtered_df = df[df["ion_type"].isin(selected_ion_types)].copy()
    filtered_df, _ = check_file_existence(filtered_df, model, ext)
    return filtered_df[~filtered_df["downloaded"]]

# === HDF5 LOADING ===

def load_correl_data(h5_path):
    h5_path = Path(h5_path)  # Expect local absolute path
    if not h5_path.exists():
        raise FileNotFoundError(f"❌ Data file not found: {h5_path}")

    with h5py.File(h5_path, "r") as f:
        return {
            "irrBZ": f["irrBZ"][:],
            "k_sz": f["k_sz"][()],
            "corrdiag": f["correldiag"][:],
            "corroffd": f["correloffd"][:],
            "filename": h5_path.stem,
        }
