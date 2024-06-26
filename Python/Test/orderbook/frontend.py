# Copyright 2023-present Coinbase Global, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import sqlite3
import pandas as pd
from dash import html, dcc, Output, Input, Dash, dash_table
from backend import product_id, agg_level, row_count

app = Dash(__name__)

app.layout = html.Div([
    html.H1(id='mid-price'),
    dcc.Interval(id='update', interval=1000),
    dash_table.DataTable(id='my-table',
                         columns=[
                             {'name': 'Price', 'id': 'price', 'type': 'text'},
                             {'name': 'Qty', 'id': 'size', 'type': 'text'},
                         ],
                         style_data_conditional=[
                             {
                                 'if': {
                                     'column_id': 'price',
                                     'filter_query': '{id} contains "bid"'
                                 },
                                 'backgroundColor': '#50C878'
                             },
                             {
                                 'if': {
                                     'column_id': 'price',
                                     'filter_query': '{id} contains "ask"'
                                 },
                                 'backgroundColor': '#DC143C'
                             },
                             {
                                 'if': {
                                     'column_id': 'size',
                                     'filter_query': '{id} contains "ask"'
                                 },
                                 'backgroundColor': '#FAA0A0'
                             },
                             {
                                 'if': {
                                     'column_id': 'size',
                                     'filter_query': '{id} contains "bid"'
                                 },
                                 'backgroundColor': '#C1E1C1'
                             }
                         ],
                         style_cell={'font-family': 'Courier New'}
                         )

], style={'width': '30%', 'font-family': 'Arial'}, )


@app.callback(
    Output('mid-price', 'children'),
    Input('update', 'n_intervals'),
)
def update_mid(intervals):
    df = load_data()

    max_bid = df.loc[df['id'].str.contains('bid'), 'price'].max()

    one_usd = '1'
    if agg_level == one_usd:
        max_bid = int(max_bid)

    return f'{product_id}: {max_bid}'


@app.callback(
    Output('my-table', 'data'),
    Input('update', 'n_intervals'),
)
def update_table(intervals):
    df = load_data()

    return df.to_dict(orient='records')


def load_data():
    conn = sqlite3.connect('prime_orderbook.db')
    cursor = conn.cursor()

    query = f'SELECT * FROM book ORDER BY id + 0 ASC LIMIT {row_count}'

    data = cursor.execute(query)

    df = pd.DataFrame(data)

    df.columns = ['index', 'price', 'size', 'id']
    df = df.sort_values(by=['price'], ascending=False)

    return df


if __name__ == '__main__':
    app.run_server(debug=True)
