import dash
from dash import html, dcc, dash_table, Input, Output, State, callback, ctx
import dash.exceptions
import threading
import time
import socket

from logic.data_loader import load_simulation_metadata, get_files_to_download
from sync.gdrive_sync import start_download_thread, get_progress_log

# Register sync page in Dash app routing
# Path: /sync | Page Name: Data Sync
dash.register_page(__name__, path="/sync", name="Data Sync")

def is_connected(host="8.8.8.8", port=53, timeout=3):
    """Check internet connection by attempting a connection to a public DNS.

    Parameters
    ----------
    host : str
        Host to test connection with.
    port : int
        Port to test.
    timeout : int
        Timeout duration in seconds.

    Returns
    -------
    bool
        True if connection is successful, False otherwise.
    """
    try:
        socket.setdefaulttimeout(timeout)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
        return True
    except socket.error:
        return False


# === Layout Definition ===

# Offline Mode Layout
if not is_connected():
    layout = html.Div([
        html.H2("📡 Sync Simulation Data"),
        html.Div("🔌 You are offline. Google Drive sync is unavailable.", style={
            "color": "red", "fontWeight": "bold", "marginBottom": "20px"
        }),
        html.P("Reconnect to the internet and reload this page to enable syncing."),
        html.P("You can still use the app with previously downloaded files."),
    ], style={"margin": "20px", "padding": "10px", "boxSizing": "border-box"})

# Online Mode Layout
else:
    layout = html.Div([
        html.H2("📡 Sync Simulation Data"),
        html.Label("Select Model"),
        dcc.Dropdown(["lat", "ss"], id="model-select", value="lat"),

        html.Label("Select Ion Types"),
        dcc.Checklist(["3d_d1", "4d_d1", "5d_d1", "3d_d2", "4d_d2", "5d_d2"], id="ion-select", value=["3d_d1"]),

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

        html.Div([
            html.Button("Download missing files", id="download-button", n_clicks=0),
            html.Div(id="sync-status", style={"marginLeft": "20px", "display": "inline-block"})
        ], style={"display": "flex", "alignItems": "center"}),

        dcc.Interval(id="progress-interval", interval=1000, n_intervals=0, disabled=True)
    ], style={"margin": "20px", "padding": "10px", "boxSizing": "border-box"})


# === Callbacks ===
if is_connected():

    @callback(
        Output("table-container", "children"),
        Output("missing-files-store", "data"),
        Input("check-btn", "n_clicks"),
        State("model-select", "value"),
        State("ion-select", "value"),
    )
    def update_sim_table(n_clicks, model, ion_types):
        """Display missing simulations in a table after user checks availability.

        Parameters
        ----------
        n_clicks : int
            Number of times the check button was clicked.
        model : str
            Selected model ('lat' or 'ss').
        ion_types : list
            Selected ion types.

        Returns
        -------
        component, dict
            Dash DataTable showing missing files and metadata for download.
        """
        if n_clicks == 0:
            return dash.no_update, dash.no_update

        df = load_simulation_metadata(model, force_download=True)
        missing = get_files_to_download(df, ion_types, model)

        if missing.empty:
            return html.P("✅ All files are downloaded for selected ion types."), {}

        common_cols = ["ion_type", "N", "U", "J", "lbd", "g"]
        model_specific = {"lat": ["t"], "ss": ["B"]}
        display_cols = [col for col in common_cols + model_specific.get(model, []) if col in missing.columns]

        return (
            dash_table.DataTable(
                data=missing[display_cols].to_dict("records"),
                columns=[{"name": col, "id": col} for col in display_cols],
                style_table={"overflowX": "auto"},
                page_size=8,
                style_cell={"textAlign": "center", "padding": "5px", "fontSize": "14px"},
                style_header={"fontWeight": "bold", "backgroundColor": "#f0f0f0"}
            ),
            {"model": model, "filenames": missing["filename"].tolist()}
        )


    @callback(
        Output('progress-interval', 'disabled'),
        Input('download-button', 'n_clicks'),
        State('missing-files-store', 'data'),
        prevent_initial_call=True
    )
    def start_download(n_clicks, missing_data):
        """Start background thread to download missing files.

        Parameters
        ----------
        n_clicks : int
            Clicks on the download button.
        missing_data : dict
            Model and list of filenames to download.

        Returns
        -------
        bool
            Whether to enable periodic progress updates.
        """
        if not missing_data:
            raise dash.exceptions.PreventUpdate

        model = missing_data["model"]
        filenames = missing_data["filenames"]

        if not filenames:
            raise dash.exceptions.PreventUpdate

        start_download_thread(model, filenames)
        return False


    @callback(
        Output('sync-status', 'children'),
        Input('progress-interval', 'n_intervals')
    )
    def update_progress(n_intervals):
        """Update status message with download progress.

        Parameters
        ----------
        n_intervals : int
            Number of interval ticks since start.

        Returns
        -------
        html.Div
            Component with current download status.
        """
        progress_text = get_progress_log()
        return html.Div(progress_text)
