#To Do
# Tabs can be disabled
# Conditional formatting and filters for the datatable - reuseable code, along with tool tips
# Enhance bar graph with "update traces"
# Try using dashlabs.plugins to group output components

import collections
from typing import List,Dict
import dash
import pandas as pd
import numpy as np

from dash.dependencies import Output, Input, State, ALL, MATCH
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc
import plotly.express as px


import dash_html_components as html
import dash_core_components as dcc
import dash_table
from datetime import datetime

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP], suppress_callback_exceptions=True)

hist = pd.read_parquet("/home/basal/PycharmProjects/fastApi_wDash/dm_athena_features_profiled_histogram")\
    .fillna("unknown")\
    .sort_values(by=['column_name', 'ratio'], ascending=False)


def create_dynamic_card(data_store: List[Dict], column_name: str) -> dbc.Card:
    """
    Creates a card block with tabs for bar chart, pie chart and a data table
    :param data_store: Data store containing the value distribution
    :param column_name: Column for which the card block will be created
    :return: A card block
    """
    col_data_store = [x for x in data_store if x["column_name"] == column_name]
    fig = px.bar(
        col_data_store,
        y="cat_value",
        x="ratio",
        orientation='h',
        color="cat_value",
        text='num_occurrences'
    )

    card = dbc.Card([
        html.H4(f"Distribution for Column - '{column_name}' ", className="card-title"),
        html.H6(f"Viz generated @ {datetime.now()}", className="card-subtitle"),
        dbc.CardHeader(
            dbc.Tabs(
                [
                    dbc.Tab(
                        label="View Bar Chart",
                        tab_id="tabBarChart",
                        children=[
                            html.Br(),
                            html.H6(f"Viz generated @ {datetime.now()}", className="card-subtitle"),
                            html.Br(),
                            dcc.Graph(
                            id={
                                'type': 'dynBarChart',
                                'index': column_name
                            },
                            figure=fig
                            )
                        ],
                    ),
                    dbc.Tab(
                        label="View Pie Chart",
                        tab_id="tabPieChart",
                        children=[
                            html.Br(),
                            html.Br(),
                            dcc.Graph(
                                id={
                                    'type': 'dynPieChart',
                                    'index': column_name
                                },
                            )
                        ],

                    ),
                    dbc.Tab(
                        label="View Data",
                        tab_id="tabData",
                        children=[
                            html.Br(),
                            html.Br(),
                            dash_table.DataTable(
                                id={
                                    'type': 'dynDataTable',
                                    'index': column_name
                                },
                                # columns=[{"name": i, "id": i} for i in col_data_store[0].keys()],
                                # data=col_data_store,
                            )
                        ],

                    ),
                ],
                active_tab="tabBarChart",
            )
        ),
        dbc.CardBody(
            id={
                'type': 'dynCardBody',
                'index': column_name
            },
        children=[
            dcc.Store(
                id={
                    'type': 'dynStore',
                    'index': column_name
                },
                data=col_data_store
            ),
        ]
    )],
    style={"width": "3"},
    )
    return card

app.layout = dbc.Container(
    [
    dcc.Store(id='resultStore', data=hist.to_dict('records')),
    html.Br(),
    dcc.Dropdown(id='columnsDropdown', options=[
        {'value': x, 'label': x} for x in set(hist['column_name'])
    ], multi=True, value=[], disabled=False),
    dcc.Store(id='colsPrevSelected', data=[]),
    html.Br(),
    html.Div(id="myGraphCollections", children=[]),
]
)


@app.callback([Output('myGraphCollections', 'children'),
              Output('colsPrevSelected', 'data')],
              [Input('resultStore', 'data'),
              Input('columnsDropdown', 'value')],
              [State('colsPrevSelected', 'data'),
              State('myGraphCollections', 'children')],
              prevent_initial_call=True
              )
def on_data_set_graph(data_store, col_selected, cols_prev_selected, graphs_prev_displayed):
    if col_selected is None:
        raise PreventUpdate
    new_col = np.setdiff1d(col_selected, cols_prev_selected)

    if new_col.size > 0:
        new_graph=create_dynamic_card(data_store, new_col.tolist()[0])
        graphs_prev_displayed.insert(0, new_graph)
        return graphs_prev_displayed, col_selected
    else:
        col_selected.reverse()
        graphs = [create_dynamic_card(data_store, col) for col in col_selected]
        return graphs, col_selected


'''
Creating Dynamic components based on the column selection. This call back will occur
'''
@app.callback(
    [
        Output(component_id={'type': 'dynPieChart', 'index': MATCH}, component_property='figure'),
        Output(component_id={'type': 'dynDataTable', 'index': MATCH}, component_property='columns'),
        Output(component_id={'type': 'dynDataTable', 'index': MATCH}, component_property='data'),
        Output(component_id={'type': 'dynDataTable', 'index': MATCH}, component_property='style_data_conditional'),
        ],
    Input(component_id={'type': 'dynStore', 'index': MATCH}, component_property='data'),
)
def on_data_set_dyn_graph(col_data_store):
    fig_pie = px.pie(
        col_data_store,
        names="cat_value",
        values="ratio",
        color="cat_value",
    )
    columns = [{"name": i, "id": i} for i in col_data_store[0].keys()]
    data = col_data_store
    # Conditional styling for the data table
    style_data_conditional=[
        {
            'if': {
                'column_id': 'column_name',
            },
            'hidden': 'True',
            'color': 'white'
        }
    ]
    return fig_pie, columns, data, style_data_conditional


if __name__ == '__main__':
    app.run_server(host="11.15.93.81", debug=True, threaded=True, port=10450)