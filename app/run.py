from dash import dcc, html, Dash, Input, Output, page_container
import sys
from pathlib import Path
import dash_bootstrap_components as dbc

# Add project root to sys.path so that imports from parent directory work
sys.path.append(str(Path(__file__).resolve().parents[1]))

# Initialize the Dash app with Bootstrap theme for styling
app = Dash(
    __name__,
    use_pages=True,
    external_stylesheets=[dbc.themes.FLATLY],
    serve_locally=True  # ✅ Ensures local JS/CSS
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
    dcc.Location(id="url"),  # Component to track the current page URL
    html.Div(id="navbar"),   # Placeholder for the navigation bar (will be updated dynamically)
    page_container           # Placeholder for page-specific content loaded by Dash Pages
], style={
    "margin": "20px",
    "padding": "10px",
    "boxSizing": "border-box",
    "minHeight": "100vh",
    "overflow": "hidden",
})

# Define callback to update the navigation bar based on the current page
@app.callback(
    Output("navbar", "children"),  # Output: Replace the children of the navbar div
    Input("url", "pathname")        # Input: Trigger when URL path changes
)
def update_navbar(pathname):
    """Update the navigation bar links based on the current page path."""
    links = []

    # Handle case where pathname is None
    if pathname is None:
        pathname = "/"  # Default to home page if no path detected

    # Helper function to create navigation links with dynamic styling
    def make_link(name, href):
        is_active = pathname == href  # Determine if link is the current page
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

    # Create links for different pages
    links.append(make_link("Single-site model", "/"))
    links.append(make_link("Lattice model", "/lat_t"))
    links.append(make_link("Sync Page", "/sync"))

    # Return all links wrapped inside a Div
    return html.Div(
    [
        html.Img(
            src=app.get_asset_url("icon.png"),   # safest way
            style={"height": "30px", "marginRight": "5px", "marginLight": "15px"}
        ),
        html.Span("T2g App  ", style={
            "fontWeight": "bold",
            "fontSize": "24px",
            "marginRight": "85px"
        }),
        *links
    ],
    style={
        "display": "flex",
        "alignItems": "center",
        "gap": "20px",
        "marginBottom": "30px"
    }
)

server = app.server

# Run the Dash app (only if this file is executed directly)
if __name__ == "__main__":
    try:
        app.run(
        host="127.0.0.1",
        port=8050,     # Dash server runs here
        debug=True,
    )
    except Exception as e:
        print(f"Failed to start the app: {e}")
