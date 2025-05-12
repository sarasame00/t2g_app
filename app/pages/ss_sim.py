import numpy as np
import plotly.express as px
from dash import dcc, html, Input, Output, callback, register_page
from matplotlib.colors import LinearSegmentedColormap, to_hex

from logic.data_loader import load_cached_filtered_metadata
from sync.config import LOCAL_DATA_FOLDER
from plots.visualize import empty_plot

# === CONFIGURATION ===
shape = (101, 101)  # Shape of the energy maps
model = "ss"        # Model type (single-site)

# Load filtered metadata
df, _ = load_cached_filtered_metadata(model)
DATA_DIR = LOCAL_DATA_FOLDER / f"{model}_data"

# === Prepare dropdowns: collect available parameter values
param_names = ["U", "J", "g", "lbd", "B"]
param_values = {param: sorted(df[param].unique()) for param in param_names}

# Human-readable labels for the UI
param_labels = {
    "U": "U (eV)",
    "J": "J (eV)",
    "g": "g (eV)",
    "B": "B (eV)",
    "lbd": "ξ (eV)"
}

# === Custom color map for energy plots ===
colors = [
    (0.0, "black"), (0.15, "yellow"), (0.25, "orange"), (0.35, "red"),
    (0.5, "magenta"), (0.65, "blue"), (0.85, "cyan"), (1.0, "white")
]
custom_cmap = LinearSegmentedColormap.from_list("custom_map", colors)
plotly_colorscale = [(i / 254, to_hex(custom_cmap(i / 254))) for i in range(255)]

# === Dash Page Setup ===
register_page(__name__, path='/', name='Single-site model')

layout = html.Div([
    html.Div([
        html.H2("Single-site Model"),
        html.Div([
            dcc.Loading(
                id="loading-energy-map",
                type="circle",
                children=[dcc.Graph(id="energy-map", style={"height": "100%", "width": "100%"})]
            )
        ])
    ], style={
        "marginLeft": "290px",
        "padding": "15px",
        "overflow": "hidden",
        "height": "calc(100vh - 100px)"
    }),

    # === Sidebar ===
    html.Div([
        dcc.Store(id="ss-fixed-colorbar", storage_type="memory"),

        html.Label("Colorbar Mode:"),
        dcc.RadioItems(
            id="colorbar-mode-toggle",
            options=[
                {"label": "Auto", "value": "auto"},
                {"label": "Fixed", "value": "fixed"}
            ],
            value="auto",
            inline=True,
            style={"marginBottom": "20px"},
            labelStyle={"marginRight": "15px"}
        ),

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
    [Output(f"ss-dropdown-{param}", "options") for param in param_names] +
    [Output(f"ss-dropdown-{param}", "value") for param in param_names],
    Input("ion-type-dropdown-ss", "value")
)
def initialize_dropdowns(selected_ion_type):
    """Initialize dropdowns for parameters based on selected ion type.

    Parameters
    ----------
    selected_ion_type : str
        Ion type selected by the user.

    Returns
    -------
    list
        Dropdown options and default selected values for each parameter.
    """
    if not selected_ion_type:
        return [[] for _ in param_names * 2]

    filtered_df = df[df['ion_type'] == selected_ion_type]

    param_values = {
        param: sorted(filtered_df[param].unique())
        for param in param_names
    }

    options = []
    default_values = []

    for param in param_names:
        clean_vals = [
            float(v) for v in param_values[param]
            if isinstance(v, (int, float, np.number)) or (isinstance(v, str) and v.replace('.', '', 1).isdigit())
        ]
        opts = [{"label": f"{v:.3f}", "value": v} for v in clean_vals]
        options.append(opts)
        default_values.append(clean_vals[0] if clean_vals else None)

    return options + default_values


@callback(
    Output("ss-fixed-colorbar", "data"),
    Input("ion-type-dropdown-ss", "value")
)
def compute_fixed_zrange(selected_ion_type):
    """Compute fixed z-axis range for consistent colorbars.

    Parameters
    ----------
    selected_ion_type : str
        The selected ion type.

    Returns
    -------
    dict
        Dictionary with min and max z-values across all relevant data.
    """
    if not selected_ion_type:
        return {}

    filtered_df = df[df['ion_type'] == selected_ion_type]
    zmins, zmaxs = [], []

    for _, row in filtered_df.iterrows():
        file_path = DATA_DIR / row["filename"]
        if not file_path.exists():
            continue
        try:
            data = np.loadtxt(file_path)
            if data.size == 0:
                continue
            emap = data[:, 2].reshape(shape)
            zmins.append(np.min(emap))
            zmaxs.append(np.max(emap))
        except Exception:
            continue

    if not zmins or not zmaxs:
        return {}

    return {"zmin": min(zmins), "zmax": max(zmaxs)}


@callback(
    Output("energy-map", "figure"),
    Input("ion-type-dropdown-ss", "value"),
    Input("colorbar-mode-toggle", "value"),
    Input("ss-fixed-colorbar", "data"),
    *[Input(f"ss-dropdown-{param}", "value") for param in param_names]
)
def update_figure(selected_ion_type, colorbar_mode, fixed_zrange, U, J, g, lbd, B):
    """Update energy map figure based on user selections.

    Parameters
    ----------
    selected_ion_type : str
        Ion type selected.
    colorbar_mode : str
        Mode for color scaling ('auto' or 'fixed').
    fixed_zrange : dict
        Precomputed z-range for fixed color scaling.
    U, J, g, lbd, B : float
        Physical parameters used to filter the data.

    Returns
    -------
    plotly.graph_objects.Figure
        A heatmap visualization of the energy data.
    """
    if not selected_ion_type:
        return empty_plot("❌ Select an ion type")

    filtered_df = df[df['ion_type'] == selected_ion_type]
    match = filtered_df[
        (filtered_df["N"] == 1) &
        np.isclose(filtered_df["U"], U) &
        np.isclose(filtered_df["J"], J) &
        np.isclose(filtered_df["g"], g) &
        np.isclose(filtered_df["B"], B) &
        np.isclose(filtered_df["lbd"], lbd)
    ]

    if match.empty:
        return empty_plot("❌ No matching simulation found")

    file_path = DATA_DIR / match.iloc[-1]["filename"]

    try:
        data = np.loadtxt(file_path)
        emap = data[:, 2].reshape(shape)
        if colorbar_mode == "fixed" and fixed_zrange:
            zmin, zmax = fixed_zrange["zmin"], fixed_zrange["zmax"]
        else:
            zmin = np.min(emap)
            zmax = zmin + (np.max(emap) - zmin) * 1.0
    except Exception as e:
        print(f"❌ Error loading or reshaping data: {e}")
        return empty_plot("❌ Error loading simulation")

    fig = px.imshow(
        emap,
        color_continuous_scale=plotly_colorscale,
        zmin=zmin,
        zmax=zmax
    )
    fig.update_layout(transition_duration=300)
    return fig
