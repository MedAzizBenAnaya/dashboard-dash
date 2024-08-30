from dash import Dash, dcc, html
import dash_bootstrap_components as dbc
from flask import Flask, session
from layouts import Layouts
from authentication import Auth
from callbacks import register_callbacks

# Initialize Flask server
server = Flask(__name__)
server.secret_key = 'BB'

# Initialize Dash app
app = Dash(__name__, server=server, external_stylesheets=[dbc.themes.BOOTSTRAP, '/assets/custom.css'],
           suppress_callback_exceptions=True)

# Instantiate the layout and authentication classes
layouts = Layouts()

# layouts.fetch_data()

auth = Auth()

# Main layout with conditional navbar
app.layout = html.Div([
    dcc.Location(id="url"),
    html.Div(id="navbar-container"),
    html.Div(id="page-content"),
    dcc.Store(id='stored-figure-data', storage_type='memory')

])

# Register callbacks
register_callbacks(app, layouts, auth)

if __name__ == "__main__":
    app.run_server(debug=True)
