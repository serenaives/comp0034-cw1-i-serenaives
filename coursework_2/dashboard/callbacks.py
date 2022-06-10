from pathlib import Path
import numpy as np
import pandas as pd
from dash.dependencies import Input, Output, State
from dash._callback_context import callback_context as ctx
import plotly.graph_objects as go
import plotly.express as px
from dash import dcc

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

# Import data
# ---------------------------------------------------------------------------------
fp = Path(__file__).parent.parent.parent.joinpath('meteorite_landings_cleaned.csv')
df = pd.read_csv(fp)

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
    df_count = filtered_df.groupby(['year', 'fall'])['name'].count().unstack(fill_value=0).stack().reset_index()
    df_count.columns = ['year', 'fall', 'count']
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
        xaxis_title='Year',
    )
    fig.update_yaxes(rangemode='tozero')

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


def register_callbacks(dashapp):
    # geographical scatter map
    # ------------------------------------------------------------------------------
    @dashapp.callback(
        [Output('map-plot', 'figure'),
         Output('map-plot', 'selectedData')],
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
    def update_map(years_selected, discovery, color_coord, n_clicks, mass_selected, size, cat_selected, selected_data,
                   current_fig):
        filtered_df = get_filtered_df(years_selected, discovery, mass_selected)
        text = filtered_df.name
        trace = []
        selectedData = None

        # if anything other than input from the <<reset map selection>> button triggered the callback
        if ctx.triggered[0]['prop_id'].split('.')[0] != 'refresh-button':
            # filter by current selection of points on map
            filtered_df = geo_filter(filtered_df, selected_data)
            # keep the same selection of points as before
            selectedData = selected_data

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
                    return [current_fig, selected_data]

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

        return [fig, selectedData]

    # interactive table
    # ------------------------------------------------------------------------------
    @dashapp.callback(
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
    @dashapp.callback(
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
    @dashapp.callback(
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
    @dashapp.callback(
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
    @dashapp.callback(
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
    @dashapp.callback(
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
