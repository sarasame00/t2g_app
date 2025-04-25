from dash import dcc, Dash, html, page_container
import sys
from pathlib import Path

# Add project root to sys.path
sys.path.append(str(Path(__file__).resolve().parents[1]))

app = Dash(__name__, use_pages=True)

app.layout = html.Div([
    html.Div([
        dcc.Link("Single-site model", href="/ss"),
        html.Span(" | "),
        dcc.Link("Lattice model", href="/lat"),
        html.Span(" | "),
        dcc.Link("Sync Page", href="/sync")
    ], style={"marginBottom": "30px"}),  

    page_container
])

if __name__ == "__main__":
    print("🚀 Launching app on http://127.0.0.1:8050")
    app.run(debug=True)
