import dash
from dash import html
import dash_bootstrap_components as dbc

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

app.layout = html.Div([
    dbc.Card(
        dbc.CardBody([
            html.H4("Card Title", className="card-title"),
            html.P("This is some card content.", className="card-text"),
        ])
    )
])

if __name__ == '__main__':
    app.run_server(debug=True)