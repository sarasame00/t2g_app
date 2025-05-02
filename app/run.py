from dash import dcc, html, Dash, Input, Output, page_container
import sys
from pathlib import Path
import dash_bootstrap_components as dbc
import os
import multiprocessing


def resource_path(relative_path):
    """Get absolute path to resource, works for PyInstaller and dev."""
    if hasattr(sys, '_MEIPASS'):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


# Add project root to sys.path so that imports from parent directory work
sys.path.append(str(Path(__file__).resolve().parents[1]))

pages_path = resource_path("pages")
assets_path = resource_path("assets")

print("💡 Looking for pages folder at:", pages_path)
print("📁 Contents of dist directory:", os.listdir(os.path.dirname(pages_path)))
print("📁 Contents of pages_path:", os.listdir(pages_path) if os.path.exists(pages_path) else "❌ NOT FOUND")

# Initialize the Dash app with Bootstrap theme for styling
app = Dash(
    __name__,
    assets_folder=assets_path,
    pages_folder=pages_path,
    use_pages=True,
    external_stylesheets=[dbc.themes.FLATLY],
    serve_locally=True
)

# Customize the default HTML template to remove margins, paddings, and hide scrollbars
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

# Define the overall layout of the app
app.layout = html.Div([
    dcc.Location(id="url"),
    html.Div(id="navbar"),
    page_container
], style={
    "margin": "20px",
    "padding": "10px",
    "boxSizing": "border-box",
    "minHeight": "100vh",
    "overflow": "hidden",
})


@app.callback(
    Output("navbar", "children"),
    Input("url", "pathname")
)
def update_navbar(pathname):
    """Update the navigation bar links based on the current page path."""
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
                "color": "black" if is_active else "grey",
            }
        )

    links.append(make_link("Single-site model", "/"))
    links.append(make_link("Lattice model", "/lat_t"))
    links.append(make_link("Sync Page", "/sync"))

    return html.Div([
        html.Img(
            src=app.get_asset_url("icon.png"),
            style={"height": "30px", "marginRight": "15px"}
        ),
        html.Span("T2g App", style={
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


if __name__ == "__main__":
    multiprocessing.freeze_support() 
    try:
        app.run(
            host="127.0.0.1",
            port=8050,
            debug=False
        )
    except Exception as e:
        print(f"❌ Failed to start the app: {e}")
