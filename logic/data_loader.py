import pandas as pd
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

def get_files_to_download(df, selected_ion_types, model):
    filtered_df = df[df["ion_type"].isin(selected_ion_types)].copy()

    # Use different file extensions per model
    extension = {
        "lat": ".hdf5",
        "ss": ""  # no extension
    }[model]

    filtered_df["filename"] = filtered_df["timestamp"].astype(str) + extension

    # Check if files exist locally
    local_dir = LOCAL_DATA_FOLDER / f"{model}_data"
    filtered_df["downloaded"] = filtered_df["filename"].apply(
        lambda f: (local_dir / f).exists()
    )

    missing_files = filtered_df[~filtered_df["downloaded"]]
    return missing_files
