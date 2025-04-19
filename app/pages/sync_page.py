import dash
from dash import html, dcc, dash_table, Input, Output, State, callback

from logic.data_loader import load_simulation_metadata, get_files_to_download
from sync.gdrive_sync import download_files_from_drive


dash.register_page(__name__, path="/sync", name="Data Sync")

layout = html.Div([
    html.H2("📡 Sync Simulation Data"),
    html.Label("Select Model"),
    dcc.Dropdown(["lat", "ss"], id="model-select", value="lat"),

    html.Label("Select Ion Types"),
    dcc.Checklist(["3d_d1", "4d_d1", "5d_d1"], id="ion-select", value=["3d_d1"]),

    html.Br(),
    html.Button("🔍 Check Available Simulations", id="check-btn", n_clicks=0),

    html.Div(id="table-container"),

    html.Br(),
    html.Button("⬇️ Download Missing Files", id="download-btn", n_clicks=0),

    html.Div(id="download-output")
])

@callback(
    Output("table-container", "children"),
    Input("check-btn", "n_clicks"),
    State("model-select", "value"),
    State("ion-select", "value"),
)
def update_sim_table(n_clicks, model, ion_types):
    if n_clicks == 0:
        return dash.no_update

    df = load_simulation_metadata(model)
    missing = get_files_to_download(df, ion_types, model)

    if missing.empty:
        return html.P("✅ All files are downloaded for selected ion types.")

    # Explicit parameter columns based on model
    common_cols = ["ion_type", "N", "U", "J", "lbd", "g"]
    model_specific = {"lat": ["t"], "ss": ["B"]}
    display_cols = common_cols + model_specific.get(model, [])

    # Only keep those columns if they exist in the dataframe
    display_cols = [col for col in display_cols if col in missing.columns]

    return dash_table.DataTable(
        data=missing[display_cols].to_dict("records"),
        columns=[{"name": col, "id": col} for col in display_cols],
        style_table={"overflowX": "auto"},
        page_size=10,
        style_cell={"textAlign": "center", "padding": "5px"},
        style_header={"fontWeight": "bold", "backgroundColor": "#f0f0f0"},
    )


@callback(
    Output("download-output", "children"),
    Input("download-btn", "n_clicks"),
    State("model-select", "value"),
    State("ion-select", "value"),
)
def handle_download(n_clicks, model, ion_types):
    if n_clicks == 0:
        return dash.no_update

    df = load_simulation_metadata(model)
    missing = get_files_to_download(df, ion_types, model)
    filenames = missing["filename"].tolist()

    if not filenames:
        return "✅ Nothing to download."

    download_files_from_drive(filenames, model)
    return f"⬇️ Downloaded {len(filenames)} file(s)."
