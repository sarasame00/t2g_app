from dash import Dash, html, dcc, page_container

app = Dash(__name__, use_pages=True, pages_folder="app")


app.layout = html.Div([
    html.H1("T2G App"),
    html.Div([
        dcc.Link("Single-site model", href="/"),
        html.Span(" | "),
        dcc.Link("Lattice model", href="/new")
    ], style={"marginBottom": "30px"}),
    page_container
])

if __name__ == "__main__":
    app.run(debug=True)
