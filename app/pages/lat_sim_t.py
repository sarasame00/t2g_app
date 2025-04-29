from dash import dcc, html, Input, Output, callback, register_page

import pandas as pd
import numpy as np

from logic.data_loader import load_filtered_metadata, load_correl_data
import plots.visualize as visual
from logic.inference import infer_ion_type
import dash_bootstrap_components as dbc
from logic.sym_utils import take_borders

# === CONFIGURATION ===
model = "lat"

# === Load metadata
df, DATA_DIR = load_filtered_metadata(model, data_ext=".hdf5")

# === Infer ion type for each row
df['ion_type'] = df.apply(infer_ion_type, axis=1)

# === Define parameter names
float_params = ["U", "J", "g", "t", "lbd"]
param_names = float_params

# Map internal parameter names to human-readable labels
param_labels = {
    "U": "U (eV)",
    "J": "J (eV)",
    "g": "g (eV)",
    "t": "t (eV)",
    "lbd": "ξ (eV)"
}

# === Register Page with Dash Pages system
register_page(__name__, path='/lat_t', name='Lattice model')

# === Layout of the page
layout = html.Div([
    html.H2("Lattice Model"),

    html.Div([
        # === Sidebar ===
        dcc.Store(id="fixed-axes-store", storage_type="memory"),  # Store for fixed axes

        html.Div([
            # Axis mode toggle (Auto / Fixed)
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

            # Ion type selector
            html.Label("Select Ion Type:"),
            dcc.Dropdown(
                id="ion-type-dropdown-lat-t",
                options=[{'label': ion, 'value': ion} for ion in sorted(df['ion_type'].unique())],
                placeholder="Select an ion type",
                value="3d_d1",
                clearable=False,
                style={"marginBottom": "25px", "width": "100%"}
            ),

            # Store for initializing dropdowns
            dcc.Store(id="lat-t-initializer", data={}, storage_type='memory'),

            # Parameter dropdowns
            dcc.Loading(
                id="loading-dropdowns-lat-t",
                type="dot",
                children=[
                    html.Div([
                        html.Label(param_labels.get(param, param)),
                        dcc.Dropdown(id=f"t-dropdown-{param}", multi=(param == "t"), clearable=False, style={"width": "100%"})
                    ], style={"marginBottom": "25px"})
                    for param in param_names
                ]
            )
        ], style={
            "flex": "0 0 250px",
            "padding": "15px",
            "boxSizing": "border-box",
            "overflowY": "auto"
        }),

        # === Plot Area ===
        html.Div([
            dbc.Container([
                dbc.Row([
                    dbc.Col(dcc.Graph(id="t-plot-1", style={"height": "35vh"}), width=4),
                    dbc.Col(dcc.Graph(id="t-plot-3", style={"height": "35vh"}), width=4),
                    dbc.Col(dcc.Graph(id="t-plot-5", style={"height": "35vh"}), width=4),
                ]),
                dbc.Row([
                    dbc.Col(dcc.Graph(id="t-plot-2", style={"height": "35vh"}), width=4),
                    dbc.Col(dcc.Graph(id="t-plot-4", style={"height": "35vh"}), width=4),
                    dbc.Col(html.Div(id="legend-div", style={"padding": "10px", "fontSize": "14px", "lineHeight": "1.6"}), width=4)
                ]),
            ], fluid=True)
        ], style={
            "flex": "1",
            "padding": "15px",
            "boxSizing": "border-box"
        })
    ],
    style={
        "display": "flex",
        "flexDirection": "row",
        "overflow": "hidden"
    })
], style={
    "margin": "20px",
    "padding": "10px",
    "boxSizing": "border-box",
    "overflow": "hidden"
})

# === CALLBACKS ===

# Initialize parameter dropdowns based on selected ion type
@callback(
    [Output(f"t-dropdown-{param}", "options") for param in param_names] +
    [Output(f"t-dropdown-{param}", "value") for param in param_names],
    Input("ion-type-dropdown-lat-t", "value")
)
def initialize_dropdowns(selected_ion_type):
    """Initialize dropdown options and default values."""
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

# Compute fixed axes ranges for plots
@callback(
    Output("fixed-axes-store", "data"),
    Input("ion-type-dropdown-lat-t", "value")
)
def compute_fixed_axes(selected_ion_type):
    """Compute global fixed axis ranges."""
    if not selected_ion_type:
        return {}

    filtered_df = df[df['ion_type'] == selected_ion_type]

    data_list = []
    for idx, row in filtered_df.iterrows():
        filename = row["filename"]
        file_path = DATA_DIR / filename

        if not file_path.exists():
            continue

        try:
            data = load_correl_data(file_path)
        except Exception:
            continue

        data_list.append(data)

    if not data_list:
        return {}

    # Extract min/max from correlation functions
    momentum_min, momentum_max = [], []
    for data in data_list:
        orbcharge = 4 * (data["corrdiag"] - data["corroffd"])
        spincharge = 2 * (3 * data["corrdiag"] + data["corroffd"])

        dist, orbcharge_k = take_borders(data["irrBZ"], orbcharge)
        dist, spin_k = take_borders(data["irrBZ"], spincharge)

        momentum_min.append(np.min(orbcharge_k))
        momentum_min.append(np.min(spin_k))
        momentum_max.append(np.max(orbcharge_k))
        momentum_max.append(np.max(spin_k))

    # Add margin
    margin_factor = 0.05
    momentum_range = [min(momentum_min), max(momentum_max)]
    momentum_margin = (momentum_range[1] - momentum_range[0]) * margin_factor

    fixed_ranges = {
        "momentum": [momentum_range[0] - momentum_margin, momentum_range[1] + momentum_margin],
        "orbital_real": [-0.15, 0.15],
        "spin_real": [-0.15, 0.15],
    }

    return fixed_ranges

# Update plots when user changes parameters
@callback(
    Output("t-plot-1", "figure"),
    Output("t-plot-2", "figure"),
    Output("t-plot-3", "figure"),
    Output("t-plot-4", "figure"),
    Output("t-plot-5", "figure"),
    Output("legend-div", "children"),
    Input("ion-type-dropdown-lat-t", "value"),
    Input("axis-mode-toggle", "value"),
    Input("fixed-axes-store", "data"),
    *[Input(f"t-dropdown-{param}", "value") for param in param_names]
)
def update_lat_plots(selected_ion_type, axis_mode, fixed_axes, U, J, g, t_list, lbd):
    """Update all plots according to user selection."""
    if not selected_ion_type:
        empty_fig = visual.empty_plot(message="❌ Select an ion type")
        return empty_fig, empty_fig, empty_fig, empty_fig, empty_fig, html.Div("No legend")

    # Defensive: Ensure t_list is a list
    if not isinstance(t_list, list):
        t_list = [t_list]

    filtered_df = df[df['ion_type'] == selected_ion_type]
    data_list = []
    t_values = []

    for t in t_list:
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

        filename = match.iloc[0]["filename"]
        file_path = DATA_DIR / filename

        if not file_path.exists():
            continue

        try:
            data = load_correl_data(file_path)
        except Exception:
            continue

        data_list.append(data)
        t_values.append(t)

    if not data_list:
        empty_fig = visual.empty_plot(message="❌ No matching data")
        return empty_fig, empty_fig, empty_fig, empty_fig, empty_fig, html.Div("No legend")

    # === Handle fixed axis ranges if enabled ===
    momentum_fixed = fixed_axes.get("momentum", None) if fixed_axes else None
    orbital_real_fixed = fixed_axes.get("orbital_real", None) if fixed_axes else None
    spin_real_fixed = fixed_axes.get("spin_real", None) if fixed_axes else None

    fig_orbital_momentum = visual.plot_orbital_momentum(
        data_list, t_values, fixed_range=momentum_fixed if axis_mode == "fixed" else None
    )
    fig_spin_momentum = visual.plot_spin_momentum(
        data_list, t_values, fixed_range=momentum_fixed if axis_mode == "fixed" else None
    )
    fig_orbital_real = visual.plot_orbital_real(
        data_list, t_values, fixed_range=orbital_real_fixed if axis_mode == "fixed" else None
    )
    fig_spin_real = visual.plot_spin_real(
        data_list, t_values, fixed_range=spin_real_fixed if axis_mode == "fixed" else None
    )
    fig_nearest_neighbor = visual.plot_nn_correlation_vs_t(data_list, t_values)
    legend_html = visual.build_custom_legend(t_values)

    return fig_orbital_momentum, fig_spin_momentum, fig_orbital_real, fig_spin_real, fig_nearest_neighbor, legend_html
