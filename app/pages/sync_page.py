import dash
from dash import html,ctx, dcc, dash_table, Input, Output, State, callback
from dash.exceptions import PreventUpdate

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
    dcc.Loading(
        id="loading-check",
        type="circle",  
        children=html.Div(id="table-container")
    ),


    html.Br(),
    html.Button("⬇️ Download Missing Files", id="download-btn", n_clicks=0),
    dcc.Loading(
        id="loading-download",
        type="circle",
        children=html.Div([
            html.Div(id="download-output"),
            html.Div(id="download-status"),
        ])
    ),

    dcc.Interval(id="download-interval", interval=1000, n_intervals=0, disabled=True),
    dcc.Store(id="files-to-download"),
    dcc.Store(id="download-progress", data={"index": 0}),
    dcc.Interval(id="clear-status-interval", interval=3000, n_intervals=0, disabled=True),


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

    common_cols = ["ion_type", "N", "U", "J", "lbd", "g"]
    model_specific = {"lat": ["t"], "ss": ["B"]}
    display_cols = common_cols + model_specific.get(model, [])
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
    Output("files-to-download", "data"),
    Output("download-progress", "data"),
    Output("download-output", "children"),
    Output("download-status", "children"),
    Output("download-interval", "disabled"),
    Output("clear-status-interval", "disabled"),
    Input("download-btn", "n_clicks"),
    Input("download-interval", "n_intervals"),
    Input("clear-status-interval", "n_intervals"),
    State("model-select", "value"),
    State("ion-select", "value"),
    State("files-to-download", "data"),
    State("download-progress", "data"),
)
def manage_download(n_clicks, download_tick, clear_tick, model, ion_types, filenames, progress):
    triggered_id = ctx.triggered_id

    if triggered_id == "download-btn":
        if not n_clicks:
            raise PreventUpdate

        df = load_simulation_metadata(model)
        missing = get_files_to_download(df, ion_types, model)
        filenames = missing["filename"].tolist()

        if not filenames:
            return [], {"index": 0}, "", "✅ Nothing to download.", True, False

        return filenames, {"index": 0}, "", f"Preparing to download {len(filenames)} files...", False, True


    elif triggered_id == "download-interval":
        if not filenames:
            raise PreventUpdate

        index = progress["index"]

        # ✅ Check for completion BEFORE downloading
        if index >= len(filenames):
            return filenames, progress, dash.no_update, "✅ Download complete.", True

        filename = filenames[index]
        print(f"⬇️ Downloading file {index+1}/{len(filenames)}: {filename}")
        download_files_from_drive([filename], model)

        new_index = index + 1

        # ✅ If that was the last file, we also end it right here
        if new_index >= len(filenames):
            return filenames, {"index": new_index}, dash.no_update, "✅ Download complete.", True, False

        status = f"⬇️ Downloaded {new_index}/{len(filenames)} file(s)..."
        return filenames, {"index": new_index}, dash.no_update, status, False, True

    if triggered_id == "clear-status-interval":
        return dash.no_update, dash.no_update, dash.no_update, "", dash.no_update, True


    raise PreventUpdate
