from dash import dcc, html, Input, Output, callback, register_page
import pandas as pd
import numpy as np
from logic.data_loader import load_filtered_metadata, load_correl_data
import plots.visualize as visual
from logic.inference import infer_ion_type
import dash_bootstrap_components as dbc

# === CONFIG ===
model = "lat"

# === Load metadata
df, DATA_DIR = load_filtered_metadata(model, data_ext=".hdf5")

# === Infer ion type for each row
df['ion_type'] = df.apply(infer_ion_type, axis=1)

# === Parameter names (no N)
float_params = ["U", "J", "g", "t", "lbd"]
param_names = float_params

# === Page registration
register_page(__name__, path='/lat', name='Lattice model')

# === Layout
layout = html.Div([
    html.H2("Lattice Simulation Viewer"),

    html.Div([
        # Sidebar
        html.Div([
            html.H4("Parameters"),
            html.Label("Select Ion Type:"),
            dcc.Dropdown(
                id="ion-type-dropdown-lat",
                options=[{'label': ion, 'value': ion} for ion in sorted(df['ion_type'].unique())],
                placeholder="Select an ion type",
                clearable=False,
                style={"marginBottom": "10px", "width": "100%"}
            ),
            dcc.Store(id="lat-initializer", data={}, storage_type='memory'),
            dcc.Loading(
                id="loading-dropdowns-lat",
                type="dot",
                children=[
                    html.Div([
                        html.Label(param),
                        dcc.Dropdown(id=f"dropdown-{param}", clearable=False, style={"width": "100%"})
                    ], style={"marginBottom": "10px"})
                    for param in param_names
                ]
            )
        ], style={
            "flex": "0 0 250px",
            "padding": "15px",
            "boxSizing": "border-box",
            "height": "calc(100vh - 60px)",
            "overflowY": "auto"
        }),

        # Plot Area
        html.Div([
            dbc.Container([
                # First row: 3 plots
                dbc.Row([
                    dbc.Col(dcc.Graph(id="plot-1", style={"height": "40vh"}), width=4),
                    dbc.Col(dcc.Graph(id="plot-3", style={"height": "40vh"}), width=4),
                    dbc.Col(dcc.Graph(id="plot-5", style={"height": "40vh"}), width=4),
                ]),

                # Second row: 2 plots (leave third empty)
                dbc.Row([
                    dbc.Col(dcc.Graph(id="plot-2", style={"height": "40vh"}), width=4),
                    dbc.Col(dcc.Graph(id="plot-4", style={"height": "40vh"}), width=4),
                    dbc.Col(html.Div(), width=4),  # empty column for balance
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
        "height": "calc(100vh - 60px)",
        "overflow": "hidden"
    })
])





# === Callbacks

@callback(
    [Output(f"dropdown-{param}", "options") for param in param_names] +
    [Output(f"dropdown-{param}", "value") for param in param_names],
    Input("ion-type-dropdown-lat", "value")
)
def initialize_dropdowns(selected_ion_type):
    if not selected_ion_type:
        return [[] for _ in param_names * 2]

    filtered_df = df[df['ion_type'] == selected_ion_type]

    param_values = {param: sorted(filtered_df[param].unique()) for param in param_names}

    options = [
        [{"label": f"{v:.3f}", "value": v} for v in param_values[param]]
        for param in param_names
    ]

    default_values = [param_values[param][0] for param in param_names]

    return options + default_values

@callback(
    Output("plot-1", "figure"),
    Output("plot-2", "figure"),
    Output("plot-3", "figure"),
    Output("plot-4", "figure"),
    Output("plot-5", "figure"),
    [Input("ion-type-dropdown-lat", "value")] + [Input(f"dropdown-{param}", "value") for param in param_names]
)
def update_lat_plots(selected_ion_type, U, J, g, t, lbd):
    if not selected_ion_type:
        empty_fig = visual.empty_plot()
        return empty_fig, empty_fig, empty_fig, empty_fig, empty_fig

    filtered_df = df[df['ion_type'] == selected_ion_type]

    match = filtered_df[
        (filtered_df["N"] == 1) &
        np.isclose(filtered_df["U"], U) &
        np.isclose(filtered_df["J"], J) &
        np.isclose(filtered_df["g"], g) &
        np.isclose(filtered_df["t"], t) &
        np.isclose(filtered_df["lbd"], lbd)
    ]

    if match.empty:
        empty_fig = visual.empty_plot()
        return empty_fig, empty_fig, empty_fig, empty_fig, empty_fig

    filename = match.iloc[0]["filename"]
    file_path = DATA_DIR / filename

    if not file_path.exists():
        empty_fig = visual.empty_plot()
        return empty_fig, empty_fig, empty_fig, empty_fig, empty_fig

    try:
        data = load_correl_data(file_path)
    except Exception as e:
        empty_fig = visual.empty_plot()
        return empty_fig, empty_fig, empty_fig, empty_fig, empty_fig

    fig_orbital_momentum = visual.plot_orbital_momentum(data)
    fig_spin_momentum = visual.plot_spin_momentum(data)
    fig_orbital_real = visual.plot_orbital_real(data)
    fig_spin_real = visual.plot_spin_real(data)
    fig_spinexchange_momentum = visual.plot_spinexchange_momentum(data)

    # Important: Match x-axes inside the same column
    fig_orbital_momentum.update_layout(xaxis=dict(matches='x2'))
    fig_spin_momentum.update_layout(xaxis=dict(matches='x2'))

    fig_orbital_real.update_layout(xaxis=dict(matches='x4'))
    fig_spin_real.update_layout(xaxis=dict(matches='x4'))

    return fig_orbital_momentum, fig_spin_momentum, fig_orbital_real, fig_spin_real, fig_spinexchange_momentum
