import dash
import dash_bootstrap_components as dbc
import pandas as pd
from dash import dcc
from dash import html
from dash.dependencies import Input, Output

# ------------------------------------------------------------------------------
mark_values = {900: '900', 1000: '1000', 1100: '1100', 1200: '1200',
               1300: '1300', 1400: '1400', 1500: '1500', 1600: '1600',
               1700: '1700', 1800: '1800', 1900: '1900', 2000: '2000'}


# Initialise the app
# ------------------------------------------------------------------------------
app = dash.Dash(external_stylesheets=[dbc.themes.SOLAR])


# Import data
# ------------------------------------------------------------------------------
df = pd.read_csv('meteorite_landings_cleaned.csv')

# Store MapBox access token
# ------------------------------------------------------------------------------
mapbox_access_token = 'pk.eyJ1Ijoic2VyZW5haXZlcyIsImEiOiJjbDEzeDcxemUwNTN0M2Jxem9hbmVtb3RyIn0.K_CZ4pFHTGuZ2mOrCRC89Q'

# App layout
# ------------------------------------------------------------------------------
app.layout = dbc.Container([

    html.Br(),

    # Navbar
    # ------------------------------------------------------------------------------
    dbc.Row([
        dbc.CardGroup([
            dbc.Card([html.H1('Meteorite Landings')], style={'align': 'left', 'padding': '1%'}),
            dbc.CardGroup([
                dbc.Card([dbc.Button(['explore the data'], style={'height': '100%', 'vertical-align': 'top'})], style={'width': '2'}),
                dbc.Card([dbc.Button(['take the quiz'], style={'height': '100%', 'vertical-align': 'top'})], style={'width': '2'}),
                dbc.Card([dbc.Button(['log in/ register'], style={'height': '100%', 'vertical-align': 'top'})], style={'width': '2'})
            ], style={'align': 'right'})
        ], style={'padding': '1%'}),
    ]),

    html.Br(),

    # control box
    # ------------------------------------------------------------------------------
    dbc.Card([
        dbc.CardHeader([
            html.P('Control Box')
        ]),
        dbc.CardBody([
            dbc.Row([
                # year slider
                # ------------------------------------------------------------------------------
                dbc.Col([
                    html.P('Filter meteorite landings by year')
                ], style={'width': 2, 'text-align': 'left', 'font-size': '100%'}),
                dbc.Col([
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
                                       'position': 'absolute', 'right': '5%'})
            ]),
            dbc.Row([
                dbc.Col(html.Br())
            ]),
            # found/fell checkbox selection
            # ------------------------------------------------------------------------------
            dbc.Row([
                dbc.Col([
                    html.P('Filter meteorites by how they were discovered')
                ], style={'width': 2, 'text-align': 'left', 'font-size': '100%'}),
                dbc.Col(html.Br()),
                dbc.Col([
                    dbc.Checklist(
                        id='found-fell-selection',
                        options=[
                            {'label': 'seen falling', 'value': 'Fell'},
                            {'label': 'discovered after landing', 'value': 'Found'}
                        ],
                        value=['Fell', 'Found'],
                        inline=False
                    )
                ])
            ])
        ])
    ]),

    html.Br(),

    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader([
                    html.P('Geographic Distribution')
                ]),
                dbc.CardBody(
                    id='maps',
                    children=[
                        dbc.Row([
                            dcc.Graph(id='map-plot')
                        ], style={'width': '100%', 'alignment': 'center'})
                    ]
                )
            ], style={'width': '100%', 'alignment': 'center'})
        ], style={'width': '40%', 'alignment': 'left'}),

        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    dbc.Tabs([
                        # category tab
                        # ------------------------------------------------------------------------------
                        dbc.Tab(label='category', tab_id='category-tab', children=[
                            dbc.Row([
                                dcc.Graph(id='category-graph')
                            ], style={'width': '100%', 'alignment': 'center'}),

                            dbc.Row([
                                # pie or bar chart selection option
                                # ------------------------------------------------------------------------------
                                dbc.RadioItems(
                                    id='category-graph-type',
                                    options=[
                                        {'label': 'Pie chart', 'value': 'Pie'},
                                        {'label': 'Bar graph', 'value': 'Bar'},
                                    ],
                                    value='Bar',
                                    inline=False,
                                    style={'padding': '2%'}
                                ),
                            ], style={'width': '25%', 'margin': '2%'}),
                        ]),

                        # year tab
                        # ------------------------------------------------------------------------------
                        dbc.Tab(label='year', tab_id='year_tab', children=[
                            dbc.Row([
                                dcc.Graph(id='year-graph')
                            ], style={'width:': '100%', 'alignment': 'center'})
                        ]),

                        # mass tab
                        # ------------------------------------------------------------------------------
                        dbc.Tab(label='mass', tab_id='mass_tab')
                    ],
                        id='visualise-by-tabs',
                        active_tab='category-tab'
                    )
                ])
            ], style={'width': '100%', 'alignment': 'center'})
        ], style={'width': '40%', 'alignment': 'right'})
    ])
], fluid=True)

# Define functions used in data filtering
# ------------------------------------------------------------------------------

# filters dataframe based on input from user (control box input)
# years_selected is a tuple (start year, end year) from range slider selection
# discovery is a tuple containing values 'found' and/or 'fell' or none from checklist selection - rephrase
# adapted from x


def get_filtered_df(years_selected, discovery):
    # year selection
    filtered_df = df[(df['year'] >= years_selected[0]) & (df['year'] <= years_selected[1])]

    # discovery (found/ fell) selection
    filtered_df = filtered_df[filtered_df['fall'].isin(discovery)]
    return filtered_df


def get_year_count(df):
    df_year_count = df.groupby(['year'])['name'].count().reset_index()
    df_year_count.rename({'name': 'count'}, inplace=True, axis=1)
    return df_year_count


def get_by_count(df, col):
    df_count = df.groupby([col])['name'].count().reset_index()
    df_count.rename({'name': 'count'}, inplace=True, axis=1)
    return df_count


# App callbacks
# ------------------------------------------------------------------------------

# Map
@app.callback(
    Output('map-plot', 'figure'),
    [Input('year-slider', 'value'),
     Input('found-fell-selection', 'value')]
)
def update_map(years_selected, discovery):
    filtered_df = get_filtered_df(years_selected, discovery)
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
     Input('category-graph-type', 'value'),
     Input('found-fell-selection', 'value')]
)
def update_category_graph(years_selected, category_graph_type, discovery):
    filtered_df = get_filtered_df(years_selected, discovery)
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
        legend_title_text='Meteorite landings by category',
        plot_bgcolor='#22434A',
        paper_bgcolor='#22434A',
        xaxis=dict(color="#b58900", showgrid=False),
        yaxis=dict(color="#b58900", showgrid=False),
    )
    fig = dict(data=trace, layout=layout)
    return fig

# Year graph (line graph)

@app.callback(
    Output('year-graph', 'figure'),
    [Input('year-slider', 'value'),
     Input('found-fell-selection', 'value')]
)
def update_year_graph(years_selected, discovery):
    filtered_df = get_filtered_df(years_selected, discovery)
    df_year_count = get_by_count(filtered_df,'year')
    trace = [dict(
        type='scatter',
        mode='lines',
        x=df_year_count['year'],
        y=df_year_count['count'],
        name='label',
    )]
    layout = dict(
        plot_bgcolor = '#22434A',
        paper_bgcolor = '#22434A',
        xaxis = dict(color="#b58900", showgrid=False),
        yaxis = dict(color="#b58900", showgrid=False),
    )

    fig = dict(data=trace, layout=layout)
    return fig


# ------------------------------------------------------------------------------
if __name__ == '__main__':
    app.run_server(debug=True)
