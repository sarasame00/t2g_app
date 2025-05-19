from dash import dcc, html, Input, Output, callback, register_page
import numpy as np
import os, sys
from pathlib import Path
from itertools import product

from logic.data_loader import load_cached_filtered_metadata, load_correl_data
import plots.visualize as visual
import dash_bootstrap_components as dbc
from logic.sym_utils import take_borders
from sync.config import LOCAL_DATA_FOLDER

# === CONFIGURATION ===
model = "lat"

# === Load metadata
# Load filtered metadata and set the data directory
# based on local configuration and model name
df, DATA_DIR = load_cached_filtered_metadata("lat", data_ext=".hdf5")
DATA_DIR = Path(LOCAL_DATA_FOLDER) / f"{model}_data"

# === Define parameter names
float_params = ["U", "J", "g", "t", "lbd"]
param_names = float_params

# Human-readable labels for UI display
param_labels = {
    "U": "U (eV)",
    "J": "J (eV)",
    "g": "g (eV)",
    "t": "t (eV)",
    "lbd": "ξ (eV)"
}

# === Register Dash Page ===
register_page(__name__, path='/lat_t', name='Lattice model')

# === Layout of the Dash Page ===
layout = html.Div([
    html.Div([
        html.H2("Lattice Model"),

        html.Div([
            dbc.Container([
                dbc.Row([
                    dbc.Col(dcc.Graph(id="t-plot-1", style={"height": "23vh"}), width=4),
                    dbc.Col(dcc.Graph(id="t-plot-2", style={"height": "23vh"}), width=4),
                    dbc.Col(dcc.Graph(id="t-plot-6", style={"height": "23vh"}), width=4),
                ]),
                dbc.Row([
                    dbc.Col(dcc.Graph(id="t-plot-3", style={"height": "23vh"}), width=4),
                    dbc.Col(dcc.Graph(id="t-plot-4", style={"height": "23vh"}), width=4),
                    dbc.Col(dcc.Graph(id="t-plot-7", style={"height": "23vh"}), width=4),
                ]),
                dbc.Row([
                    dbc.Col(dcc.Graph(id="t-plot-5", style={"height": "23vh"}), width=4),
                    dbc.Col(html.Div(id="legend-correl", style={"height": "23vh"}), width=4),
                    dbc.Col(html.Div(id="legend-t", style={"height": "23vh"}), width=4),
                ]),
            ], fluid=True)
        ])
    ], style={
        "marginLeft": "290px",
        "padding": "15px",
        "overflow": "hidden",
        "height": "calc(100vh - 100px)"
    }),

    # Sidebar with parameter selectors
    html.Div([
        dcc.Store(id="fixed-axes-store", storage_type="memory"),

        html.Label("Axis Mode:"),
        dcc.RadioItems(
            id="axis-mode-toggle",
            options=[
                {"label": "Auto", "value": "auto"},
                {"label": "Fixed", "value": "fixed"}
            ],
            value="auto",
            inline=True,
            labelStyle={"marginRight": "20px"},
            style={"marginBottom": "20px"}
        ),

        html.H4("Parameters"),

        html.Label("Select Ion Type:"),
        dcc.Dropdown(
            id="ion-type-dropdown-lat-t",
            options=[{'label': ion, 'value': ion} for ion in sorted(df['ion_type'].unique())],
            placeholder="Select an ion type",
            value="3d_d1",
            clearable=False,
            style={"marginBottom": "25px", "width": "100%"}
        ),

        dcc.Store(id="lat-t-initializer", data={}, storage_type='memory'),

        dcc.Loading(
            id="loading-dropdowns-lat-t",
            type="dot",
            children=[
                html.Div([
                    html.Label(param_labels.get(param, param)),
                    dcc.Dropdown(
                        id=f"t-dropdown-{param}",
                        multi= True,
                        clearable=False,
                        style={"width": "100%"}
                    )
                ], style={"marginBottom": "25px"})
                for param in param_names
            ]
        )
    ], style={
        "position": "fixed",
        "top": "80px",
        "bottom": "0",
        "left": "20px",
        "width": "250px",
        "padding": "15px",
        "boxSizing": "border-box",
        "overflowY": "auto",
        "borderRight": "1px solid #ccc",
        "backgroundColor": "white",
        "zIndex": 1000
    })
], style={
    "height": "100vh",
    "overflow": "hidden",
    "margin": "0",
    "padding": "0",
    "boxSizing": "border-box"
})


# === CALLBACKS ===

@callback(
    [Output(f"t-dropdown-{param}", "options") for param in param_names] +
    [Output(f"t-dropdown-{param}", "value") for param in param_names],
    Input("ion-type-dropdown-lat-t", "value")
)
def initialize_dropdowns(selected_ion_type):
    """Initialize dropdowns for parameters based on selected ion type.

    Parameters
    ----------
    selected_ion_type : str
        The selected ion type from the dropdown.

    Returns
    -------
    list
        A list of options and default values for each parameter dropdown.
    """
    if not selected_ion_type:
        return [[] for _ in param_names * 2]

    filtered_df = df[df['ion_type'] == selected_ion_type]
    param_values = {param: sorted(filtered_df[param].unique()) for param in param_names}

    options = [
        [{"label": f"{v:.3f}", "value": v} for v in param_values[param]]
        for param in param_names
    ]

    default_values = [
        param_values[param][0] if param != "t" else [param_values[param][0]]
        for param in param_names
    ]

    return options + default_values


@callback(
    Output("fixed-axes-store", "data"),
    Input("ion-type-dropdown-lat-t", "value")
)
def compute_fixed_axes(selected_ion_type):
    """Compute global fixed axis ranges for plots.

    Parameters
    ----------
    selected_ion_type : str
        The selected ion type.

    Returns
    -------
    dict
        Axis range settings for momentum, orbital and spin values.
    """
    if not selected_ion_type:
        return {}

    filtered_df = df[df['ion_type'] == selected_ion_type]
    data_list = []
    for idx, row in filtered_df.iterrows():
        file_path = DATA_DIR / row["filename"]
        if not file_path.exists():
            continue
        try:
            data = load_correl_data(file_path)
        except Exception:
            continue
        data_list.append(data)

    if not data_list:
        return {}

    momentum_min, momentum_max = [], []
    for data in data_list:
        orbcharge = 4 * (data["corrdiag"] - data["corroffd"])
        spincharge = 2 * (3 * data["corrdiag"] + data["corroffd"])
        _, orbcharge_k = take_borders(data["irrBZ"], orbcharge)
        _, spin_k = take_borders(data["irrBZ"], spincharge)
        momentum_min.extend([np.min(orbcharge_k), np.min(spin_k)])
        momentum_max.extend([np.max(orbcharge_k), np.max(spin_k)])

    margin_factor = 0.05
    momentum_range = [min(momentum_min), max(momentum_max)]
    margin = (momentum_range[1] - momentum_range[0]) * margin_factor

    return {
        "momentum": [momentum_range[0] - margin, momentum_range[1] + margin],
        "orbital_real": [-0.15, 0.15],
        "spin_real": [-0.15, 0.15],
    }


@callback(
    Output("t-plot-1", "figure"),
    Output("t-plot-2", "figure"),
    Output("t-plot-3", "figure"),
    Output("t-plot-4", "figure"),
    Output("t-plot-5", "figure"),
    Output("t-plot-6", "figure"),
    Output("t-plot-7", "figure"),
    Output("legend-correl", "children"),
    Output("legend-t", "children"),
    Input("ion-type-dropdown-lat-t", "value"),
    Input("axis-mode-toggle", "value"),
    Input("fixed-axes-store", "data"),
    *[Input(f"t-dropdown-{param}", "value") for param in param_names]
)
def update_lat_plots(selected_ion_type, axis_mode, fixed_axes, U_list, J_list, g_list, t_list, lbd_list):
    """Update all plots based on user inputs and selected parameters.

    Parameters
    ----------
    selected_ion_type : str
        Selected ion type.
    axis_mode : str
        Axis mode toggle ('auto' or 'fixed').
    fixed_axes : dict
        Dict with fixed axis ranges.
    U, J, g, t_list, lbd : float or list
        Physical parameters for filtering and plotting.

    Returns
    -------
    tuple
        Plotly figures and legend components.
    """
    if not selected_ion_type:
        empty_fig = visual.empty_plot(message="❌ Select an ion type")
        return (empty_fig,) * 7 + (html.Div("No legend"),) * 2


    U_vals = U_list if isinstance(U_list, list) else [U_list]
    J_vals = J_list if isinstance(J_list, list) else [J_list]
    g_vals = g_list if isinstance(g_list, list) else [g_list]
    t_vals = t_list if isinstance(t_list, list) else [t_list]
    lbd_vals = lbd_list if isinstance(lbd_list, list) else [lbd_list]

    filtered_df = df[df['ion_type'] == selected_ion_type]
    data_list, t_values = [], []

    for U, J, g, t, lbd in product(U_vals, J_vals, g_vals, t_vals, lbd_vals):
        match = filtered_df[
            (filtered_df["N"] == 1) &
            np.isclose(filtered_df["U"], U) &
            np.isclose(filtered_df["J"], J) &
            np.isclose(filtered_df["g"], g) &
            np.isclose(filtered_df["t"], t) &
            np.isclose(filtered_df["lbd"], lbd)
        ]
        if match.empty:
            continue
        file_path = DATA_DIR / match.iloc[-1]["filename"]
        if not file_path.exists():
            continue
        try:
            data = load_correl_data(file_path)
        except Exception:
            continue
        data_list.append(data)
        t_values.append((U, J, g, t, lbd))


    if not data_list:
        empty_fig = visual.empty_plot(message="❌ No matching data")
        return (empty_fig,) * 7 + (html.Div("No legend"),) * 2

    momentum_fixed = fixed_axes.get("momentum") if fixed_axes and axis_mode == "fixed" else None
    orbital_real_fixed = fixed_axes.get("orbital_real") if fixed_axes and axis_mode == "fixed" else None
    spin_real_fixed = fixed_axes.get("spin_real") if fixed_axes and axis_mode == "fixed" else None

    return (
        visual.plot_orbital_momentum(data_list, t_values, fixed_range=momentum_fixed),
        visual.plot_spin_momentum(data_list, t_values, fixed_range=momentum_fixed),
        visual.plot_orbital_real(data_list, t_values, fixed_range=orbital_real_fixed),
        visual.plot_spin_real(data_list, t_values, fixed_range=spin_real_fixed),
        visual.plot_nn_correlation_vs_t(data_list, t_values),
        visual.plot_sigmaz_momentum(data_list, t_values, fixed_range=momentum_fixed),
        visual.plot_sigmaz_real(data_list, t_values, fixed_range=orbital_real_fixed),
        visual.build_legend_correl(),
        visual.build_legend_t(t_values)
    )
