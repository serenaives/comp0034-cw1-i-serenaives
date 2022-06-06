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
# ---------------------------------------------------------------------------------

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
category_arr = ['stony', 'iron', 'stony iron', 'unclassified']

# array used to keep track of selected meteorite categories
visible_arr = category_arr.copy()

# dictionary used to map meteorite categories to map marker colors
discrete_color_map = {'stony': '#3B8FA2',
                      'iron': '#CD4117',
                      'stony iron': '#F3CA4C',
                      'unclassified': '#888888'}

# array used to map meteorite categories to bar and pie chart colors
colors = ['#3B8FA2', '#CD4117', '#F3CA4C', '#888888']

# dictionary used to map year and mass graphs to colors corresponding to found/ fell categorisation
two_color_palette = {
    'Found': '#466930',
    'Fell': '#48BF52'
}

# column names for dash_table (corresponding to the dataset columns)
table_cols = ['name', 'fall', 'category', 'year', 'mass (g)']

# generic layout for dcc.Graph objects
layout = dict(
    plot_bgcolor='#FFFFFF',
    paper_bgcolor='#FFFFFF',
    xaxis=dict(color='black', showgrid=False),
    yaxis=dict(color='black', showgrid=False),
    title_font_family='Courier New',
    font_family='Courier New',
    title_font_color='black',
    font_color='black'
)

# Initialise the app
# ---------------------------------------------------------------------------------
app = dash.Dash(external_stylesheets=[dbc.themes.MINTY], suppress_callback_exceptions=True)

# Import data
# ---------------------------------------------------------------------------------
df = pd.read_csv('meteorite_landings_cleaned.csv')


# Define functions used in data filtering
# ---------------------------------------------------------------------------------


def get_filtered_df(years_selected, discovery, mass_selected):
    """filters global DataFrame df by year, discovery type (found/ fell) and mass
    Args:
        years_selected: tuple [start year, end year]
        discovery: array of strings, one of ["Found"], ["Fell"], ["Found", "Fell"], ["Fell", "Found"] or []
        mass_selected: tuple [minimum mass, maximum mass]
    Returns:
        filtered_df: global df filtered by parameter values
        """
    # filter by year selection
    filtered_df = df[(df['year'] >= years_selected[0]) & (df['year'] <= years_selected[1])]

    # filter by discovery (found/ fell) selection
    filtered_df = filtered_df[filtered_df['fall'].isin(discovery)]

    # filter by mass selection
    filtered_df = filtered_df[
        (filtered_df['mass (g)'] >= mass_selected[0]) & (filtered_df['mass (g)'] <= mass_selected[1])]
    return filtered_df


def geo_filter(dff, selected_data):
    """filters a DataFrame to match selection of points on geographical scatter map
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


def get_by_category_count(filtered_df):
    """calculates count of each unique value in 'category' column of a DataFrame
    Args:
        filtered_df: df with current filters applied
    Returns:
        df_count: DataFrame with columns 'category' and 'count'
    """
    df_count = pd.DataFrame(filtered_df['category'].value_counts().reset_index().values, columns=['category', 'count'])
    df_count = df_count.sort_index(axis=0, ascending=True)
    return df_count


def get_by_year_count(filtered_df):
    """groups a DataFrame by 'year' and 'fall' columns and calculates count of each group
    Args:
        filtered_df: df with current filters applied
    Returns:
        df_count: DataFrame with columns 'year', 'fall' and 'count'
    """
    df_count = filtered_df.groupby(['year', 'fall'])['name'].count().reset_index()
    df_count.rename(columns={'name': 'count'}, inplace=True)
    df_count.sort_values(by='year', inplace=True)
    return df_count


# Define functions used to create plotly graph figures in visualise-by column
# --------------------------------------------------------------------------------


# category graph (bar graph or pie chart depending on argument category_graph_type)
# ---------------------------------------------------------------------------------
def get_category_graph(filtered_df, category_graph_type):
    # get meteorite count by category
    df_category_count = get_by_category_count(filtered_df)

    # bar graph
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

    # pie chart
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
            marker_line=dict(color='black', width=1)
        )

    # update fig with generic graph layout and shared legend title
    fig.update_layout(
        layout,
        legend_title='Category'
    )
    return fig


# year graph (line graph with separate traces corresponding to found/ fell categorisation)
# ----------------------------------------------------------------------------------------
def get_year_graph(filtered_df, discovery):
    # get meteorite count by year
    df_year_count = get_by_year_count(filtered_df)

    trace = []

    # if found and fell are both selected
    if 'Found' in discovery and 'Fell' in discovery:
        # add a trace with data corresponding to ALL meteorite landings
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

    # add separate traces corresponding to each selected mode of discovery (found and/or fell)
    for i in discovery:
        trace.append(
            dict(
                name=i,
                type='scatter',
                mode='lines',
                x=df_year_count[df_year_count['fall'] == i]['year'],
                y=df_year_count[df_year_count['fall'] == i]['count'],
                marker=dict(
                    color=two_color_palette[i]
                )
            )
        )

    # initialise figure with generic layout
    fig = go.Figure(data=trace, layout=layout)
    # update layout with features specific to year graph
    fig.update_layout(
        hovermode='x unified',
        yaxis_title='Number of Meteorite Landings',
        xaxis_title='Year'
    )
    return fig


# mass graph (histogram or box & whisker plot depending on argument mass_graph_type)
# ----------------------------------------------------------------------------------------
def get_mass_graph(filtered_df, mass_graph_type, discovery, log_scale):
    # set scale and x-axis title according to parameter log_scale
    if log_scale == 'on':
        filtered_df['log mass (g)'] = np.log(filtered_df['mass (g)'])
        x_col = 'log mass (g)'
        xaxis_title = 'log mass (g)'
    else:
        x_col = 'mass (g)'
        xaxis_title = 'Mass (g)'

    # initialise figure with generic layout
    fig = go.Figure(layout=layout)

    # histogram
    if mass_graph_type == 'Histogram':
        # if found and fell are both selected
        if 'Found' in discovery and 'Fell' in discovery:
            fig.add_trace(
                go.Histogram(
                    name='All',
                    x=filtered_df[x_col],
                    visible='legendonly'
                ),
            )

        # add separate traces corresponding to each selected mode of discovery (found and/or fell)
        for i in discovery:
            fig.add_trace(
                go.Histogram(
                    name=i,
                    x=filtered_df[filtered_df['fall'] == i][x_col],
                    marker=dict(
                        color=two_color_palette[i]
                    )
                ),
            )

        # update layout with features specific to histogram
        fig.update_layout(
            layout,
            barmode='overlay',
            hovermode='x unified',
            xaxis_title=xaxis_title,
            yaxis_title='Number of Meteorite Landings'
        )

        fig.update_traces(opacity=0.75)

    # box & whisker plot
    elif mass_graph_type == 'Box':
        # if found and fell are both selected
        if 'Found' in discovery and 'Fell' in discovery:
            # add a trace with data corresponding to ALL meteorite landings
            fig.add_trace(
                go.Box(
                    name='All',
                    x=filtered_df[x_col],
                    orientation='h',
                    visible='legendonly'
                ),
            )

        # add separate traces corresponding to each selected mode of discovery (found and/or fell)
        for i in discovery:
            fig.add_trace(
                go.Box(
                    name=i,
                    x=filtered_df[filtered_df['fall'] == i][x_col],
                    orientation='h',
                    marker=dict(
                        color=two_color_palette[i]
                    )
                ),
            )

        # update layout with features specific to box & whisker plot
        fig.update_layout(
            xaxis_title=xaxis_title)

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
                dbc.Card([dbc.Button(['explore the data'], color='danger', style={'height': '100%'})], style={'width': '2'}),
                dbc.Card([dbc.Button(['take the quiz'], color='danger', style={'height': '100%'})], style={'width': '2'}),
                dbc.Card([dbc.Button(['log in/ register'], color='danger', style={'height': '100%'})], style={'width': '2'})
            ], style={'align': 'right'})
        ], style={'padding': '1%'}, id='card-grp'),
    ]),

    html.Br(),

    # data filters control box
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
                                        # year selection slider
                                        # -------------------------------------------------------
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
                                        # mass selection slider
                                        # ---------------------------------------------------------
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
                                        # discovery (found/ fell) checklist
                                        # -------------------------------------------------------------------
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
                                        # RadioItems selection: color-coordinate to category
                                        # ---------------------------------------------------------
                                        dbc.RadioItems(
                                            id='color-coordinate',
                                            options=[
                                                {'label': 'ON', 'value': 'on'},
                                                {'label': 'OFF', 'value': 'off'}
                                            ],
                                            inline=True,
                                            switch=True,
                                            value='off'
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
                                        # RadioItems selection: size-coordinate to mass
                                        # ---------------------------------------------------------
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
        # visualisation of geographic distribution
        # --------------------------------------------------------------------------
        dbc.Col([
            dbc.Row([
                dbc.Card([
                    dbc.CardHeader([
                        html.H3('Geographic Distribution')
                    ]),
                    dbc.CardBody(
                        id='map-card',
                        children=[
                            dbc.Row([
                                # geographic scatter map
                                # ----------------------------------------------------------------
                                dcc.Graph(id='map-plot', selectedData=None)
                            ], style={'margin': '0', 'width': '100%', 'alignment': 'center'})
                        ]
                    )
                ], style={'width': '100%', 'alignment': 'center'})
            ]),
            dbc.Row([
                # card below geographic distribution contains interactive table
                # ---------------------------------------------------------------------------------------------
                dbc.Card([
                    dbc.CardHeader([
                        dbc.Row([
                            dbc.Col([
                                html.P('Use the selection box on the map to filter the visualisations and view '
                                       'the data in table format')
                            ], {'width': '80%', 'align': 'left'}),
                            dbc.Col([
                                # reset map selection button
                                # --------------------------------------------------------------------
                                dbc.Card([
                                    dbc.Button(
                                        id='refresh-button',
                                        n_clicks=0,
                                        children=[
                                            html.P('clear selection')
                                        ], color='danger')
                                ], style={'align': 'right'})
                            ], style={'width': '20%', 'align': 'right'})
                        ])
                    ]),
                    dbc.CardBody([
                        dbc.Row([
                            # interactive table
                            # ------------------------------------------------------------------------------
                            dash_table.DataTable(
                                id='interactive-table',
                                columns=[{'name': i, 'id': i} for i in table_cols],
                                style_header={
                                    'backgroundColor': '#FF7850',
                                    'color': '#ffffff',
                                    'fontWeight': 'bold'
                                }
                            )
                        ])
                    ])
                ])
            ])
        ], style={'width': '40%', 'alignment': 'left'}),

        # visualisations by category/ year/ mass
        # ------------------------------------------------------------------------------
        dbc.Col([
            dbc.Card([
                dbc.CardHeader([
                    html.H3('Visualise meteorite landings by:')
                ]),
                dbc.CardBody([
                    # tabs to select category/ year/ mass
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
                # category graphs control box
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
                                        # RadioItems selection: bar or pie chart
                                        # -------------------------------------------------------
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
            ], id='category-control-box'),
            html.Div([
                # mass graphs control box
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
                                                # RadioItems selection: histogram or box & whisker
                                                # -------------------------------------------------------
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
                                                # RadioItems selection: log scale on or off
                                                # -------------------------------------------------------
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


# geographical scatter map
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
    text = filtered_df.name
    trace = []

    # if anything other than input from the <<reset map selection>> button triggered the callback
    if ctx.triggered[0]['prop_id'].split('.')[0] != 'refresh-button':
        # filter by current selection of points on map
        filtered_df = geo_filter(filtered_df, geo_selected)

    # share data stored in visible_arr between callbacks
    global visible_arr

    # if the callback was triggered by trace selection/ deselection on category graph
    if ctx.triggered[0]['prop_id'].split('.')[0] == 'category-graph':

        # then filter data visible on map according to currently selected categories on category graph
        if cat_selected is not None:

            # if the callback was triggered by trace deselection
            if cat_selected[0]['visible'][0] == 'legendonly':
                # match index to category_arr and remove deselected category from visible_arr
                visible_arr.remove(category_arr[cat_selected[1][0]])

            # if the callback was triggered by selection of a new trace
            elif cat_selected[0]['visible'][0]:
                # match index to category_arr and add newly selected category to visible_arr
                visible_arr.append(category_arr[cat_selected[1][0]])

        # if callback was not triggered by trace selection/ deselection
        # then it would instead be triggered by switching between bar and pie charts
        else:
            # except for first call, when no fig has been initialised yet
            if current_fig is not None:
                # map display remains unchanged
                return current_fig

    # if user has selected option to coordinate map markers to category
    if color_coord == 'on':
        # loop through all possible categories in original (unfiltered) dataset
        for i in category_arr:
            # if category is currently selected via category graph
            if i in visible_arr:
                # add corresponding data to map trace
                trace.append(
                    dict(
                        name=i,
                        type='scattermapbox',
                        # each trace handles only the data corresponding to current category
                        lat=filtered_df[filtered_df['category'] == i]['reclat'],
                        lon=filtered_df[filtered_df['category'] == i]['reclong'],
                        text=text,
                        hoverinfo='text',
                        mode='markers',
                        marker=dict(
                            # match category to corresponding color
                            color=discrete_color_map[i],
                            # set marker size proportional to mass
                            size=2 * (np.log(filtered_df[filtered_df['category'] == i]['mass (g)'])),
                            opacity=0.6),
                        # store row id of each data point
                        customdata=filtered_df[filtered_df['category'] == i]['id']
                    )
                )
    else:
        # display all data in filtered df with a constant color
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
                    color='#FF7850',
                    # set marker size proportional to mass
                    size=2 * (np.log(filtered_df['mass (g)'])),
                    opacity=0.6),
                # store row id of each data point
                customdata=filtered_df.id
            )
        )

    # set map-specific layout
    map_layout = dict(
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
    fig = dict(data=trace, layout=map_layout)

    # if user has not selected to coordinate size to mass
    if size == 'off':
        # set constant marker size
        for i in fig['data']:
            i['marker']['size'] = 9

    return fig


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

    # if anything other than input from the <<reset map selection>> button triggered the callback
    if ctx.triggered[0]['prop_id'].split('.')[0] != 'refresh-button':
        # filter by current selection via UI of points on map
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

    # if anything other than input from the <<reset map selection>> button triggered the callback
    if ctx.triggered[0]['prop_id'].split('.')[0] != 'refresh-button':
        # filter by current selection of points on map
        filtered_df = geo_filter(filtered_df, selected_data)

    fig = get_year_graph(filtered_df, discovery)
    content = dcc.Graph(id='year-graph', figure=fig)
    return [content]


# mass tab
# ------------------------------------------------------------------------------
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

    # if anything other than input from the <<reset map selection>> button triggered the callback
    if ctx.triggered[0]['prop_id'].split('.')[0] != 'refresh-button':
        # filter by current selection of points on map
        filtered_df = geo_filter(filtered_df, selected_data)

    fig = get_mass_graph(filtered_df, mass_graph_type, discovery, log_scale)
    content = dcc.Graph(id='mass-graph', figure=fig)
    return content


# category tab control box
# ------------------------------------------------------------------------------
@app.callback(
    Output('category-control-box', 'style'),
    [Input('visualise-by-tabs', 'active_tab')]
)
def display_category_control_box(active_tab):
    # display category tab control box if category tab is currently active
    if active_tab == 'category-tab':
        style = {'display': 'block'}
    # else keep hidden
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
    # display mass tab control box if mass tab is currently active
    if active_tab == 'mass-tab':
        style = {'display': 'block'}
    # else keep hidden
    else:
        style = {'display': 'none'}
    return style


# ------------------------------------------------------------------------------
if __name__ == '__main__':
    app.run_server(debug=False)
