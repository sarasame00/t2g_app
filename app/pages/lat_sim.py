from dash import dcc, html, Input, Output, callback, register_page
import pandas as pd
import numpy as np
from logic.data_loader import load_filtered_metadata, load_correl_data
import plots.visualize as visual

# === CONFIG ===
model = "lat"
shape = (101, 101)

# === Load metadata
df, DATA_DIR = load_filtered_metadata(model, data_ext=".hdf5")

float_params = ["U", "J", "g", "t", "lbd"]

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
            dcc.Store(id="lat-initializer", data={}, storage_type='memory'),
            dcc.Loading(
                id="loading-dropdowns-lat",
                type="dot",
                children=[
                    *[
                        html.Div([
                            html.Label(param),
                            dcc.Dropdown(id=f"dropdown-{param}", clearable=False)
                        ], style={"marginBottom": "20px"})
                        for param, values in param_values.items()
                    ]
                ]
            )
        ], style={"width": "25%", "padding": "15px"}),

        html.Div([
            dcc.Loading(
                id="loading-plots-lat",
                type="circle",
                children=[
                    html.Div(id="lat-left-plots", style={"flex": 1, "padding": "10px"}),
                    html.Div(id="lat-right-plots", style={"flex": 1, "padding": "10px"})
                ]
            )
        ], style={"display": "flex", "flexWrap": "wrap", "gap": "20px", "width": "75%", "padding": "15px"})

    ], style={"display": "flex", "flexDirection": "row"})
])


# === Callback
@callback(
    [Output(f"dropdown-{param}", "options") for param in param_names] +
    [Output(f"dropdown-{param}", "value") for param in param_names],
    Input("lat-initializer", "data")
)
def initialize_dropdowns(_):
    df, _ = load_filtered_metadata(model, data_ext=".hdf5")

    param_values = {param: sorted(df[param].unique()) for param in param_names}

    options = [
        [{"label": f"{v:.3f}", "value": v} for v in param_values[param]]
        for param in param_names
    ]

    default_values = [param_values[param][0] for param in param_names]

    return options + default_values

@callback(
    Output("lat-left-plots", "children"),
    Output("lat-right-plots", "children"),
    [Input(f"dropdown-{param}", "value") for param in param_names]
)
def update_lat_plots(N, U, J, g, t, lbd):
    # Round inputs for comparison
    params = {
        "N": N,
        "U": U,
        "J": J,
        "g": g,
        "t": t,
        "lbd": lbd
    }


    match = df[
        (df["N"] == params["N"]) &
        np.isclose(df["U"], params["U"]) &
        np.isclose(df["J"], params["J"]) &
        np.isclose(df["g"], params["g"]) &
        np.isclose(df["t"], params["t"]) &
        np.isclose(df["lbd"], params["lbd"])
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
