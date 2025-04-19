'''
from dash import html, dcc, Input, Output, callback, register_page
import os
import io
import pandas as pd
import base64
import matplotlib.pyplot as plt

import requests
from drive_utils import get_file_id_by_name, download_file_as_bytes, creds
from core.loaders import load_correl_data
import core.visualize as visual

register_page(__name__, path='/new', name='Lattice model')

# === CONFIG ===
CSV_FILENAME = "simulated_values_lat.csv"
LAT_FOLDER_ID = "1-UDQwKXUsjsOpKgKBeGaIO1Acv7T8wm6" # GDrive folder with latice data
shape = (101, 101)  # This might be unused unless needed later

# === Load CSV ===
def load_csv():
    if not creds.valid:
        creds.refresh(os.Request())
    file_id = get_file_id_by_name(CSV_FILENAME, LAT_FOLDER_ID)
    if not file_id:
        raise FileNotFoundError(f"❌ CSV file '{CSV_FILENAME}' not found in Google Drive folder")

    url = f"https://www.googleapis.com/drive/v3/files/{file_id}?alt=media"
    headers = {"Authorization": f"Bearer {creds.token}"}
    response = requests.get(url, headers=headers)
    response.raise_for_status()

    return pd.read_csv(io.StringIO(response.text))

df = load_csv()

# === Extract parameter ranges ===
param_values = {
    "N": sorted(df["N"].unique()),
    "U": sorted(df["U"].unique()),
    "J": sorted(df["J"].unique()),
    "g": sorted(df["g"].unique()),
    "lbd": sorted(df["lbd"].unique()),
    "t": sorted(df["t"].unique())
}

# === Layout ===
layout = html.Div([
    html.H2("Lattice model"),
    html.Div([
        # Column 1 – Sliders
        html.Div([
            html.H4("Parameters"),
            *[
                html.Div([
                    html.Label(param),
                    dcc.Slider(
                        id=f"slider-{param}",
                        min=min(values),
                        max=max(values),
                        step=None,
                        marks={float(v): str(v) for v in values},
                        value=values[0]
                    )
                ], style={"marginBottom": "30px"})
                for param, values in param_values.items()
            ]
        ], style={"width": "33%", "padding": "10px"}),

        # Column 2 – Left-side plots (3 stacked)
        html.Div(id="lat-left-plots", style={"width": "33%", "padding": "10px"}),

        # Column 3 – Right-side plots (2 stacked)
        html.Div(id="lat-right-plots", style={"width": "33%", "padding": "10px"})
    ], style={"display": "flex", "flexDirection": "row"})
])



# === Helper: convert matplotlib fig to base64 ===
def fig_to_base64(fig):
    buf = io.BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight", dpi=150)
    buf.seek(0)
    encoded = base64.b64encode(buf.read()).decode('utf-8')
    plt.close(fig)
    return f"data:image/png;base64,{encoded}"


# === Callback ===
@callback(
    Output("lat-left-plots", "children"),
    Output("lat-right-plots", "children"),
    [Input(f"slider-{param}", "value") for param in param_values]
)
def update_lat_plots(N, U, J, g, lbd, t):
    match = df[(df["N"] == N) & (df["U"] == U) & (df["J"] == J) &
               (df["g"] == g) & (df["t"] == t) & (df["lbd"] == lbd)]

    if match.empty:
        return html.P("❌ No matching simulation found."), html.P("")

    filename = match.iloc[0]["timestamp"] + ".hdf5"

    file_id = get_file_id_by_name(filename, LAT_FOLDER_ID)
    if not file_id:
        return html.P(f"❌ File '{filename}' not found in Google Drive")

    raw_bytes = download_file_as_bytes(file_id)
    tmp_path = f"/tmp/{filename}"
    with open(tmp_path, "wb") as f:
        f.write(raw_bytes)

    try:
        data = load_correl_data(tmp_path)
    except Exception as e:
        return html.P(f"❌ Error: {e}"), html.P("")

    # Generate plots
    plot_funcs = [
        visual.plot_orbital_momentum,
        visual.plot_orbital_real,
        visual.plot_spin_momentum,
        visual.plot_spin_real,
        visual.plot_spinexchange_momentum
    ]

    encoded_imgs = []
    for func in plot_funcs:
        fig = func(data, return_fig=True)
        encoded_imgs.append(html.Img(src=fig_to_base64(fig), style={"width": "100%", "marginBottom": "20px"}))

    # Return 3 plots in left column, 2 in right
    return encoded_imgs[:3], encoded_imgs[3:]
'''