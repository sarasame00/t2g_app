import pandas as pd
from pathlib import Path
import h5py

from logic.inference import infer_ion_type
from sync.config import LOCAL_DATA_FOLDER
from sync.gdrive_sync import download_metadata_csv

# === Load and Filter Metadata ===

def load_simulation_metadata(model: str):
    """
    Download and load simulation metadata CSV for a given model ('lat' or 'ss').

    Returns a clean dataframe with numeric parameter columns and inferred ion types.
    """
    assert model in ["lat", "ss"], "Model must be 'lat' or 'ss'"

    # Ensure metadata CSV exists by downloading it
    download_metadata_csv(model)

    # Build local path
    file_path = LOCAL_DATA_FOLDER / f"{model}_data" / f"simulated_values_{model}.csv"
    print(f"🔍 Looking for file at: {file_path}")

    if not file_path.exists():
        raise FileNotFoundError(f"Metadata CSV not found: {file_path}")

    # Load raw CSV
    df = pd.read_csv(file_path)

    # Force numeric types in parameter columns
    numeric_cols = ["U", "J", "g", "lbd", "B", "N"]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # Drop rows that are completely broken (e.g., missing N)
    df = df.dropna(subset=["N"])

    # Safely apply ion type inference
    def safe_infer(row):
        try:
            return infer_ion_type(row)
        except Exception:
            return "unknown"

    df["ion_type"] = df.apply(safe_infer, axis=1)

    return df


def check_file_existence(df, model, extension=""):
    """
    Add 'filename' and 'downloaded' columns based on local file presence.

    Parameters:
    ----------
    df : pandas.DataFrame
        Metadata DataFrame.
    model : str
        Model name ("lat" or "ss").
    extension : str
        File extension to add (e.g., ".hdf5" for lat models).

    Returns:
    -------
    df : pandas.DataFrame
        DataFrame with 'filename' and 'downloaded' columns added.
    local_dir : Path
        Local directory where files are expected.
    """
    local_dir = LOCAL_DATA_FOLDER / f"{model}_data"

    # Create filename based on timestamp and desired extension
    df = df.copy()
    df["filename"] = df["timestamp"].astype(str) + extension

    # Check if each file exists locally
    df["downloaded"] = df["filename"].apply(lambda f: (local_dir / f).exists())

    return df, local_dir

def load_filtered_metadata(model: str, data_ext: str = ""):
    """
    Load metadata and filter only rows with corresponding downloaded data files.

    Parameters:
    ----------
    model : str
        Model name ("lat" or "ss").
    data_ext : str
        File extension to use for data files.

    Returns:
    -------
    df : pandas.DataFrame
        Filtered metadata with downloaded files only.
    data_dir : Path
        Path to the local data directory.
    """
    df = load_simulation_metadata(model)
    df, data_dir = check_file_existence(df, model, data_ext)

    # Keep only downloaded simulations
    return df[df["downloaded"]], data_dir

def get_files_to_download(df, selected_ion_types, model):
    """
    Given selected ion types, find missing (not yet downloaded) simulation files.

    Parameters:
    ----------
    df : pandas.DataFrame
        Metadata DataFrame.
    selected_ion_types : list of str
        List of ion types to filter (e.g., ["3d_d1", "4d_d1"]).
    model : str
        Model name ("lat" or "ss").

    Returns:
    -------
    pandas.DataFrame
        Subset of DataFrame corresponding to missing files.
    """
    # Choose file extension
    extension = { "lat": ".hdf5", "ss": "" }[model]

    # Filter rows matching selected ion types
    filtered_df = df[df["ion_type"].isin(selected_ion_types)].copy()

    # Re-check file existence
    filtered_df, _ = check_file_existence(filtered_df, model, extension)

    # Return rows that are missing (not downloaded)
    return filtered_df[~filtered_df["downloaded"]]

# === Load Data from HDF5 Files ===

def load_correl_data(h5_path):
    """
    Load orbital and spin correlation data from a simulation HDF5 file.

    Parameters:
    ----------
    h5_path : Union[str, Path]
        Path to the .hdf5 file.

    Returns:
    -------
    dict
        Dictionary containing:
        - irrBZ : np.ndarray (k-points in BZ)
        - k_sz : int (grid size)
        - corrdiag : np.ndarray (diagonal correlators)
        - corroffd : np.ndarray (off-diagonal correlators)
        - filename : str (filename stem)
    """
    h5_path = Path(h5_path)  # Ensure it's a Path object

    with h5py.File(h5_path, "r") as f:
        return {
            "irrBZ": f["irrBZ"][:],
            "k_sz": f["k_sz"][()],
            "corrdiag": f["correldiag"][:],
            "corroffd": f["correloffd"][:],
            "filename": h5_path.stem
        }
