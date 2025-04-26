from dash import dcc, Dash, html, page_container
import sys
from pathlib import Path
import dash_bootstrap_components as dbc

# Add project root to sys.path
sys.path.append(str(Path(__file__).resolve().parents[1]))

app = Dash(__name__, use_pages=True, external_stylesheets=[dbc.themes.FLATLY])

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
app.layout = html.Div([
    html.Div([
        dcc.Link("Single-site model", href="/ss"),
        html.Span(" | "),
        dcc.Link("Lattice model", href="/lat"),
        html.Span(" | "),
        dcc.Link("Sync Page", href="/sync")
    ], style={"marginBottom": "30px"}),  

    page_container
], style={
    "margin": "20px",    
    "padding": "10px",   
    "boxSizing": "border-box",
    "minHeight": "100vh",  
    "overflow": "hidden"   # prevent scrolling
})

if __name__ == "__main__":
    app.run(debug=True)
