import dash
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
import plotly.graph_objects as go

# ------------------------------------------------------------------------------
mark_values = {900: '900', 1000: '1000', 1100: '1100', 1200: '1200',
               1300: '1300', 1400: '1400', 1500: '1500', 1600: '1600',
               1700: '1700', 1800: '1800', 1900: '1900', 2000: '2000'}

# Initialise the app
app = dash.Dash(__name__)

colors = {
    'background': '#111111',
    'text': '#7FDBFF'
}

# ------------------------------------------------------------------------------
# Import data
df = pd.read_csv('meteorite_landings_cleaned.csv')

# Store MapBox access token
mapbox_access_token = 'pk.eyJ1Ijoic2VyZW5haXZlcyIsImEiOiJjbDEzeDcxemUwNTN0M2Jxem9hbmVtb3RyIn0.K_CZ4pFHTGuZ2mOrCRC89Q'

# ------------------------------------------------------------------------------
# Map


# ------------------------------------------------------------------------------
# App layout
app.layout = html.Div([
    html.Div([
        html.H1(children="Meteorite Landings",
                style={"text-align": "center", "font-size": "200%", "color": "black"})
    ]),

    html.Div([
        dcc.Graph(
            id='map-plot'
        )]),

    html.Div([
        dcc.RangeSlider(
            id='year-slider',
            min=df['year'].min(),
            max=df['year'].max(),
            value=[1813, 2013],  # default range before slider is adjusted
            step=1,
            marks=mark_values,
            allowCross=False,
            verticalHeight=900,
            pushable=True,
            tooltip={'always_visible': True,
                     'placement': 'bottom'}
        )], style={'width': '70%',
                   'position': 'absolute', 'left': '5%'}),
])

# ------------------------------------------------------------------------------
# Connect the Plotly graphs with Dash Components

# filters dataframe based on input from user, which is a tuple (start year, end year) from range slider selection
def get_updated_df(years_selected):
    new_df = df[(df["year"] >= years_selected[0]) & (df["year"] <= years_selected[1])]
    return new_df


# Map
@app.callback(
    Output('map-plot', 'figure'),
    [Input('year-slider', 'value')]
)
def update_map(years_selected):
    new_df = get_updated_df(years_selected)

    trace = [
        dict(
            type="scattermapbox",
            lat=new_df.reclat,
            lon=new_df.reclong,
            text=new_df.name, # add more info to text (i.e include name, year, found/fell)
            hoverinfo='text',
            mode='markers',
            marker=dict(
                size=5,
                color='red',
                opacity=0.4),
        )
    ]

    layout = dict(
        hovermode='closest',
        margin=dict(r=0, l=0, t=0, b=0),
        mapbox=dict(
            accesstoken=mapbox_access_token,
            bearing=0,
            center=dict(
                lat=0,
                lon=0,
            ),
            zoom=0.5,
            style='carto-darkmatter',
        ),
    )
    fig = dict(data=trace, layout=layout)
    return fig

# Line graph

# Density graph

# Pie Chart

# ------------------------------------------------------------------------------
if __name__ == '__main__':
    app.run_server(debug=True)
