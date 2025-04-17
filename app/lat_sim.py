from dash import html, register_page

register_page(__name__, path='/new', name='Lattice model')

layout = html.Div([
    html.H1("Lattice model"),
    html.P("This will show your other simulation.")
])
