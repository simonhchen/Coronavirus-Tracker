from urllib.request import urlopen
import json
import pandas as pd

import dash
import dash_table
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.express as px

counties_df = pd.read_csv("https://raw.githubusercontent.com/nytimes/covid-19-data/master/us-counties.csv",
                          dtype={"fips": str})

states_df = pd.read_csv("https://raw.githubusercontent.com/nytimes/covid-19-data/master/us-states.csv",
                        dtype={"fips": str})

def generate_table(dataframe, max_rows=1000):
    return html.Table([
        html.Thead(
            html.Tr([html.Th(col) for col in dataframe.columns])
        ),
        html.Tbody([
            html.Tr([
                html.Td(dataframe.iloc[i][col]) for col in dataframe.columns
            ]) for i in range(min(len(dataframe), max_rows))
        ])
    ])

PAGE_SIZE = 5

with urlopen('https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json') as response:
    counties = json.load(response)

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

colors = {'background': '#111111',
          'text': '#7FDBFF'}

fig_1 = px.choropleth_mapbox(counties_df, geojson=counties, locations='fips', color='cases',
                             color_continuous_scale="Viridis",
                             range_color=(0, 50000),
                             mapbox_style="carto-positron",
                             zoom=3, center = {"lat": 37.0902, "lon": -95.7129},
                             opacity=0.5,
                             labels={'cases':'cases'}
                             )
fig_1.update_layout(margin={"r":0,"t":0,"l":0,"b":0})

fig_2 = px.line(states_df, x='date', y='cases', color='state')

fig_2.update_layout(
    hovermode='x unified',
    updatemenus=[
        dict(
            type = "buttons",
            direction = "left",
            buttons=list([
                dict(
                    args=[{"yaxis.type": "linear"}],
                    label="LINEAR",
                    method="relayout"
                ),
                dict(
                    args=[{"yaxis.type": "log"}],
                    label="LOG",
                    method="relayout"
                )
            ]),
        ),
    ]
)

app = dash.Dash(__name__,  external_stylesheets=external_stylesheets)

app.layout = html.Div(children=[
    html.H1(children='COVID-19 Cases in the US',
            style={'textAlign': 'center'}
            ),

    html.Div(children='COVID-19 Cases by County in the United States.',
             style={'textAlign': 'center'}
             ),

    dcc.Graph(figure=fig_1),

    html.H2(children='Line/Log Graph of COVID-19 Cases in the US',
            style={'textAlign': 'center'}),

    dcc.Graph(figure=fig_2),

    html.H4(children='US COVID-19 Cases'),
    dash_table.DataTable(
        id='datatable-paging',
        columns=[
            {"name": i, "id": i} for i in sorted(counties_df.columns)
        ],
        page_current=0,
        page_size=PAGE_SIZE,
        page_action='custom',

        filter_action='custom',
        filter_query=''
        ),

])

operators = [['ge ', '>='],
             ['le ', '<='],
             ['lt ', '<'],
             ['gt ', '>'],
             ['ne ', '!='],
             ['eq ', '='],
             ['contains '],
             ['datestartswith ']]

def split_filter_part(filter_part):
    for operator_type in operators:
        for operator in operator_type:
            if operator in filter_part:
                name_part, value_part = filter_part.split(operator, 1)
                name = name_part[name_part.find('{') + 1: name_part.rfind('}')]

                value_part = value_part.strip()
                v0 = value_part[0]
                if (v0 == value_part[-1] and v0 in ("'", '"', '`')):
                    value = value_part[1: -1].replace('\\' + v0, v0)
                else:
                    try:
                        value = float(value_part)
                    except ValueError:
                        value = value_part

                # word operators need spaces after them in the filter string,
                # but we don't want these later
                return name, operator_type[0].strip(), value

    return [None] * 3


@app.callback(
    Output('datatable-paging', "data"),
    [Input('datatable-paging', "page_current"),
     Input('datatable-paging', "page_size"),
     Input('datatable-paging', "filter_query")])
def update_table(page_current, page_size, filter):
    print(filter)
    filtering_expressions = filter.split(' && ')
    dff = counties_df
    for filter_part in filtering_expressions:
        col_name, operator, filter_value = split_filter_part(filter_part)

        if operator in ('eq', 'ne', 'lt', 'le', 'gt', 'ge'):
            # these operators match pandas series operator method names
            dff = dff.loc[getattr(dff[col_name], operator)(filter_value)]
        elif operator == 'contains':
            dff = dff.loc[dff[col_name].str.contains(filter_value)]
        elif operator == 'datestartswith':
            # this is a simplification of the front-end filtering logic,
            # only works with complete fields in standard format
            dff = dff.loc[dff[col_name].str.startswith(filter_value)]

    return dff.iloc[
        page_current*page_size:(page_current+ 1)*page_size
    ].to_dict('records')


if __name__ == '__main__':
    app.run_server(debug=True)

