import dash
import dash_bootstrap_components as dbc
import pandas as pd
from dash import dcc
from dash import dash_table
from dash import html
from dash.dependencies import Input, Output
import plotly.express as px
import plotly.figure_factory as ff

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

discrete_color_map = {'stony': 'purple',
                      'iron': 'red',
                      'stony iron': 'blue',
                      'unclassified': 'green'}

table_cols = ['name', 'fall', 'category', 'year', 'mass (g)']

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
    colors = ['purple', 'red', 'blue', 'green']

    # get number of meteorites in each category
    for i in range(4):
        try:
            count_arr[i] = category_dict[category_arr[i]]
        except KeyError:
            count_arr[i] = 0

    if category_graph_type == 'Bar':
        fig=px.bar(
            orientation='v',
            x=category_arr,
            y=count_arr,
            color=category_arr,
            color_discrete_sequence=colors,
            )

        fig.update_layout(xaxis_title='Meteorite Category', yaxis_title='Number of Meteorite Landings')

    elif category_graph_type == 'Pie':
        fig=px.pie(
            names=category_arr,
            values=count_arr,
            color=category_arr,
            color_discrete_sequence=colors
        )

        fig.update_traces(textinfo='percent+label',
                          marker_line=dict(color='white', width=1)
                          )

    layout = dict(
        plot_bgcolor='#22434A',
        paper_bgcolor='#22434A',
        xaxis=dict(color='white', showgrid=False),
        yaxis=dict(color='white', showgrid=False),
        font_color='white',
        font_family='Courier New',
        title_font_family='Courier New',
        title_font_color='white',
        legend_title='Category'
    )
    fig.update_layout(layout)
    return fig


def get_year_graph(years_selected, discovery):
    filtered_df = get_filtered_df(years_selected, discovery)
    df_year_count = get_by_count(filtered_df, 'year')

    trace = []

    for i in discovery:
        if i == 'Fell':
            name = 'Fell'
        elif i == 'Found':
            name = 'Found'
        trace.append(
            dict(
                name=name,
                type='scatter',
                mode='lines',
                x=df_year_count[df_year_count['fall'] == i]['year'],
                y=df_year_count[df_year_count['fall'] == i]['count'],
                visible='legendonly'
            )
        )

    if 'Found' in discovery and 'Fell' in discovery:
        trace.append(
            dict(
                name='All',
                type='scatter',
                mode='lines',
                x=df_year_count['year'],
                y=df_year_count['count']
            )
        )

    layout = dict(
        hovermode='x unified',
        plot_bgcolor='#22434A',
        paper_bgcolor='#22434A',
        xaxis=dict(color='white', showgrid=False),
        yaxis=dict(color='white', showgrid=False),
        title_font_family='Courier New',
        font_family='Courier New',
        title_font_color='white',
        font_color='white',
        legend=dict(
            font=dict(
                color='white',
                font_family='Courier New'
            )
        )
    )

    fig = dict(data=trace, layout=layout)
    return fig


def get_mass_graph(years_selected, discovery):
    filtered_df = get_filtered_df(years_selected, discovery)

    hist_data = [filtered_df['mass (g)']]
    group_labels = ['all meteorite landings']

    fig = ff.create_distplot(hist_data, group_labels)

    layout = dict(
        plot_bgcolor='#22434A',
        paper_bgcolor='#22434A',
        xaxis=dict(color='#839396', showgrid=False),
        yaxis=dict(color='#839396', showgrid=False),
        title_font_family='Courier New',
        font_family='Courier New',
        title_font_color='white',
        font_color='white',
        legend=dict(
            font=dict(
                color='white'
            )
        )
    )

    fig.update_layout(layout)
    return fig


# App layout
# ------------------------------------------------------------------------------
app.layout = dbc.Container([

    html.Br(),

    # page header
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
    dbc.Row([
        dbc.Card([
            dbc.CardHeader([
                html.H3('Data Filters')
            ]),
            dbc.CardBody([
                dbc.Row([
                    dbc.CardGroup([
                        dbc.Card([
                            dbc.Col([
                                dbc.CardBody([
                                    dbc.Row([
                                        html.P([
                                            'Filter meteorite landings by year'
                                        ], style={'text-align': 'left'})
                                    ]),
                                    dbc.Row([
                                        dcc.RangeSlider(
                                            id='year-slider',
                                            min=df['year'].min(),
                                            max=df['year'].max(),
                                            value=[1795, 1915],  # default range
                                            step=1,
                                            marks=mark_values,
                                            allowCross=False,
                                            verticalHeight=900,
                                            pushable=True,
                                            tooltip={'always_visible': True,
                                                     'placement': 'bottom'}
                                        )
                                    ], style={'width': '90%', 'position': 'absolute', 'left': '1%'}),
                                    dbc.Row([
                                        html.Br()
                                    ]),
                                    dbc.Row([
                                        html.Br()
                                    ])
                                ])
                            ])
                        ]),
                        dbc.Card([
                            dbc.Col([
                                dbc.CardBody([
                                    dbc.Row([
                                        html.P([
                                            'Filter meteorite landings by discovery'
                                        ], style={'text-align': 'left'}),
                                        ]),
                                    dbc.Row([
                                        dbc.Checklist(
                                            id='found-fell-selection',
                                            options=[
                                                {'label': 'seen falling (fell)', 'value': 'Fell'},
                                                {'label': 'discovered after falling (found)', 'value': 'Found'}
                                            ],
                                            value=['Fell', 'Found'],
                                            inline=False
                                        )
                                    ], style={'width': '80%', 'position': 'absolute', 'left': '4%'}),
                                    dbc.Row([
                                        html.Br()
                                    ]),
                                    dbc.Row([
                                        html.Br()
                                    ])
                                ])
                             ])
                        ]),
                        dbc.Card([
                            dbc.Col([
                                dbc.CardBody([
                                    dbc.Row([
                                        html.P([
                                            'Colour-coordinate map markers to meteorite category:'
                                        ], style={'text-align': 'left'})
                                    ]),
                                    dbc.Row([
                                        dbc.RadioItems(
                                            id='color-coordinate',
                                            options=[
                                                {'label': 'ON', 'value': 'on'},
                                                {'label': 'OFF', 'value': 'off'}
                                            ],
                                            inline=False,
                                            switch=True,
                                            value='on'
                                        )
                                    ], style={'width': '80%', 'position': 'absolute', 'left': '4%'}),
                                    dbc.Row([
                                        html.Br()
                                    ]),
                                    dbc.Row([
                                        html.Br()
                                    ])
                                ]),
                            ])
                        ])
                    ])
                ])
            ])
        ])
    ]),

    dbc.Row([
        html.Br()
    ]),

    # visualisations (split into two columns)
    # ------------------------------------------------------------------------------
    dbc.Row([
        dbc.Col([
            dbc.Row([
                # geographic distribution card (map)
                # ------------------------------------------------------------------------------
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
                ], style={'width': '100%', 'alignment': 'center'})
            ]),
            dbc.Row([
                # card below geographic distribution contains interactive table
                # ------------------------------------------------------------------------------
                dbc.Card([
                    dbc.CardHeader([
                        dbc.Row([
                            dbc.Col([
                                html.P('Use the selection box on the map to view the data in table format')
                            ], {'width': '80%', 'align': 'left'}),
                            dbc.Col([
                                # reset map selection button
                                # ------------------------------------------------------------------------------
                                dbc.Card([
                                    dbc.Button(
                                        id='refresh-button',
                                        n_clicks=0,
                                        children=[
                                            html.P('clear map selection')
                                    ])
                                ], style={'align': 'right'})
                            ], style={'width': '20%', 'align': 'right'})
                        ])
                    ]),
                    # interactive table
                    # ------------------------------------------------------------------------------
                    dbc.CardBody([
                        dbc.Row([
                            dash_table.DataTable(
                                id='interactive-table',
                                columns=[{'name': i, 'id': i} for i in table_cols]
                            )
                        ])
                    ])
                ])
            ])
        ], style={'width': '40%', 'alignment': 'left'}),

        dbc.Col([
            # visualise-by card (split into 3 tabs: category, year & mass)
            # ------------------------------------------------------------------------------
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
                            ]),

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
            html.Div([
                # category graph control box (select bar or pie chart)
                # ------------------------------------------------------------------------------
                dbc.Card([
                    dbc.CardBody(
                        id='category-graph-controls',
                        children=[
                            dbc.Row([
                                dbc.Col([
                                    dbc.Row([
                                        html.P('Select category chart type:')
                                    ]),
                                    dbc.Row([
                                        dbc.RadioItems(
                                            id='category-graph-type',
                                            options=[
                                                {'label': 'Pie chart', 'value': 'Pie'},
                                                {'label': 'Bar graph', 'value': 'Bar'},
                                            ],
                                            value='Bar',
                                            inline=False
                                        )
                                    ])
                                ], style={'width': '50%', 'alignment': 'left'}),
                            ], style={'width': '100%', 'alignment': 'center'})
                        ]
                    )
                ])
            ],  id='category-control-box')
        ], style={'width': '40%', 'alignment': 'right'})
    ])
], fluid=True)


# App callbacks
# ------------------------------------------------------------------------------

# scatter map
# ------------------------------------------------------------------------------
@app.callback(
    Output('map-plot', 'figure'),
    [Input('year-slider', 'value'),
     Input('found-fell-selection', 'value'),
     Input('color-coordinate', 'value'),
     Input('refresh-button', 'n_clicks')]
)
def update_map(years_selected, discovery, color_coord, n_clicks):
    filtered_df = get_filtered_df(years_selected, discovery)
    text = filtered_df.name # edit for hover functionality

    trace = []

    if color_coord == 'on':
        for i in category_arr:
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
                        size=7,
                        color=discrete_color_map[i],
                        opacity=0.6),
                    customdata=filtered_df.id,
                    selectedData=None
                )
            )
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
                    size=7,
                    color='#b58900',
                    opacity=0.6),
                customdata=filtered_df.id,
                selectedData=None
            )
        )

    layout = dict(
        hovermode='closest',
        margin=dict(r=0, l=0, t=0, b=0),
        color=filtered_df.category,
        showlegend=False,
        mapbox=dict(
            accesstoken=mapbox_access_token,
            bearing=0,
            center=dict(
                lat=0,
                lon=0,
            ),
            zoom=0.7,
            style='carto-positron',
        ),
    )
    fig = dict(data=trace, layout=layout)
    return fig

'''
@app.callback(
    Output('mass-tab-content', 'children'),
    [Input('year-slider', 'value'),
     Input('found-fell-selection', 'value')]
)
def update_mass_graph(years_selected, discovery):
    fig = get_mass_graph(years_selected, discovery)
    content = dcc.Graph(id='mass-graph', figure=fig)
    return [content]
'''


# category tab
# ------------------------------------------------------------------------------
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


# year tab
# ------------------------------------------------------------------------------
@app.callback(
    Output('year-tab-content', 'children'),
    [Input('year-slider', 'value'),
     Input('found-fell-selection', 'value')]
)
def update_year_tab(years_selected, discovery):
    fig = get_year_graph(years_selected, discovery)
    content = dcc.Graph(id='year-graph', figure=fig)
    return [content]


# category tab control box
# ------------------------------------------------------------------------------
@app.callback(
    Output('category-control-box', 'style'),
    [Input('visualise-by-tabs', 'active_tab')]
)
def display_category_control_box(active_tab):
    if active_tab == 'category-tab':
        style = {'display': 'block'}
    else:
        style = {'display': 'none'}
    return style


# interactive table
# ------------------------------------------------------------------------------
@app.callback(
    Output('interactive-table', 'data'),
    [Input('map-plot', 'selectedData'),
     Input('year-slider', 'value'),
     Input('found-fell-selection', 'value')]
)
def update_table(selected_data, years_selected, discovery):
    filtered_df = get_filtered_df(years_selected, discovery)

    row_ids = []
    dff = pd.DataFrame([])

    if selected_data is not None:
        for point in selected_data['points']:
            row_ids.append(point['customdata'])
            dff = filtered_df[filtered_df['id'].isin(row_ids)]
            dff = dff.filter(items=['name', 'fall', 'category', 'year', 'mass (g)'])
        return dff.to_dict('records')
    else:
        # return empty dictionary - nothing selected
        return None


# ------------------------------------------------------------------------------
if __name__ == '__main__':
    app.run_server(debug=True)