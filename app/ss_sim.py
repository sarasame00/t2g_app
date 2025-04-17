import os
import numpy as np
import pandas as pd
import plotly.express as px
from dash import Dash, dcc, html, Input, Output, callback, register_page
from matplotlib.colors import LinearSegmentedColormap, to_hex
import requests, io

from drive_utils import get_file_id_by_name, download_txt_file, creds

# === CONFIG ===
CSV_FILENAME = "simulated_values_ss.csv"
FOLDER_ID = "1qroO12tPkKu6c3w5Xy-2Reys5XFcbX5L"  # Shared Drive folder with all the files
LAT_FOLDER_ID = "1-UDQwKXUsjsOpKgKBeGaIO1Acv7T8wm6" # GDrive folder with single-site data
SS_FOLDER_ID = "1VPQ4HARo7HJVXoXWRhVYYn79Svs3IZWq" # GDrive folder with lattice data


shape = (101, 101)  # Shape of your simulation data files



def load_csv_from_drive_by_name(filename, parent_id):
    file_id = get_file_id_by_name(filename, parent_id)
    if not file_id:
        raise FileNotFoundError(f"❌ CSV file '{filename}' not found in Google Drive folder")

    if not creds.valid:
        creds.refresh(os.Request())

    url = f"https://www.googleapis.com/drive/v3/files/{file_id}?alt=media"
    headers = {"Authorization": f"Bearer {creds.token}"}

    response = requests.get(url, headers=headers)
    response.raise_for_status()

    return pd.read_csv(io.StringIO(response.text))


# === Load main CSV ===
df = load_csv_from_drive_by_name(CSV_FILENAME, SS_FOLDER_ID)

# === Prepare sliders ===
param_values = {
    "N": sorted([int(v) for v in df["N"].unique()]),
    "U": sorted([float(v) for v in df["U"].unique()]),
    "J": sorted([float(v) for v in df["J"].unique()]),
    "g": sorted([float(v) for v in df["g"].unique()]),
    "lbd": sorted([float(v) for v in df["lbd"].unique()]),
    "B": sorted([float(v) for v in df["B"].unique()])
}

# === Custom colormap ===
colors = [
    (0.0, "black"), (0.15, "yellow"), (0.25, "orange"), (0.35, "red"),
    (0.5, "magenta"), (0.65, "blue"), (0.85, "cyan"), (1.0, "white")
]
custom_cmap = LinearSegmentedColormap.from_list("custom_map", colors)
plotly_colorscale = [(i / 254, to_hex(custom_cmap(i / 254))) for i in range(255)]


# === Dash App ===
register_page(__name__, path='/', name='Single-site model')

layout = html.Div(
    [
        html.Div([
            html.Label(param),
            dcc.Slider(
                min=min(values),
                max=max(values),
                step=None,
                marks={v: str(v) for v in values},
                value=values[0],
                id=f"slider-{param}"
            )
        ], style={'margin': '20px'}) for param, values in param_values.items()
    ] + [
        dcc.Graph(id='energy-map')
    ]
)


@callback(
    Output("energy-map", "figure"),
    [Input(f"slider-{param}", "value") for param in param_values]
)
def update_figure(N, U, J, g, lbd, B):
    match = df[(df["N"] == N) & (df["U"] == U) & (df["J"] == J) &
               (df["g"] == g) & (df["B"] == B) & (df["lbd"] == lbd)]

    if match.empty:
        fig = px.imshow(np.zeros(shape), color_continuous_scale=plotly_colorscale)
        fig.update_layout(title="No matching simulation found")
        return fig

    timestamp = str(match.iloc[0]["timestamp"])
    filename = f"{timestamp}"

    file_id = get_file_id_by_name(filename, SS_FOLDER_ID)

    if not file_id:
        fig = px.imshow(np.zeros(shape), color_continuous_scale=plotly_colorscale)
        fig.update_layout(title=f"Missing file: {filename}")
        return fig

    try:
        data = download_txt_file(file_id)
        emap = data[:, 2].reshape(shape)
        zmin = np.min(emap)
        zmax = zmin + (np.max(emap) - zmin) * 1.0
    except Exception as e:
        print(f"❌ Error loading or reshaping data: {e}")
        emap = np.zeros(shape)
        zmin, zmax = 0, 1

    fig = px.imshow(
        emap,
        color_continuous_scale=plotly_colorscale,
        zmin=zmin,
        zmax=zmax
    )
    fig.update_layout(
        title=f"Ground State Energy — N={N}, U={U}, J={J}, g={g}, B={B}, λ={lbd}",
        transition_duration=300
    )
    return fig
