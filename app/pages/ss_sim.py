import numpy as np
import plotly.express as px
from dash import dcc, html, Input, Output, callback, register_page
from matplotlib.colors import LinearSegmentedColormap, to_hex

from logic.data_loader import load_filtered_metadata
from logic.inference import infer_ion_type 

# === CONFIG ===
shape = (101, 101)  # Shape of the energy maps
model = "ss"

# === Load filtered metadata
df, DATA_DIR = load_filtered_metadata(model)

# === Infer Ion Type Column
df['ion_type'] = df.apply(infer_ion_type, axis=1)

# === Prepare dropdowns
param_names = ["U", "J", "g", "lbd", "B"]  # N is now FIXED per ion type
param_values = {param: sorted(df[param].unique()) for param in param_names}

# Map internal param names to display labels
param_labels = {
    "U": "U (eV)",
    "J": "J (eV)",
    "g": "g (eV)",
    "B": "B (eV)",
    "lbd": "ξ (eV)"
}

# === Custom colormap
colors = [
    (0.0, "black"), (0.15, "yellow"), (0.25, "orange"), (0.35, "red"),
    (0.5, "magenta"), (0.65, "blue"), (0.85, "cyan"), (1.0, "white")
]
custom_cmap = LinearSegmentedColormap.from_list("custom_map", colors)
plotly_colorscale = [(i / 254, to_hex(custom_cmap(i / 254))) for i in range(255)]

# === Dash Page Setup
register_page(__name__, path='/ss', name='Single-site model')

layout = html.Div([
    html.H2("Single-site Model"),

    html.Div([
        # Sidebar
        html.Div([
            html.H4("Parameters"),
            html.Label("Select Ion Type:"),
            dcc.Dropdown(
                id="ion-type-dropdown-ss",
                options=[{'label': ion, 'value': ion} for ion in sorted(df['ion_type'].unique())],
                placeholder="Select an ion type",
                value="3d_d1",
                clearable=False,
                style={"marginBottom": "25px", "width": "100%"}
            ),
            dcc.Store(id="ss-initializer", data={}, storage_type='memory'),
            dcc.Loading(
                id="loading-dropdowns-ss",
                type="dot",
                children=[
                    html.Div([
                        html.Label(param_labels.get(param, param)),
                        dcc.Dropdown(id=f"ss-dropdown-{param}", clearable=False, style={"width": "100%"})
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
            dcc.Loading(
                id="loading-energy-map",
                type="circle",
                fullscreen=False,
                children=[
                    dcc.Graph(id="energy-map", style={"height": "100%", "width": "100%"})
                ]
            )
        ], style={"width": "75%", "padding": "15px"})

    ], style={"display": "flex", "flexDirection": "row"})
], style={
    "margin": "20px",   
    "padding": "10px",   
    "boxSizing": "border-box",
    "overflow": "hidden" 
})

@callback(
    [Output(f"ss-dropdown-{param}", "options") for param in param_names] +
    [Output(f"ss-dropdown-{param}", "value") for param in param_names],
    Input("ion-type-dropdown-ss", "value")
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
    Output("energy-map", "figure"),
    [Input("ion-type-dropdown-ss", "value")] +
    [Input(f"ss-dropdown-{param}", "value") for param in param_names]
)
def update_figure(selected_ion_type, U, J, g, lbd, B):
    if not selected_ion_type:
        fig = px.imshow(np.zeros(shape), color_continuous_scale=plotly_colorscale)
        fig.update_layout(title="❌ Select an ion type")
        return fig

    filtered_df = df[df['ion_type'] == selected_ion_type]

    # Fix N automatically by ion type (it is always N=1 here)
    match = filtered_df[
        (filtered_df["N"] == 1) &
        np.isclose(filtered_df["U"], U) &
        np.isclose(filtered_df["J"], J) &
        np.isclose(filtered_df["g"], g) &
        np.isclose(filtered_df["B"], B) &
        np.isclose(filtered_df["lbd"], lbd)
    ]

    if match.empty:
        fig = px.imshow(np.zeros(shape), color_continuous_scale=plotly_colorscale)
        fig.update_layout(title="❌ No matching simulation found")
        return fig

    filename = match.iloc[0]["filename"]
    file_path = DATA_DIR / filename

    try:
        data = np.loadtxt(file_path)
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
        transition_duration=300
    )
    return fig
