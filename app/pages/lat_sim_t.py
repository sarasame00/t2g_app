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

# Map internal param names to display labels
param_labels = {
    "U": "U (eV)",
    "J": "J (eV)",
    "g": "g (eV)",
    "t": "t (eV)",
    "lbd": "ξ (eV)"
}



# === Page registration
register_page(__name__, path='/lat_t', name='Lattice model (function of t) ')

# === Layout
layout = html.Div([
    html.H2("Lattice Model"),

    html.Div([
        # Sidebar
        html.Div([
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

        # Plot Area
        html.Div([
            dbc.Container([
                # First row: 3 plots
                dbc.Row([
                    dbc.Col(dcc.Graph(id="t-plot-1", style={"height": "35vh"}), width=4),
                    dbc.Col(dcc.Graph(id="t-plot-3", style={"height": "35vh"}), width=4),
                    dbc.Col(dcc.Graph(id="t-plot-5", style={"height": "35vh"}), width=4),
                ]),

                # Second row: 2 plots (leave third empty)
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





# === Callbacks

@callback(
    [Output(f"t-dropdown-{param}", "options") for param in param_names] +
    [Output(f"t-dropdown-{param}", "value") for param in param_names],
    Input("ion-type-dropdown-lat-t", "value")
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

    default_values = [
    param_values[param][0] if param != "t" else [param_values[param][0]]
    for param in param_names
]


    return options + default_values

@callback(
    Output("t-plot-1", "figure"),
    Output("t-plot-2", "figure"),
    Output("t-plot-3", "figure"),
    Output("t-plot-4", "figure"),
    Output("t-plot-5", "figure"),
    Output("legend-div", "children"),
    [Input("ion-type-dropdown-lat-t", "value")] + [Input(f"t-dropdown-{param}", "value") for param in param_names]
)
def update_lat_plots(selected_ion_type, U, J, g, t_list, lbd):
    if not selected_ion_type:
        empty_fig = visual.empty_plot(message="❌ Select an ion type")
        return empty_fig, empty_fig, empty_fig, empty_fig, empty_fig

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


    fig_orbital_momentum = visual.plot_orbital_momentum(data_list, t_values)
    fig_spin_momentum = visual.plot_spin_momentum(data_list, t_values)
    fig_orbital_real = visual.plot_orbital_real(data_list, t_values)
    fig_spin_real = visual.plot_spin_real(data_list, t_values)
    fig_nearest_neighbor = visual.plot_nn_correlation_vs_t(data_list, t_values)
    legend_html = visual.build_custom_legend(t_values)


    return fig_orbital_momentum, fig_spin_momentum, fig_orbital_real, fig_spin_real, fig_nearest_neighbor, legend_html
