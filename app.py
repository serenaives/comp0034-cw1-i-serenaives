import dash
import dash_bootstrap_components as dbc
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import dash_table
from dash import dcc
from dash import html
from dash._callback_context import callback_context as ctx
from dash.dependencies import Input, Output, State

# Store values used in the app
# ------------------------------------------------------------------------------

# mark values for year range slider
year_mark_values = {900: '900', 1100: '1100',
                    1300: '1300', 1500: '1500',
                    1700: '1700', 1900: '1900'}

# mark values for mass range slider
mass_mark_values = {0: '0',
                    20000000: '20 million',
                    40000000: '40 million',
                    60000000: '60 million'}

# MapBox access token
mapbox_access_token = 'pk.eyJ1Ijoic2VyZW5haXZlcyIsImEiOiJjbDEzeDcxemUwNTN0M2Jxem9hbmVtb3RyIn0.K_CZ4pFHTGuZ2mOrCRC89Q'

# all meteorite categories in the original dataset
category_arr = ['stony', 'iron', 'stony_iron', 'unclassified']

# visible_arr is used to keep track of selected meteorite categories
visible_arr = category_arr.copy()

# dictionary used to map meteorite categories to map marker colors
discrete_color_map = {'stony': 'purple',
                      'iron': 'red',
                      'stony_iron': 'blue',
                      'unclassified': 'green'}

# array used to map meteorite categories to bar and pie chart colors
colors = ['purple', 'red', 'blue', 'green']

# column names for dash_table (corresponding to the dataset columns)
table_cols = ['name', 'fall', 'category', 'year', 'mass (g)']

# generic layout for dcc.Graph objects
layout = dict(
    plot_bgcolor='#22434A',
    paper_bgcolor='#22434A',
    xaxis=dict(color='white', showgrid=False),
    yaxis=dict(color='white', showgrid=False),
    title_font_family='Courier New',
    font_family='Courier New',
    title_font_color='white',
    font_color='white'
)


# Initialise the app
# ------------------------------------------------------------------------------
app = dash.Dash(external_stylesheets=[dbc.themes.SOLAR], suppress_callback_exceptions=True)


# Import data
# ------------------------------------------------------------------------------
df = pd.read_csv('meteorite_landings_cleaned.csv')

# Define functions used in data filtering
# ------------------------------------------------------------------------------


def geo_filter(dff, selected_data):
    """filters DataFrame to match selection of points on geographical scatter map
    Args:
        dff: df with current filters applied
        selected_data: dictionary containing points on geographical scatter map selected via UI
                       input, each point is a dictionary:
                       {'points': {curveNumber, pointNumber, pointIndex, lon, lat, customdata, text}}
    Returns:
        dff: dff filtered to include only rows with id values corresponding
             to those specified by selected_data
        """
    if selected_data is not None:
        row_ids = []
        for point in selected_data['points']:
            # customdata stores the id for each point in selected_data
            row_ids.append(point['customdata'])
        # match ids of selected_data to ids in meteorite dataset and filter accordingly
        dff = dff[dff['id'].isin(row_ids)]
    return dff


def get_filtered_df(years_selected, discovery, mass_selected):
    # year selection
    filtered_df = df[(df['year'] >= years_selected[0]) & (df['year'] <= years_selected[1])]

    # discovery (found/ fell) selection
    filtered_df = filtered_df[filtered_df['fall'].isin(discovery)]

    # mass selection
    filtered_df = filtered_df[(filtered_df['mass (g)'] >= mass_selected[0]) & (filtered_df['mass (g)'] <= mass_selected[1])]
    return filtered_df


def get_year_count(df):
    df_year_count = df.groupby(['year', 'fall'])['name'].count().reset_index()
    df_year_count.rename({'name': 'count'}, inplace=True, axis=1)
    return df_year_count


def get_by_category_count(filtered_df):
    df_count = pd.DataFrame(filtered_df['category'].value_counts().reset_index().values, columns=['category', 'count'])
    df_count = df_count.sort_index(axis=0, ascending=True)
    return df_count


def get_by_year_count(filtered_df):
    year_count = filtered_df.groupby(['year', 'fall'])['name'].count().reset_index()
    year_count.rename(columns={'name': 'count'}, inplace=True)
    year_count.sort_values(by='year', inplace=True)
    return year_count


def get_category_graph(filtered_df, category_graph_type):
    df_category_count = get_by_category_count(filtered_df)

    if category_graph_type == 'Bar':
        fig = px.bar(
            data_frame=df_category_count,
            x='category',
            y='count',
            orientation='v',
            color='category',
            color_discrete_sequence=colors,
            )

        fig.update_layout(
            xaxis_title='Meteorite Category',
            yaxis_title='Number of Meteorite Landings')

    elif category_graph_type == 'Pie':
        fig = px.pie(
            data_frame=df_category_count,
            names='category',
            values='count',
            color='category',
            color_discrete_sequence=colors
        )

        fig.update_traces(
            textinfo='percent+label',
            marker_line=dict(color='white', width=1)
        )

    fig.update_layout(
        layout,
        legend_title='Category'
    )
    return fig


def get_year_graph(filtered_df, discovery):
    df_year_count = get_by_year_count(filtered_df)

    trace = []

    if 'Found' in discovery and 'Fell' in discovery:
        trace.append(
            dict(
                name='All',
                type='scatter',
                mode='lines',
                x=df_year_count['year'],
                y=df_year_count['count'],
                visible='legendonly'
            )
        )

    for i in discovery:
        trace.append(
            dict(
                name=i,
                type='scatter',
                mode='lines',
                x=df_year_count[df_year_count['fall'] == i]['year'],
                y=df_year_count[df_year_count['fall'] == i]['count']
            )
        )

    fig = go.Figure(data=trace, layout=layout)
    fig.update_layout(
        hovermode='x unified',
        yaxis_title='Number of Meteorite Landings',
        xaxis_title='Year'
    )

    return fig


def get_mass_graph(filtered_df, mass_graph_type, discovery, log_scale):
    if log_scale == 'on':
        filtered_df['log mass (g)'] = np.log(filtered_df['mass (g)'])
        x_col = 'log mass (g)'
        xaxis_title = 'log mass (g)'
    else:
        x_col = 'mass (g)'
        xaxis_title = 'Mass (g)'

    fig = go.Figure()

    if mass_graph_type == 'Histogram':
        if 'Found' in discovery and 'Fell' in discovery:
            fig.add_trace(
                go.Histogram(
                    name='All',
                    x=filtered_df[x_col],
                    visible='legendonly'
                ),
            )

        for i in discovery:
            fig.add_trace(
                go.Histogram(
                    name=i,
                    x=filtered_df[filtered_df['fall'] == i][x_col]
                ),
            )

        fig.update_layout(
            layout,
            barmode='overlay',
            hovermode='x unified',
            xaxis_title=xaxis_title,
            yaxis_title='Number of Meteorite Landings'
        )

        fig.update_traces(opacity=0.75)

    elif mass_graph_type == 'Box':
        if 'Found' in discovery and 'Fell' in discovery:
            fig.add_trace(
                go.Box(
                    name='All',
                    x=filtered_df[x_col],
                    orientation='h',
                    visible='legendonly'
                ),
            )

        for i in discovery:
            fig.add_trace(
                go.Box(
                    name=i,
                    x=filtered_df[filtered_df['fall'] == i][x_col],
                    orientation='h'
                ),
            )
        fig.update_layout(
            xaxis_title=xaxis_title)

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
        ], style={'padding': '1%'}, id='card-grp'),
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
                                            marks=year_mark_values,
                                            allowCross=False,
                                            verticalHeight=900,
                                            pushable=True,
                                            tooltip={'always_visible': True,
                                                     'placement': 'bottom'}
                                        )
                                    ], style={'width': '100%', 'position': 'absolute', 'left': '1%'}),
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
                                            'Filter meteorite landings by mass (g)'
                                        ], style={'text-align': 'left'})
                                    ]),
                                    dbc.Row([
                                        dcc.RangeSlider(
                                            id='mass-slider',
                                            min=df['mass (g)'].min(),
                                            max=df['mass (g)'].max(),
                                            value=[0.01, 60000000],  # default range
                                            step=1,
                                            marks=mass_mark_values,
                                            allowCross=False,
                                            verticalHeight=900,
                                            pushable=True,
                                            tooltip={'always_visible': True,
                                                     'placement': 'bottom'}
                                        )
                                    ], style={'width': '100%', 'position': 'absolute', 'left': '1%'}),
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
                                            'Coordinate map markers to category:'
                                        ], style={'text-align': 'left'})
                                    ]),
                                    dbc.Row([
                                        dbc.RadioItems(
                                            id='color-coordinate',
                                            options=[
                                                {'label': 'ON', 'value': 'on'},
                                                {'label': 'OFF', 'value': 'off'}
                                            ],
                                            inline=True,
                                            switch=True,
                                            value='on'
                                        )
                                    ], style={'width': '80%', 'left': '4%'}),
                                    dbc.Row([
                                        html.Br()
                                    ]),
                                    dbc.Row([
                                        html.P([
                                            'Coordinate map marker size to mass:'
                                        ], style={'text-align': 'left'})
                                    ]),
                                    dbc.Row([
                                        dbc.RadioItems(
                                            id='size-coordinate',
                                            options=[
                                                {'label': 'ON', 'value': 'on'},
                                                {'label': 'OFF', 'value': 'off'}
                                            ],
                                            inline=True,
                                            switch=True,
                                            value='off'
                                        )
                                    ], style={'width': '80%', 'left': '4%'})
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
                        id='map-card',
                        children=[
                            dbc.Row([
                                dcc.Graph(id='map-plot', selectedData=None)
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
                                html.P('Use the selection box on the map to filter the visualisations and view the '
                                       'data in table format')
                            ], {'width': '80%', 'align': 'left'}),
                            dbc.Col([
                                # reset map selection button
                                # ------------------------------------------------------------------------------
                                dbc.Card([
                                    dbc.Button(
                                        id='refresh-button',
                                        n_clicks=0,
                                        children=[
                                            html.P('clear selection')
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
                                columns=[{'name': i, 'id': i} for i in table_cols],
                                style_header={
                                    'backgroundColor': '#b58900',
                                    'color': '#ffffff',
                                    'fontWeight': 'bold'}
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
            ],  id='category-control-box'),
            html.Div([
                # category graph control box (select bar or pie chart)
                # ------------------------------------------------------------------------------
                dbc.Card([
                    dbc.CardBody(
                        id='mass-graph-controls',
                        children=[
                            dbc.Col([
                                dbc.CardGroup([
                                    dbc.Card([
                                        dbc.Col([
                                            dbc.Row([
                                                html.P('Select mass chart type:')
                                            ]),
                                            dbc.Row([
                                                dbc.RadioItems(
                                                    id='mass-graph-type',
                                                    options=[
                                                        {'label': 'Histogram', 'value': 'Histogram'},
                                                        {'label': 'Box and Whisker', 'value': 'Box'},
                                                    ],
                                                    value='Histogram',
                                                    inline=False
                                                )
                                            ])
                                        ], style={'margin': '4%'})
                                    ]),
                                    dbc.Card([
                                        dbc.Col([
                                            dbc.Row([
                                                html.P('log scale:')
                                            ]),
                                            dbc.Row([
                                                dbc.RadioItems(
                                                    id='log-scale',
                                                    options=[
                                                        {'label': 'ON', 'value': 'on'},
                                                        {'label': 'OFF', 'value': 'off'},
                                                    ],
                                                    value='on',
                                                    inline=False
                                                )
                                            ])
                                        ], style={'margin': '4%'})
                                    ])
                                ], style={'width': '100%'}),
                            ], style={'width': '100%', 'alignment': 'center'})
                        ]
                    )
                ])
            ], id='mass-control-box')
        ], style={'width': '40%', 'alignment': 'right'})
    ])
], fluid=True)


# App callbacks
# ------------------------------------------------------------------------------
'''
def remove_cat(filtered_df, cat):
    filtered_df = filtered_df[filtered_df['category'] != cat]
    return filtered_df

def add_cat(filtered_df, cat):
    filtered_df = filtered_df[filtered_df['category'] != cat]
    return filtered_df
'''
# scatter map
# ------------------------------------------------------------------------------
@app.callback(
    Output('map-plot', 'figure'),
    [Input('year-slider', 'value'),
     Input('found-fell-selection', 'value'),
     Input('color-coordinate', 'value'),
     Input('refresh-button', 'n_clicks'),
     Input('mass-slider', 'value'),
     Input('size-coordinate', 'value'),
     Input('category-graph', 'restyleData'),
     Input('map-plot', 'selectedData'),
     State('map-plot', 'figure')]
)
def update_map(years_selected, discovery, color_coord, n_clicks, mass_selected, size, cat_selected, geo_selected, current_fig):
    filtered_df = get_filtered_df(years_selected, discovery, mass_selected)
    if ctx.triggered[0]['prop_id'].split('.')[0] != 'refresh-button':
        filtered_df = geo_filter(filtered_df, geo_selected)

    text = filtered_df.name
    trace = []

    global visible_arr

    if ctx.triggered[0]['prop_id'].split('.')[0] == 'category-graph':
        if cat_selected is not None:
            if cat_selected[0]['visible'][0] == 'legendonly':
                visible_arr.remove(category_arr[cat_selected[1][0]])
            elif cat_selected[0]['visible'][0]:
                visible_arr.append(category_arr[cat_selected[1][0]])
        else:
            # except for first call, when no fig has been initialised
            if current_fig is not None:
                return current_fig

    if color_coord == 'on':
        for i in category_arr:
            if i in visible_arr:
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
                            color=discrete_color_map[i],
                            size=2*(np.log(filtered_df[filtered_df['category'] == i]['mass (g)'])),
                            opacity=0.6),
                        customdata=filtered_df[filtered_df['category'] == i]['id']
                    )
            )
    else:
        trace.append(
            dict(
                type='scattermapbox',
                lat=filtered_df.reclat,
                lon=filtered_df.reclong,
                hovertemplate=None,
                text=text,
                hoverinfo='text',
                mode='markers',
                marker=dict(
                    color='#b58900',
                    size=2*(np.log(filtered_df['mass (g)'])),
                    opacity=0.6),
                customdata=filtered_df.id
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

    if size == 'off':
        for i in fig['data']:
            i['marker']['size'] = 9

    return fig


@app.callback(
    Output('mass-tab-content', 'children'),
    [Input('year-slider', 'value'),
     Input('found-fell-selection', 'value'),
     Input('mass-graph-type', 'value'),
     Input('map-plot', 'selectedData'),
     Input('refresh-button', 'n_clicks'),
     Input('mass-slider', 'value'),
     Input('log-scale', 'value')]
)
def update_mass_tab(years_selected, discovery, mass_graph_type, selected_data, n_clicks, mass_selected, log_scale):
    filtered_df = get_filtered_df(years_selected, discovery, mass_selected)

    if ctx.triggered[0]['prop_id'].split('.')[0] != 'refresh-button':
        filtered_df = geo_filter(filtered_df, selected_data)

    fig = get_mass_graph(filtered_df, mass_graph_type, discovery, log_scale)
    content = dcc.Graph(id='mass-graph', figure=fig)
    return content


# category tab
# ------------------------------------------------------------------------------
@app.callback(
    Output('category-tab-content', 'children'),
    [Input('year-slider', 'value'),
     Input('category-graph-type', 'value'),
     Input('found-fell-selection', 'value'),
     Input('map-plot', 'selectedData'),
     Input('refresh-button', 'n_clicks'),
     Input('mass-slider', 'value')]
)
def update_category_tab(years_selected, category_graph_type, discovery, selected_data, n_clicks, mass_selected):
    filtered_df = get_filtered_df(years_selected, discovery, mass_selected)

    if ctx.triggered[0]['prop_id'].split('.')[0] != 'refresh-button':
        filtered_df = geo_filter(filtered_df, selected_data)

    fig = get_category_graph(filtered_df, category_graph_type)
    content = dcc.Graph(id='category-graph', figure=fig)
    return [content]


# year tab
# ------------------------------------------------------------------------------
@app.callback(
    Output('year-tab-content', 'children'),
    [Input('year-slider', 'value'),
     Input('found-fell-selection', 'value'),
     Input('map-plot', 'selectedData'),
     Input('refresh-button', 'n_clicks'),
     Input('mass-slider', 'value')]
)
def update_year_tab(years_selected, discovery, selected_data, n_clicks, mass_selected):
    filtered_df = get_filtered_df(years_selected, discovery, mass_selected)

    if ctx.triggered[0]['prop_id'].split('.')[0] != 'refresh-button':
        filtered_df = geo_filter(filtered_df, selected_data)

    fig = get_year_graph(filtered_df, discovery)
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


# mass tab control box
# ------------------------------------------------------------------------------
@app.callback(
    Output('mass-control-box', 'style'),
    [Input('visualise-by-tabs', 'active_tab')]
)
def display_mass_control_box(active_tab):
    if active_tab == 'mass-tab':
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
     Input('found-fell-selection', 'value'),
     Input('refresh-button', 'n_clicks'),
     Input('mass-slider', 'value')]
)
def update_table(selected_data, years_selected, discovery, n_clicks, mass_selected):
    # if callback was triggered by refresh button clear table
    if ctx.triggered[0]['prop_id'].split('.')[0] == 'refresh-button':
        return None

    # if nothing is selected on the map table is empty
    elif selected_data is None:
        return None

    # else populate table according to the selected data
    else:
        filtered_df = get_filtered_df(years_selected, discovery, mass_selected)
        dff = geo_filter(filtered_df, selected_data)
        dff = dff.filter(items=['name', 'fall', 'category', 'year', 'mass (g)'])
        return dff.to_dict('records')


# ------------------------------------------------------------------------------
if __name__ == '__main__':
    app.run_server(debug=False)