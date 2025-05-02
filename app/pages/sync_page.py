import dash
from dash import html, dcc, dash_table, Input, Output, State, callback, ctx
import dash.exceptions
import threading
import time
import socket

from logic.data_loader import load_simulation_metadata, get_files_to_download
from sync.gdrive_sync import start_download_thread, get_progress_log

dash.register_page(__name__, path="/sync", name="Data Sync")


def is_connected(host="127.0.0.1", port=8050, timeout=5):
    """Check internet connection by pinging a DNS server."""
    try:
        socket.setdefaulttimeout(timeout)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
        return True
    except socket.error:
        return False


# === Conditional Layout: Handle Offline Mode ===
if not is_connected():
    layout = html.Div([
        html.H2("📡 Sync Simulation Data"),
        html.Div("🔌 You are offline. Google Drive sync is unavailable.", style={
            "color": "red", "fontWeight": "bold", "marginBottom": "20px"
        }),
        html.P("Reconnect to the internet and reload this page to enable syncing."),
        html.P("You can still use the app with previously downloaded files."),
    ], style={
        "margin": "20px",
        "padding": "10px",
        "boxSizing": "border-box",
    })
else:
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

        dcc.Store(id="missing-files-store"),
        dcc.Store(id="download-progress-store", data=""),

        html.Br(),

        # Button and Status Message on the same row
        html.Div([
            html.Button("Download missing files", id="download-button", n_clicks=0),
            html.Div(id="sync-status", style={"marginLeft": "20px", "display": "inline-block"})
        ], style={"display": "flex", "alignItems": "center"}),

        # Hidden Interval to trigger periodic refresh
        dcc.Interval(id="progress-interval", interval=1000, n_intervals=0, disabled=True)
    ], style={
        "margin": "20px",
        "padding": "10px",
        "boxSizing": "border-box",
    })


# === Callbacks (only registered if online) ===
if is_connected():

    @callback(
        Output("table-container", "children"),
        Output("missing-files-store", "data"),
        Input("check-btn", "n_clicks"),
        State("model-select", "value"),
        State("ion-select", "value"),
    )
    def update_sim_table(n_clicks, model, ion_types):
        if n_clicks == 0:
            return dash.no_update, dash.no_update

        df = load_simulation_metadata(model, force_download=True)
        missing = get_files_to_download(df, ion_types, model)

        if missing.empty:
            return html.P("✅ All files are downloaded for selected ion types."), {}

        common_cols = ["ion_type", "N", "U", "J", "lbd", "g"]
        model_specific = {"lat": ["t"], "ss": ["B"]}
        display_cols = common_cols + model_specific.get(model, [])
        display_cols = [col for col in display_cols if col in missing.columns]

        missing_files_list = missing["filename"].tolist()

        return (
            dash_table.DataTable(
                data=missing[display_cols].to_dict("records"),
                columns=[{"name": col, "id": col} for col in display_cols],
                style_table={"overflowX": "auto"},
                page_size=8,
                style_cell={"textAlign": "center", "padding": "5px", "fontSize": "14px",},
                style_header={"fontWeight": "bold", "backgroundColor": "#f0f0f0"},
            ),
            {"model": model, "filenames": missing_files_list}
        )


    @callback(
        Output('progress-interval', 'disabled'),
        Input('download-button', 'n_clicks'),
        State('missing-files-store', 'data'),
        prevent_initial_call=True,
    )
    def start_download(n_clicks, missing_data):
        if not missing_data:
            raise dash.exceptions.PreventUpdate

        model = missing_data["model"]
        filenames = missing_data["filenames"]

        if not filenames:
            raise dash.exceptions.PreventUpdate

        start_download_thread(model, filenames)

        return False  # Start the interval


    @callback(
        Output('sync-status', 'children'),
        Input('progress-interval', 'n_intervals'),
    )
    def update_progress(n_intervals):
        progress_text = get_progress_log()
        return html.Div(progress_text)
