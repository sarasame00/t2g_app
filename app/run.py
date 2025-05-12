from dash import dcc, html, Dash, Input, Output, page_container
import sys
from pathlib import Path
import dash_bootstrap_components as dbc

# Add project root to sys.path to allow top-level imports
sys.path.append(str(Path(__file__).resolve().parents[1]))

# === Initialize Dash App ===
app = Dash(
    __name__,
    use_pages=True,
    external_stylesheets=[dbc.themes.FLATLY],
    serve_locally=True
)

# === Customize HTML Template (no scrollbars, no margins) ===
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
        <style>
            html, body {
                margin: 0;
                padding: 0;
                overflow: hidden;
                height: 100%;
            }
        </style>
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''

# === App Layout ===
app.layout = html.Div([
    dcc.Location(id="url"),       # Tracks current URL
    html.Div(id="navbar"),        # Navigation bar (dynamic)
    page_container                 # Page content loaded by Dash Pages
], style={
    "margin": "20px",
    "padding": "10px",
    "boxSizing": "border-box",
    "minHeight": "100vh",
    "overflow": "hidden",
})


# === Navigation Bar Callback ===
@app.callback(
    Output("navbar", "children"),
    Input("url", "pathname")
)
def update_navbar(pathname):
    """Update the navigation bar based on the current page.

    Parameters
    ----------
    pathname : str
        The current URL path

    Returns
    -------
    html.Div
        Navigation links and branding
    """
    links = []

    if pathname is None:
        pathname = "/"

    def make_link(name, href):
        is_active = pathname == href
        return dcc.Link(
            name,
            href=href,
            style={
                "marginRight": "20px",
                "fontSize": "20px",
                "fontWeight": "bold" if is_active else "normal",
                "textDecoration": "underline" if is_active else "none",
                "color": "black" if is_active else "grey"
            }
        )

    links.append(make_link("Single-site model", "/"))
    links.append(make_link("Lattice model", "/lat_t"))
    links.append(make_link("Sync Page", "/sync"))  # Optional link

    return html.Div([
        html.Img(
            src=app.get_asset_url("icon.png"),
            style={"height": "30px", "marginRight": "5px", "marginLight": "15px"}
        ),
        html.Span("T2g App  ", style={
            "fontWeight": "bold",
            "fontSize": "24px",
            "marginRight": "85px"
        }),
        *links
    ], style={
        "display": "flex",
        "alignItems": "center",
        "gap": "20px",
        "marginBottom": "30px"
    })


# === Expose Server ===
server = app.server


# === Run App (for local dev) ===
if __name__ == "__main__":
    try:
        app.run(
            host="127.0.0.1",
            port=8050,
            debug=True
        )
    except Exception as e:
        print(f"Failed to start the app: {e}")
