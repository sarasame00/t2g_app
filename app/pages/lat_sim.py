from dash import dcc, html, Input, Output, callback, register_page
import pandas as pd
from logic.data_loader import load_filtered_metadata, load_correl_data
import plots.visualize as visual

# === CONFIG ===
model = "lat"
shape = (101, 101)

# === Load metadata
df, DATA_DIR = load_filtered_metadata(model, data_ext=".hdf5")

# === Round float params to avoid precision mismatch
float_params = ["U", "J", "g", "t", "lbd"]
df[float_params] = df[float_params].round(3)

# === Parameter names and values
param_names = ["N"] + float_params
param_values = {param: sorted(df[param].unique()) for param in param_names}

# === Page registration
register_page(__name__, path='/lat', name='Lattice model')

# === Layout
layout = html.Div([
    html.H2("Lattice Simulation Viewer"),

    html.Div([
        html.Div([
            html.H4("Parameters"),
            *[
                html.Div([
                    html.Label(param),
                    dcc.Dropdown(
                        id=f"dropdown-{param}",
                        options=[{"label": str(v), "value": v} for v in values],
                        value=values[0],
                        clearable=False
                    )
                ], style={"marginBottom": "20px"})
                for param, values in param_values.items()
            ]
        ], style={"width": "33%", "padding": "15px"}),

        html.Div([
            html.Div(id="lat-left-plots", style={"flex": 1, "padding": "10px"}),
            html.Div(id="lat-right-plots", style={"flex": 1, "padding": "10px"})
        ], style={"display": "flex", "flexWrap": "wrap", "gap": "20px", "width": "67%", "padding": "15px"})

    ], style={"display": "flex", "flexDirection": "row"})
])

# === Callback
@callback(
    Output("lat-left-plots", "children"),
    Output("lat-right-plots", "children"),
    [Input(f"dropdown-{param}", "value") for param in param_names]
)
def update_lat_plots(N, U, J, g, t, lbd):
    # Round inputs for comparison
    params = {
        "N": N,
        "U": round(U, 3),
        "J": round(J, 3),
        "g": round(g, 3),
        "t": round(t, 3),
        "lbd": round(lbd, 3)
    }

    match = df[
        (df["N"] == params["N"]) &
        (df["U"] == params["U"]) &
        (df["J"] == params["J"]) &
        (df["g"] == params["g"]) &
        (df["t"] == params["t"]) &
        (df["lbd"] == params["lbd"])
    ]

    if match.empty:
        return html.P("❌ No matching simulation found."), html.P("")

    filename = match.iloc[0]["filename"]
    file_path = DATA_DIR / filename

    if not file_path.exists():
        return html.P(f"❌ File '{filename}' not found locally."), html.P("")

    try:
        data = load_correl_data(file_path)
    except Exception as e:
        return html.P(f"❌ Error reading file: {e}"), html.P("")

    # Generate plots
    plot_funcs = [
        visual.plot_orbital_momentum,
        visual.plot_orbital_real,
        visual.plot_spin_momentum,
        visual.plot_spin_real,
        visual.plot_spinexchange_momentum
    ]

    encoded_imgs = [
        html.Img(
            src=visual.fig_to_base64(func(data, return_fig=True)),
            style={"width": "100%", "marginBottom": "20px"}
        ) for func in plot_funcs
    ]

    return encoded_imgs[:3], encoded_imgs[3:]
