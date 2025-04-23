import pandas as pd
from pathlib import Path
import h5py

from logic.inference import infer_ion_type
from sync.config import LOCAL_DATA_FOLDER
from sync.gdrive_sync import download_metadata_csv


def load_simulation_metadata(model: str):
    assert model in ["lat", "ss"], "Model must be 'lat' or 'ss'"

    print(f"🧠 Loading metadata for model: {model}")
    print(f"📥 Downloading metadata CSV...")
    download_metadata_csv(model)

    file_path = LOCAL_DATA_FOLDER / f"{model}_data" / f"simulated_values_{model}.csv"
    print(f"🔍 Looking for file at: {file_path}")

    if not file_path.exists():
        raise FileNotFoundError(f"Metadata CSV not found: {file_path}")

    df = pd.read_csv(file_path)
    df["ion_type"] = df.apply(infer_ion_type, axis=1)
    return df

def check_file_existence(df, model, extension=""):
    """
    Adds 'filename' and 'downloaded' columns to the DataFrame based on local file presence.
    """
    local_dir = LOCAL_DATA_FOLDER / f"{model}_data"
    df = df.copy()
    df["filename"] = df["timestamp"].astype(str) + extension
    df["downloaded"] = df["filename"].apply(lambda f: (local_dir / f).exists())
    return df, local_dir

def load_filtered_metadata(model: str, data_ext: str = ""):
    df = load_simulation_metadata(model)
    df, data_dir = check_file_existence(df, model, data_ext)
    return df[df["downloaded"]], data_dir

def get_files_to_download(df, selected_ion_types, model):
    extension = { "lat": ".hdf5", "ss": "" }[model]
    filtered_df = df[df["ion_type"].isin(selected_ion_types)].copy()
    filtered_df, _ = check_file_existence(filtered_df, model, extension)
    return filtered_df[~filtered_df["downloaded"]]


def load_correl_data(h5_path):
    """
    Loads all data needed to plot orbital, spin-orbital, and spin-exchange correlations
    from a single .hdf5 simulation output file.

    Parameters:
    - h5_path (Union[str, Path]): Path to the .hdf5 file.

    Returns:
    - dict: Dictionary containing irrBZ, k_sz, and all correlators.
    """
    h5_path = Path(h5_path)  # ensure it's a Path object

    with h5py.File(h5_path, "r") as f:
        return {
            "irrBZ": f["irrBZ"][:],
            "k_sz": f["k_sz"][()],
            "corrdiag": f["correldiag"][:],
            "corroffd": f["correloffd"][:],
            "filename": h5_path.stem  # this gives filename without extension
        }
