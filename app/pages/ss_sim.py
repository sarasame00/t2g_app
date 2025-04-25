import numpy as np
import plotly.express as px
from dash import dcc, html, Input, Output, callback, register_page
from matplotlib.colors import LinearSegmentedColormap, to_hex

from logic.data_loader import load_filtered_metadata


# === CONFIG ===
shape = (101, 101)  # Shape of the energy maps
model = "ss"

# === Load filtered metadata
df, DATA_DIR = load_filtered_metadata(model)

# === Prepare dropdowns ===
param_names = ["N", "U", "J", "g", "lbd", "B"]
param_values = {
    param: sorted(df[param].unique()) for param in param_names
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
    html.H2("Single-site Simulation Viewer"),

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
            dcc.Graph(id="energy-map", style={"height": "100%", "width": "100%"})
        ], style={"width": "67%", "padding": "15px"})
    ], style={"display": "flex", "flexDirection": "row"})
])


@callback(
    Output("energy-map", "figure"),
    [Input(f"dropdown-{param}", "value") for param in param_names]
)
def update_figure(N, U, J, g, lbd, B):
    match = df[
        (df["N"] == N) & (df["U"] == U) & (df["J"] == J) &
        (df["g"] == g) & (df["B"] == B) & (df["lbd"] == lbd)
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
        title=f"Ground State Energy — N={N}, U={U}, J={J}, g={g}, B={B}, λ={lbd}",
        transition_duration=300
    )
    return fig
