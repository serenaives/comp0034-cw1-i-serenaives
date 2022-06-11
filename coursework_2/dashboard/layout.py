from dash import dcc, html, dash_table
import dash_bootstrap_components as dbc


# mark values for year range slider
year_mark_values = {900: '900', 1100: '1100',
                    1300: '1300', 1500: '1500',
                    1700: '1700', 1900: '1900'}

min_year = 860
max_year = 2012

min_mass = 0.01
max_mass = 60000000.0

# mark values for mass range slider
mass_mark_values = {0: '0',
                    20000000: '20 million',
                    40000000: '40 million',
                    60000000: '60 million'}

# column names for dash_table (corresponding to the dataset columns)
table_cols = ['name', 'fall', 'category', 'year', 'mass (g)']

layout = dbc.Container([

    html.Br(),

    # page header
    # ------------------------------------------------------------------------------
    dbc.Row([
        dbc.CardGroup([
            dbc.Card([html.H1('Meteorite Landings')], style={'align': 'left', 'padding': '1%'}),
            dbc.CardGroup([
                dbc.Card([
                    dbc.Button([
                        'back to main page'
                    ],
                        color='danger',
                        style={'height': '100%'},
                        href='http://127.0.0.1:5000'
                    )
                ], style={'width': '2'}),
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
                                            min=min_year,
                                            max=max_year,
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
                                            min=min_mass,
                                            max=max_mass,
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