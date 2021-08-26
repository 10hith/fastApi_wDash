import collections
import dash
import pandas as pd
import numpy as np

from dash.dependencies import Output, Input, State
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc
import plotly.express as px
from plotly.graph_objs import _figure as Figure

import dash_html_components as html
import dash_core_components as dcc
import dash_table
from datetime import datetime

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP], suppress_callback_exceptions=True)

df = pd.read_csv('/home/basal/PycharmProjects/fastApi_wDash/resources/gapminderDataFiveYear.csv')
hist = pd.read_parquet("/home/basal/PycharmProjects/fastApi_wDash/dm_athena_features_profiled_histogram")\
    .fillna("unknown")\
    .sort_values(by=['column_name', 'ratio'], ascending=False)


def plot_cat_value(df: pd.DataFrame, column_name: str) -> dbc.Card:
    filtered_df = df.query(f"column_name == '{column_name}' ")
    fig = px.bar(
        filtered_df,
        y="cat_value",
        x="ratio",
        orientation='h',
        color="cat_value",
        # title=f"Distribution for Column -'{column_name}' "
    )
    card = dbc.Card(id={
        'type': 'dynamic-dropdown',
        'index': column_name
    }, children=dbc.CardBody(
        [
            html.H4(f"Distribution for Column - '{column_name}' ", className="card-title"),
            html.H6(f"Viz generated @ {datetime.now()}", className="card-subtitle"),
            # html.P(
            #     "Below is the",
            #     className="card-text",
            # ),
            dcc.Graph(figure=fig)
        ]
    ),
    style={"width": "3"},
    )
    return card
    # return dcc.Graph(figure=fig)


app.layout = dbc.Container([
    # card,
    dcc.Store(id='resultStore', data=hist.to_dict('records')),
    dcc.Dropdown(id='columnsDropdown', options=[
        {'value': x, 'label': x} for x in set(hist['column_name'])
    ], multi=True, value=[], disabled=False),
    dcc.Store(id='colsPrevSelected', data=[]),
    html.Div(id="myGraphCollections", children=[]),
    html.Div(id="myGraphCollectionsPrev"),
])


# @app.callback(Output('resultStore', 'data'),
#               Input('columnsDropdown', 'value'))
# def filter_countries(columns_selected):
#     if not columns_selected:
#         # Return all the rows on initial load/no country selected.
#         return hist.to_dict('records')
#     filtered = hist.query('column_name in @columns_selected')
#     return filtered.to_dict('records')


# @app.callback(Output('myGraphCollections', 'children'),
#               Input('resultStore', 'data'),
#               Input('columnsDropdown', 'value'))
# def on_data_set_graph(data, columnsSelected):
#     # if data is None:
#     #     raise PreventUpdate
#
#     dcc_store_df = pd.DataFrame.from_dict(data)
#     columnsSelected.reverse()
#     graphs = [plot_cat_value(dcc_store_df, col) for col in columnsSelected]
#     return graphs

# @app.callback(Output('colsPrevSelected', 'data'),
#               Input('columnsDropdown', 'value')
#               )
# def capture_cols_selected_state(columns_selected):
#     print(f"Columns Previously selected are ")
#     [print(x) for x in columns_selected]
#     return columns_selected
#
#
# @app.callback(Output('colsPrevSelected', 'data'),
#               Input('columnsDropdown', 'value')
#               )
# def capture_cols_selected_state(columns_selected):
#     print(f"Columns Previously selected are ")
#     [print(x) for x in columns_selected]
#     return columns_selected



@app.callback([Output('myGraphCollections', 'children'),
              Output('colsPrevSelected', 'data')],
              [Input('resultStore', 'data'),
              Input('columnsDropdown', 'value')],
              [State('colsPrevSelected', 'data'),
              State('myGraphCollections', 'children')],
              prevent_initial_call=True
              )
def on_data_set_graph(data, col_selected, cols_prev_selected, graphs_prev_displayed):
    if col_selected is None:
        raise PreventUpdate

    dcc_store_df = pd.DataFrame.from_dict(data)
    new_col = np.setdiff1d(col_selected, cols_prev_selected)

    if new_col.size > 0:
        new_graph=plot_cat_value(dcc_store_df, new_col.tolist()[0])
        graphs_prev_displayed.insert(0, new_graph)
        return graphs_prev_displayed, col_selected
    else:
        col_selected.reverse()
        graphs = [plot_cat_value(dcc_store_df, col) for col in col_selected]
        return graphs, col_selected


if __name__ == '__main__':
    app.run_server(host="11.15.93.81", debug=True, threaded=True, port=10450)