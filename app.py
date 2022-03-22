import dash
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
from dash import dcc
from dash import html

# ------------------------------------------------------------------------------
# Initialise the app
app = dash.Dash(__name__)

# ------------------------------------------------------------------------------
# Import data
df = pd.read_csv('meteorite_landings_cleaned.csv')

# ------------------------------------------------------------------------------
# App layout

# ------------------------------------------------------------------------------
# Connect the Plotly graphs with Dash Components

# ------------------------------------------------------------------------------
if __name__ == '__main__':
    app.run_server(debug=True)