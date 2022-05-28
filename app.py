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
        dcc.Graph(
            id='bar-graph')]),

    html.Div([
        dcc.RangeSlider(
            id='year-slider',
            min=df['year'].min(),
            max=df['year'].max(),
            value=[1600, 2013],  # default range
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

# Define functions used in ___

# filters dataframe based on input from user, which is a tuple (start year, end year) from range slider selection
# ADD FOUND/ FELL FILTER TO THIS FUNCTION
def get_filtered_df(years_selected):
    filtered_df = df[(df["year"] >= years_selected[0]) & (df["year"] <= years_selected[1])]
    return filtered_df

# returns an array containing number of entries for each value in the 'category' column of the dataframe
def get_category_count(df):
    num_dict = df['category'].value_counts()
    key_arr = ['unclassified', 'stony_iron', 'iron', 'stony']
    num_arr = [0, 0, 0, 0]
    for i in range(len(num_arr)):
        try:
            num_arr[i] = num_dict[key_arr[i]]
        except KeyError:
            num_arr[i] = 0
    return num_arr

# Map
@app.callback(
    Output('map-plot', 'figure'),
    [Input('year-slider', 'value')]
)
def update_map(years_selected):
    filtered_df = get_filtered_df(years_selected)

    trace = [
        dict(
            type="scattermapbox",
            lat=filtered_df.reclat,
            lon=filtered_df.reclong,
            text=filtered_df.name, #add more info to text (i.e include name, year, found/fell)
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

# Bar Graph
@app.callback(
    Output('bar-graph', 'figure'),
    [Input('year-slider', 'value')]
)
def update_bar_graph(years_selected):
        filtered_df = get_filtered_df(years_selected)

        trace = [dict(
            type='bar',
            x=get_category_count(filtered_df),
            y=['unclassified', 'stony-iron', 'iron', 'stony'],
            orientation='h'
        )]
        layout = dict(
            legend_title_text='Meteorite categories'
        )
        fig = dict(data=trace, layout=layout)
        return fig

# Line graph

# Density graph

# Pie Chart

# ------------------------------------------------------------------------------
if __name__ == '__main__':
    app.run_server(debug=True)
