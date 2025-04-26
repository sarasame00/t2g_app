from dash import dcc, html, Dash, Input, Output, page_container
import sys
from pathlib import Path
import dash_bootstrap_components as dbc

# Add project root to sys.path
sys.path.append(str(Path(__file__).resolve().parents[1]))

# Create Dash app
app = Dash(__name__, use_pages=True, external_stylesheets=[dbc.themes.FLATLY])

# Fix body margins and scrolling
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

# Layout
app.layout = html.Div([
    dcc.Location(id="url"),  # Track current page

    html.Div(id="navbar"),   # Navbar will be built dynamically

    page_container           # Page content
], style={
    "margin": "20px",
    "padding": "10px",
    "boxSizing": "border-box",
    "minHeight": "100vh",
    "overflow": "hidden"
})

# Callback to update navigation menu
@app.callback(
    Output("navbar", "children"),
    Input("url", "pathname")
)
def update_navbar(pathname):
    links = []

    def make_link(name, href):
        is_active = pathname == href
        return dcc.Link(
            name,
            href=href,
            style={
                "marginRight": "20px",
                "fontSize": "20px",              # <-- Bigger font
                "fontWeight": "bold" if is_active else "normal",  # <-- Bold if active
                "textDecoration": "underline" if is_active else "none",  # <-- Underline if active
                "color": "black" if is_active else "grey",  # <-- Color based on active
            }
        )

    links.append(make_link("Single-site model", "/ss"))
    links.append(make_link("Lattice model", "/lat"))
    links.append(make_link("Sync Page", "/sync"))

    return html.Div(links, style={"marginBottom": "30px"})

# Run app
if __name__ == "__main__":
    app.run(debug=True)
