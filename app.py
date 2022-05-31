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
            id='category-graph')]),

    html.Div([
        dcc.RadioItems(
            id='category-graph-type',
            options=[
                {'label': 'Pie chart', 'value': 'Pie'},
                {'label': 'Bar graph', 'value': 'Bar'},
            ],
            value='Bar',
            inline=False,
        ),
    ]),

    html.Div([
        dcc.Graph(
            id='year-graph')]),

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
                   'position': 'absolute', 'left': '5%'})
])


# ------------------------------------------------------------------------------
# Connect the Plotly graphs with Dash Components

# Define functions used in ___

# filters dataframe based on input from user, which is a tuple (start year, end year) from range slider selection
# ADD FOUND/ FELL FILTER TO THIS FUNCTION
def get_filtered_df(years_selected):
    filtered_df = df[(df["year"] >= years_selected[0]) & (df["year"] <= years_selected[1])]
    return filtered_df

def get_year_count(df):
    df_year_count = df.groupby(['year'])['name'].count().reset_index()
    df_year_count.rename({'name': 'count'}, inplace=True, axis=1)
    return df_year_count

def get_by_count(df, col):
    df_count = df.groupby([col])['name'].count().reset_index()
    df_count.rename({'name': 'count'}, inplace=True, axis=1)
    return df_count

# Map
@app.callback(
    Output('map-plot', 'figure'),
    [Input('year-slider', 'value')]
)
def update_map(years_selected):
    filtered_df = get_filtered_df(years_selected)
    text = filtered_df.name

    trace = [
        dict(
            type="scattermapbox",
            lat=filtered_df.reclat,
            lon=filtered_df.reclong,
            text=text,
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
            style='carto-positron',
        ),
    )
    fig = dict(data=trace, layout=layout)
    return fig


# Category Graph (Bar & Pie chart options)
@app.callback(
    Output('category-graph', 'figure'),
    [Input('year-slider', 'value'),
     Input('category-graph-type', 'value')]
)
def update_category_graph(years_selected, category_graph_type):
    filtered_df = get_filtered_df(years_selected)
    df_category_count = get_by_count(filtered_df, 'category')
    category_dict = dict(zip(df_category_count['category'], df_category_count['count']))

    count = df_category_count['count']
    category = df_category_count['category']

    count_arr = [0, 0, 0, 0]
    category_arr = ['stony', 'iron', 'stony iron', 'unclassified']

    for i in range(4):
        try:
            count_arr[i] = category_dict[category_arr[i]]
        except KeyError:
            count_arr[i] = 0
    if category_graph_type == 'Bar':
        type = 'bar'
        orientation = 'h'
        x_data = count_arr
        y_data = category_arr
        values = 'none'
        labels = 'none'
    else:
        if category_graph_type == 'Pie':
            type = 'pie'
            orientation = 'v'
            x_data = 'none'
            y_data = 'none'
            values = count_arr
            labels = category_arr
    trace = [dict(
        type=type,
        x=x_data,
        y=y_data,
        values=values,
        labels=labels,
        orientation=orientation
    )]
    layout = dict(
        legend_title_text='Meteorite categories'
    )
    fig = dict(data=trace, layout=layout)
    return fig

# Year graph (line graph)

@app.callback(
    Output('year-graph', 'figure'),
    [Input('year-slider', 'value')]
)
def update_year_graph(years_selected):
    filtered_df = get_filtered_df(years_selected)
    df_year_count = get_by_count(filtered_df,'year')
    trace = [dict(
        type='scatter',
        mode='lines',
        x=df_year_count['year'],
        y=df_year_count['count'],
        name='label',
    )]
    layout = dict(
        title=dict(
            text="Number of meteorite landings per year"
        )
    )

    fig = dict(data=trace, layout=layout)
    return fig


# ------------------------------------------------------------------------------
if __name__ == '__main__':
    app.run_server(debug=True)
