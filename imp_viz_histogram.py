import pandas as pd
import dash
import dash_labs as dl
import dash_html_components as html
import dash_core_components as dcc
import dash_table
from dash.dependencies import Output, Input
from dash.exceptions import PreventUpdate


import numpy as np
import plotly.express as px
import dash_bootstrap_components as dbc


import time

app = dash.Dash(__name__,
                plugins=[dl.plugins.FlexibleCallbacks()],
                title="My Sidebar",
                external_stylesheets=[dbc.themes.BOOTSTRAP] ## This get overridden by template
                )
tpl = dl.templates.DbcCard(app, title="Manual Update", theme=dbc.themes.BOOTSTRAP)

hist = pd.read_csv("histogram.csv").fillna("unknown")



"""
A few things happening here - 
1) I was able to get create a call back for a component in template
2) if specifying output=tpl.graph_output(), then just return fig; Else return fig within a Graph object
3) 
"""

## Call back without the use of dcc.store
@app.callback(
    args=dict(
        column_selected=tpl.dropdown_input(options = hist['column_name'].unique().tolist(),
                                           label="input", id="dropdownInput"),

    ),
    # output=tpl.graph_output(),
    template=tpl,
)
def display_histogram(column_selected):
    filtered_hist = hist.query(f"column_name == '{column_selected}' ")
    fig = px.histogram(filtered_hist, x="cat_value", y="ratio", color="cat_value",)
    # return fig
    return dcc.Graph(figure=fig)


@app.callback(Output('dccStore', 'data'),
              Input('dropdownInput', 'value'))
def filter_countries(column_selected):
    # if not column_selected:
    #     # Return all the rows on initial load/no country selected.
    #     return hist.to_dict('records')
    filtered_hist = hist.query(f"column_name == '{column_selected}' ")

    return filtered_hist.to_dict('records')


@app.callback(
    output = dict(data=Output('dataTable', 'data')),
    args = dict(dccStore = Input('dccStore', 'data'))
)
def on_data_set_table(dccStore):
    if dccStore is None:
        raise PreventUpdate
    return dict(data=dccStore)



app.layout = html.Div([
    dcc.Store(id='dccStore'),
    dbc.Row(
        dbc.Col(
            [dbc.Container(fluid=True, children=tpl.children),], width={"size": 8, "offset": 0})
    ),
    dbc.Row(
        dbc.Col([
        dash_table.DataTable(
        id='dataTable',
        columns=[{'name': i, 'id': i} for i in hist.columns]
        )], width={"size": 6, "offset": 0}
        )
    ),
    ]
)

if __name__ == "__main__":
    app.run_server(debug=True)