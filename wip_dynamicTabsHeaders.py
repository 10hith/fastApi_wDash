import collections
from typing import List,Dict
import dash
import pandas as pd
import numpy as np

from dash.dependencies import Output, Input, State, ALL, MATCH
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc
import plotly.express as px
from plotly.graph_objs import _figure as Figure

import dash_html_components as html
import dash_core_components as dcc
import dash_table
from datetime import datetime

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.SLATE], suppress_callback_exceptions=True)

df = pd.read_csv('/home/basal/PycharmProjects/fastApi_wDash/resources/gapminderDataFiveYear.csv')
hist = pd.read_parquet("/home/basal/PycharmProjects/fastApi_wDash/dm_athena_features_profiled_histogram")\
    .fillna("unknown")\
    .sort_values(by=['column_name', 'ratio'], ascending=False)


# def plot_cat_value(data_store: List[Dict], column_name: str) -> dbc.Card:
#     dyn_df = pd.DataFrame.from_dict(data_store)
#     col_data_store = [x for x in data_store if x["column_name"] == column_name]
#     fig = px.bar(
#         col_data_store,
#         y="cat_value",
#         x="ratio",
#         orientation='h',
#         color="cat_value",
#     )
#
#     card = dbc.Card(children=dbc.CardBody(
#         [
#             html.H4(f"Distribution for Column - '{column_name}' ", className="card-title"),
#             html.H6(f"Viz generated @ {datetime.now()}", className="card-subtitle"),
#             dcc.Store(
#                 id={
#                     'type': 'dynStore',
#                     'index': column_name
#                 },
#                 data=col_data_store
#             ),
#             dcc.Graph(
#                 id={
#                     'type': 'dynGraph',
#                     'index': column_name
#                 },
#                 ),
#             dcc.Graph(
#                 id={
#                     'type': 'dynGraph1',
#                     'index': column_name
#                 },
#                 figure=fig
#             ),
#         ]
#     ),
#     style={"width": "3"},
#     )
#     return card

def plot_cat_value(data_store: List[Dict], column_name: str) -> dbc.Card:
    # dyn_df = pd.DataFrame.from_dict(data_store)
    col_data_store = [x for x in data_store if x["column_name"] == column_name]
    fig = px.bar(
        col_data_store,
        y="cat_value",
        x="ratio",
        orientation='h',
        color="cat_value",
    )

    card = dbc.Card([
        dbc.CardHeader(
            dbc.Tabs(
                [
                    dbc.Tab(
                        label="View Bar Chart",
                        tab_id="tabBarChart",
                        children=[
                            html.Br(),
                            html.H4(f"Distribution for Column - '{column_name}' ", className="card-title"),
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
                            html.H4(f"Distribution for Column - '{column_name}' ", className="card-title"),
                            html.H6(f"Viz generated @ {datetime.now()}", className="card-subtitle"),
                            html.Br(),
                            dcc.Graph(
                                id={
                                    'type': 'dynPieChart',
                                    'index': column_name
                                },
                            )
                        ],

                    ),
                ],
                id={
                    'type': 'dynTabs',
                    'index': column_name
                },
                card=True,
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



app.layout = dbc.Container([
    # card,
    dcc.Store(id='resultStore', data=hist.to_dict('records')),
    dcc.Dropdown(id='columnsDropdown', options=[
        {'value': x, 'label': x} for x in set(hist['column_name'])
    ], multi=True, value=[], disabled=False),
    dcc.Store(id='colsPrevSelected', data=[]),
    html.Div(id="myGraphCollections", children=[]),
])


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

    dcc_store_df = pd.DataFrame.from_dict(data_store)
    new_col = np.setdiff1d(col_selected, cols_prev_selected)

    if new_col.size > 0:
        new_graph=plot_cat_value(data_store, new_col.tolist()[0])
        graphs_prev_displayed.insert(0, new_graph)
        return graphs_prev_displayed, col_selected
    else:
        col_selected.reverse()
        graphs = [plot_cat_value(data_store, col) for col in col_selected]
        return graphs, col_selected


# @app.callback(
#     Output(component_id={'type': 'dynGraph', 'index': MATCH}, component_property='figure'),
#     Input(component_id={'type': 'dynStore', 'index': MATCH}, component_property='data'),
# )
# def on_data_set_dyn_graph(data_store):
#     dyn_df = pd.DataFrame.from_dict(data_store)
#     fig_pie = px.pie(
#         dyn_df,
#         names="cat_value",
#         values="ratio",
#         color="cat_value",
#         # title=f"Distribution for Column -'{column_name}' "
#     )
#     return fig_pie

@app.callback(
    Output(component_id={'type': 'dynPieChart', 'index': MATCH}, component_property='figure'),
    Input(component_id={'type': 'dynStore', 'index': MATCH}, component_property='data'),
)
def on_data_set_dyn_graph(data_store):
    dyn_df = pd.DataFrame.from_dict(data_store)
    fig_pie = px.pie(
        dyn_df,
        names="cat_value",
        values="ratio",
        color="cat_value",
        # title=f"Distribution for Column -'{column_name}' "
    )
    return fig_pie


if __name__ == '__main__':
    app.run_server(host="11.15.93.81", debug=True, threaded=True, port=10450)