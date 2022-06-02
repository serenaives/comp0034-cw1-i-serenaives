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
app = dash.Dash(external_stylesheets=[dbc.themes.SOLAR], suppress_callback_exceptions=True)


# Import data
# ------------------------------------------------------------------------------
df = pd.read_csv('meteorite_landings_cleaned.csv')

# Store MapBox access token
# ------------------------------------------------------------------------------
mapbox_access_token = 'pk.eyJ1Ijoic2VyZW5haXZlcyIsImEiOiJjbDEzeDcxemUwNTN0M2Jxem9hbmVtb3RyIn0.K_CZ4pFHTGuZ2mOrCRC89Q'

# Store array containing all possible meteorite categories
# ------------------------------------------------------------------------------
category_arr = ['stony', 'iron', 'stony iron', 'unclassified']


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


def get_by_count(filtered_df, col):
    df_count = filtered_df.groupby([col, 'fall'])['name'].count().reset_index()
    df_count.rename({'name': 'count'}, inplace=True, axis=1)
    return df_count


def get_category_graph(years_selected, category_graph_type, discovery):
    filtered_df = get_filtered_df(years_selected, discovery)
    df_category_count = get_by_count(filtered_df, 'category')
    category_dict = dict(zip(df_category_count['category'], df_category_count['count']))

    count = df_category_count['count']
    category = df_category_count['category']

    count_arr = [0, 0, 0, 0]

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
        xaxis=dict(color='#839396', showgrid=False),
        yaxis=dict(color='#839396', showgrid=False),
        font={'color': '#839396'}
    )
    fig = dict(data=trace, layout=layout)
    return fig


# Control boxes for visualise-by charts
# ------------------------------------------------------------------------------
def category_graph_controls():
    children = [
        dbc.Row([
            dbc.Row([
                # pie or bar chart selection option
                # ------------------------------------------------------------------------------
                dbc.Col([
                    dbc.Row([
                        html.P('Select chart type:')
                    ])
                ]),
                dbc.Col([
                    dbc.RadioItems(
                        id='category-graph-type',
                        options=[
                            {'label': 'Pie chart', 'value': 'Pie'},
                            {'label': 'Bar graph', 'value': 'Bar'},
                        ],
                        value='Bar',
                        inline=False,
                        style={'padding': '2%'}
                    )], style={})
            ]),
        ], justify='center')
    ]
    return children


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
                dbc.Card([dbc.Button(['explore the data'], style={'height': '100%'})], style={'width': '2'}),
                dbc.Card([dbc.Button(['take the quiz'], style={'height': '100%'})], style={'width': '2'}),
                dbc.Card([dbc.Button(['log in/ register'], style={'height': '100%'})], style={'width': '2'})
            ], style={'align': 'right'})
        ], style={'padding': '1%'}),
    ]),

    html.Br(),

    # control box
    # ------------------------------------------------------------------------------
    dbc.Card([
        dbc.CardHeader([
            html.H3('Data Filters')
        ]),
        dbc.CardBody([
            dbc.Row([
                # year slider
                # ------------------------------------------------------------------------------
                dbc.Col([
                    dbc.Row([
                        dbc.Col([
                            html.P('Filter meteorite landings by year')
                        ], style={'text-align': 'left', 'font-size': '100%'}),
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
                                    )], style={'width': '40%',
                                               'position': 'absolute', 'right': '35%'}
                        )
                    ])
                ])
            ]),
            dbc.Row([
                dbc.Col(html.Br())
            ]),
            # found/fell checkbox selection
            # ------------------------------------------------------------------------------
            dbc.Row([
                dbc.Col([
                    html.P('Filter meteorites by discovery')
                ], style={'width': 2, 'text-align': 'left', 'font-size': '100%'}),
                dbc.Row([
                    dbc.Checklist(
                        id='found-fell-selection',
                        options=[
                            {'label': 'seen falling', 'value': 'Fell'},
                            {'label': 'discovered after falling', 'value': 'Found'}
                        ],
                        value=['Fell', 'Found'],
                        inline=False
                    )
                ], style={'width': '70%', 'position': 'absolute', 'right': '5%'})
            ])
        ])
    ]),

    html.Br(),

    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader([
                    html.H3('Geographic Distribution')
                ]),
                dbc.CardBody(
                    id='maps',
                    children=[
                        dbc.Row([
                            dcc.Graph(id='map-plot')
                        ], style={'margin': '0', 'width': '100%', 'alignment': 'center'})
                    ]
                )
            ], style={'width': '100%', 'alignment': 'center'}),
            dbc.Card([
                dbc.CardBody([
                    dbc.Col([
                        dbc.Row([
                            dbc.Row([
                                html.P('Colour-coordinate map markers to meteorite category:')
                            ]),
                            dbc.Row([
                                dbc.RadioItems(
                                    id='color-coordinate',
                                    options=[
                                        {'label': 'ON', 'value': 'on'},
                                        {'label': 'OFF', 'value': 'off'}
                                    ],
                                    value='off',
                                    switch=True
                                )
                            ])
                        ])
                    ])
                ])
            ])
        ], style={'width': '40%', 'alignment': 'left'}),

        dbc.Col([
            dbc.Card([
                dbc.CardHeader([
                    html.H3('Visualise meteorite landings by:')
                ]),
                dbc.CardBody([
                    dbc.Tabs([
                        # category tab
                        # ------------------------------------------------------------------------------
                        dbc.Tab(
                            label='category',
                            tab_id='category-tab',
                            children=[
                                dbc.Row(
                                    id='category-tab-content'
                                )
                            ]
                        ),

                        # year tab
                        # ------------------------------------------------------------------------------
                        dbc.Tab(label='year', tab_id='year-tab',
                                children=[
                                    dbc.Row(
                                        id='year-tab-content'
                                    )
                                ]),

                        # mass tab
                        # ------------------------------------------------------------------------------
                        dbc.Tab(label='mass', tab_id='mass-tab',
                                children=[
                                    dbc.Row(
                                        id='mass-tab-content'
                                    )
                                ])
                    ],
                        id='visualise-by-tabs',
                        active_tab='category-tab'
                    )
                ])
            ], style={'width': '100%', 'alignment': 'center'}
            ),
            dbc.Card([
                dbc.CardBody(
                    id='visualise-by-chart-controls',
                    children=category_graph_controls()
                )
            ])
        ], style={'width': '40%', 'alignment': 'right'})
    ])
], fluid=True)


# App callbacks
# ------------------------------------------------------------------------------

# Map
@app.callback(
    Output('map-plot', 'figure'),
    [Input('year-slider', 'value'),
     Input('found-fell-selection', 'value'),
     Input('color-coordinate', 'value')]
)
def update_map(years_selected, discovery, color_coord):
    filtered_df = get_filtered_df(years_selected, discovery)
    text = filtered_df.name # edit for hover functionality

    discrete_color_map = {'stony': 'pink',
                          'iron': 'red',
                          'stony iron': 'blue',
                          'unclassified': 'green'}

    trace = []

    if color_coord == 'on':
        for i in category_arr: # like a subplot for each colour
            trace.append(
                dict(
                    name=i,
                    type='scattermapbox',
                    lat=filtered_df[filtered_df['category'] == i]['reclat'],
                    lon=filtered_df[filtered_df['category'] == i]['reclong'],
                    text=text,
                    hoverinfo='text',
                    mode='markers',
                    marker=dict(
                        size=5,
                        color=discrete_color_map[i],
                        opacity=0.4),
                )
            )
        showlegend=True
    else:
        trace.append(
            dict(
                type='scattermapbox',
                lat=filtered_df.reclat,
                lon=filtered_df.reclong,
                text=text,
                hoverinfo='text',
                mode='markers',
                marker=dict(
                    size=5,
                    color='#b58900',
                    opacity=0.4)
            )
        )
        showlegend=False

    layout = dict(
        hovermode='closest',
        margin=dict(r=0, l=0, t=0, b=0),
        color=filtered_df.category,
        showlegend=showlegend,
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


# Year graph (line graph)

@app.callback(
    Output('year-graph', 'figure'),
    [Input('year-slider', 'value'),
     Input('found-fell-selection', 'value')]
)
def update_year_graph(years_selected, discovery):
    filtered_df = get_filtered_df(years_selected, discovery)
    df_year_count = get_by_count(filtered_df, 'year')

    trace = []

    for i in discovery:
        if i == 'Fell':
            name = 'seen falling'
        elif i == 'Found':
            name = 'discovered after falling'
        trace.append(
            dict(
                name=name,
                type='scatter',
                mode='line',
                x=df_year_count[df_year_count['fall'] == i]['year'],
                y=df_year_count[df_year_count['fall'] == i]['count']
            )
        )

    layout = dict(
        plot_bgcolor='#22434A',
        paper_bgcolor='#22434A',
        xaxis=dict(color='#839396', showgrid=False),
        yaxis=dict(color='#839396', showgrid=False),
        legend=dict(
            font=dict(
                color='#839396'
            )
        )
    )

    fig = dict(data=trace, layout=layout)
    return fig

@app.callback(
    Output('category-tab-content', 'children'),
    [Input('year-slider', 'value'),
     Input('category-graph-type', 'value'),
     Input('found-fell-selection', 'value')]
)
def update_category_tab(years_selected, category_graph_type, discovery):
    fig = get_category_graph(years_selected, category_graph_type, discovery)
    content = dcc.Graph(id='category-graph', figure=fig)
    return [content]

@app.callback(
    Output('visualise-by-chart-controls', 'children'),
    [Input('visualise-by-tabs', 'active_tab')]
)
def update_visualise_by_chart_controls(active_tab):
    if active_tab == 'category-tab':
        children = category_graph_controls()
    elif active_tab == 'year-tab':
        children = [

        ]
    elif active_tab == 'mass-tab':
        children = [

        ]
    else:
        children = [html.P('error displaying chart controls')]
    return children


# ------------------------------------------------------------------------------
if __name__ == '__main__':
    app.run_server(debug=True)