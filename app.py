import dash
from dash import Dash, html, dcc, Input, Output, dash_table, State
import dash_bootstrap_components as dbc

# from dash import html, dcc
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd

import datetime as dt
from datetime import datetime

import requests
import json
import os

FONT_AWESOME = "https://use.fontawesome.com/releases/v5.10.2/css/all.css"

# Initialize the app
app = dash.Dash(__name__, external_stylesheets=[
                dbc.themes.DARKLY, FONT_AWESOME])

# documentacao em: http://apiadvisor.climatempo.com.br/doc/index.html
iTOKEN = "3a81f89f4b77bd693f6232f5ffb39ab6"
iCIDADE = "3907"

# Codigo do tipo da consulta
DATAFROM = 1
iTIPOCONSULTA = 5

# Inicializa os dados
fileslist = []
for root, dirs, files in os.walk(r'data/'):
    for name in files:
        # As we need to get the provided python file,
        # comparing here like this
        fileslist.append(str(os.path.abspath(os.path.join(root, name))))
        if name == 'current.csv':
            data_current = pd.read_csv(
                str(os.path.abspath(os.path.join(root, name))))

data_prediction = pd.read_csv(fileslist[-1])


def GetPrediction():
    global data_prediction

    # 5=Previsao para as proximas 72 horas
    if iTIPOCONSULTA == 5:
        iURL = "http://apiadvisor.climatempo.com.br/api/v1/forecast/locale/" + \
            iCIDADE + "/hours/72?token=" + iTOKEN
        iRESPONSE = requests.request("GET", iURL)
        iRETORNO_REQ = json.loads(iRESPONSE.text)
        # print(iRETORNO_REQ)

        idata = []
        itemp = []
        ihumi = []
        ipres = []
        irain = []
        iwin1 = []
        iwin2 = []
        iwin3 = []
        iwin4 = []
        for iCHAVE in iRETORNO_REQ['data']:
            idata.append(iCHAVE.get('date_br'))
            itemp.append(iCHAVE['temperature']['temperature'])
            ihumi.append(iCHAVE['humidity']['humidity'])
            ipres.append(iCHAVE['pressure']['pressure'])
            irain.append(iCHAVE['rain']['precipitation'])
            iwin1.append(iCHAVE['wind']['direction'])
            iwin2.append(iCHAVE['wind']['directiondegrees'])
            iwin3.append(iCHAVE['wind']['gust'])
            iwin4.append(iCHAVE['wind']['velocity'])

            # print("data:" + str(iDATA) + " " + str(iTEMPERATURA) + "º" + "\n")

    data_prediction = pd.DataFrame(list(zip(idata, itemp, ihumi, ipres, irain, iwin1, iwin2, iwin3, iwin4)),
                                   columns=['date', 'temperature', 'humidity', 'pressure', 'precipitation', 'direction', 'directiondegrees', 'gust', 'velocity'])

    # Load data
    data_prediction.index = pd.to_datetime(data_prediction['date'])

    # datetime object containing current date and time
    now = datetime.now()
    dt_string = now.strftime("%d-%m-%Y-%H-%M-%S")
    data_prediction.to_csv('data/prediction-dmY-HMS-' + dt_string + '.csv')


def GetCurrentData():
    global data_current

    iURL = "http://apiadvisor.climatempo.com.br/api/v1/weather/locale/" + \
        iCIDADE + "/current?token=" + iTOKEN
    iRESPONSE = requests.request("GET", iURL)
    iRETORNO_REQ = json.loads(iRESPONSE.text)

    new_row = {}
    for iCHAVE in iRETORNO_REQ['data']:
        new_row[iCHAVE] = iRETORNO_REQ['data'][iCHAVE]

    data_current.loc[len(data_current)] = new_row
    nome = ['temperature', 'wind_direction', 'wind_velocity',
            'humidity', 'condition', 'pressure', 'icon', 'sensation', 'date']
    data_current2 = data_current[nome]

    data_current.to_csv('data/current.csv', index=False)


def drawFigure2A(varplot1, varplot2, h):
    return html.Div([
        dbc.Card(
            dbc.CardBody([
                dcc.Graph(
                    figure=drawFigureBasic2A(varplot1, varplot2, h),
                    config={
                        'displayModeBar': False
                    }
                )
            ]), color="secondary", inverse=True,
        ),
    ])


def drawFigure2Abar(varplot1, varplot2, h):
    return html.Div([
        dbc.Card(
            dbc.CardBody([
                dcc.Graph(
                    figure=drawFigureBasic2Abar(varplot1, varplot2, h),
                    config={
                        'displayModeBar': False
                    }
                )
            ]), color="secondary", inverse=True,
        ),
    ])


def drawFigureBasic2A(varplot1, varplot2, h):
    # Create figure with secondary y-axis
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    fig.add_trace(go.Scatter(
        x=data_prediction['date'],
        y=data_prediction[varplot1],
        mode="lines+markers+text",
        name="<b>" + varplot1 + "</b>",
        # text=data_prediction[varplot1].round(1),
        # textposition="bottom right"
    ),
        secondary_y=False,
    )

    fig.add_trace(go.Scatter(
        x=data_prediction['date'],
        y=data_prediction[varplot2],
        mode="lines+markers+text",
        name="<b>" + varplot2 + "</b>",
        # text=data_prediction[varplot2].round(1),
        #    textposition="top left"
    ),
        secondary_y=True,
    )

    fig.update_yaxes(title_text="<b>" + varplot1 + "</b>", secondary_y=False)
    fig.update_yaxes(title_text="<b>" + varplot2 + "</b>", secondary_y=True)
    fig.update_xaxes(title_text="<b> Hour </b>")
    fig.update_yaxes(automargin=True)
    fig.update_layout(
        template='plotly_dark',
        legend=dict(
            orientation="h",  # entrywidth=100,
            yanchor="bottom",
            y=1.0,
            xanchor="center",
            x=0.5,
            # font=dict(
            #    family="Courier",
            #    size=25,
            #    ),
        ),
        margin=dict(l=20, r=0, t=20, b=70, pad=5),
        height=h
        # paper_bgcolor="LightSteelBlue",
    )

    return fig


def drawFigureBasic2Abar(varplot1, varplot2, h):
    # Create figure with secondary y-axis
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    fig.add_trace(go.Bar(
        x=data_prediction['date'],
        y=data_prediction[varplot1],
        name="<b>" + varplot1 + "</b>",
        # text=data_prediction[varplot1].round(1),
        # textposition="bottom right"
    ),
        secondary_y=False,
    )

    fig.add_trace(go.Scatter(
        x=data_prediction['date'],
        y=data_prediction[varplot2],
        mode="lines+markers+text",
        name="<b>" + varplot2 + "</b>",
        # text=data_prediction[varplot2].round(1),
        #    textposition="top left"
    ),
        secondary_y=True,
    )

    fig.update_yaxes(title_text="<b>" + varplot1 + "</b>", secondary_y=False)
    fig.update_yaxes(title_text="<b>" + varplot2 + "</b>", secondary_y=True)
    fig.update_xaxes(title_text="<b> Hour </b>")
    fig.update_yaxes(automargin=True)
    fig.update_layout(
        template='plotly_dark',
        legend=dict(
            orientation="h",  # entrywidth=100,
            yanchor="bottom",
            y=1.0,
            xanchor="center",
            x=0.5,
            # font=dict(
            #    family="Courier",
            #    size=25,
            #    ),
        ),
        margin=dict(l=20, r=0, t=20, b=70, pad=5),
        height=h
        # paper_bgcolor="LightSteelBlue",
    )

    return fig


def drawText1(Text1, Text2, cor):
    return html.Div([
        dbc.Card(
            dbc.CardBody([
                html.Div([
                    html.H6(Text1, className="card-title"),
                    html.H2(Text2, className="card-text"),
                ], style={'textAlign': 'center'})
            ]), color=cor, inverse=True
        ),
    ])


def drawText2(Text1, Text2, cor):
    return html.Div([
        dbc.Card(
            dbc.CardBody([
                html.Div([
                    html.H6(Text1, className="card-title"),
                    html.H5(Text2, className="card-text"),
                ], style={'textAlign': 'center'})
            ]), color=cor, inverse=True
        ),
    ])


card_icon = {
    "color": "white",
    "textAlign": "center",
    "fontSize": 30,
    "margin": "auto",
}


def drawTextGroup(Text1, Text2, fafa, bgcolor):
    return html.Div([
        dbc.CardGroup(
            [
                dbc.Card(
                    dbc.CardBody([
                        html.Div([
                            html.H6(Text1, className="card-title"),
                            html.H2(Text2, className="card-text"),
                        ], style={'textAlign': 'center'})
                    ]), color="primary", inverse=True
                ),
                dbc.Card(
                    html.Div(className=fafa, style=card_icon),
                    className=bgcolor,
                    style={"maxWidth": 75},
                ),
            ], className="mt-0 shadow",
        )
    ])


def drawFigurePredictionReal(n):

    varplot1 = 'temperature'
    varplot2 = 'directiondegrees'
    h = 460
    return html.Div([
        dbc.Card(
            dbc.CardBody([
                dcc.Graph(
                    figure=drawFigureBasicPrediction(varplot1, varplot2, h),
                    config={
                        'displayModeBar': False
                    }
                )
            ]), color="secondary", inverse=True,
        ),
    ])

# Iris bar figure


def drawFigureBasicPrediction(varplot1, varplot2, h):
    fileslist = []
    for root, dirs, files in os.walk(r'data/'):
        for name in files:
            # As we need to get the provided python file,
            # comparing here like this
            fileslist.append(str(os.path.abspath(os.path.join(root, name))))

    fn24 = fileslist[-1]
    df24 = pd.read_csv(fn24)
    print(fn24)

    fn48 = fileslist[-2]
    df48 = pd.read_csv(fn48)
    print(fn48)

    fn72 = fileslist[-3]
    df72 = pd.read_csv(fn72)
    print(fn72)

    df24['date'] = pd.to_datetime(df24['date']) + pd.Timedelta(-3, unit='H')
    df48['date'] = pd.to_datetime(df48['date']) + pd.Timedelta(-3, unit='H')
    df72['date'] = pd.to_datetime(df72['date']) + pd.Timedelta(-3, unit='H')

    # Create figure with secondary y-axis
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    fig.add_trace(go.Scatter(
        x=df24['date'],
        y=df24[varplot1],
        mode="lines+markers+text",
        name="<b>" + fn24[-31:-4] + "</b>",
        # text=df[varplot1].round(1),
        # textposition="bottom right"
    ),
        secondary_y=False,
    )

    fig.add_trace(go.Scatter(
        x=df48['date'],
        y=df48[varplot1],
        mode="lines+markers+text",
        name="<b>" + fn48[-31:-4] + "</b>",
        # text=df[varplot2].round(1),
        #    textposition="top left"
    ),
        secondary_y=False,
    )

    fig.add_trace(go.Scatter(
        x=df72['date'],
        y=df72[varplot1],
        mode="lines+markers+text",
        name="<b>" + fn72[-31:-4] + "</b>",
        # text=df[varplot2].round(1),
        #    textposition="top left"
    ),
        secondary_y=False,
    )

    fig.add_trace(go.Scatter(
        x=data_current['date'],
        y=data_current['temperature'],
        mode="lines+markers+text",
        name="<b> AGORA </b>",
        marker=dict(size=8, color='darkred'),
    ),
        secondary_y=False,
    )

    fig.update_yaxes(title_text="<b>" + varplot1 + "</b>", secondary_y=False)
    fig.update_xaxes(title_text="<b> Hour </b>")
    fig.update_yaxes(automargin=True)
    fig.update_layout(
        template='plotly_dark',
        legend=dict(
            orientation="h",  # entrywidth=100,
            yanchor="bottom",
            y=1.0,
            xanchor="center",
            x=0.5,
            # font=dict(
            #    family="Courier",
            #    size=25,
            #    ),
        ),
        margin=dict(l=20, r=0, t=20, b=70, pad=5),
        height=h
        # paper_bgcolor="LightSteelBlue",
    )

    return fig


@app.callback(Output('live-update-text-group1', 'children'),
              Input('interval-component-fast', 'n_intervals'))
def update_group1(n):
    return [drawTextGroup('temperature', str(data_current['temperature'].iloc[-1]) + "º",
                          "fa fa-thermometer-half", "bg-danger")]


@app.callback(Output('live-update-text-group2', 'children'),
              Input('interval-component-fast', 'n_intervals'))
def update_group2(n):
    return [drawTextGroup('sensation', str(data_current['sensation'].iloc[-1]) + "º",
                          "fa fa-thermometer-half", "bg-danger")]


@app.callback(Output('live-update-text-group3', 'children'),
              Input('interval-component-fast', 'n_intervals'))
def update_group3(n):
    return [
        drawTextGroup('humidity', str(round(data_current['humidity'].iloc[-1])) +
                      "%", "fa fa-tint", "bg-warning")
    ]


@app.callback(Output('live-update-text-group4', 'children'),
              Input('interval-component-fast', 'n_intervals'))
def update_group4(n):
    return [
        drawText1('condition', str(
            data_current['condition'].iloc[-1]), "primary")
    ]


@app.callback(Output('live-update-text-group5', 'children'),
              Input('interval-component-fast', 'n_intervals'))
def update_group5(n):
    return [
        drawText2('pressure', str(
            round(data_current['pressure'].iloc[-1])) + "hPa", "success")
    ]


@app.callback(Output('live-update-text-group6', 'children'),
              Input('interval-component-fast', 'n_intervals'))
def update_group6(n):
    return [
        drawText2('wind_velocity', str(
            data_current['wind_velocity'].iloc[-1]) + "km/h", "success")
    ]


@app.callback(Output('live-update-text-group7', 'children'),
              Input('interval-component-fast', 'n_intervals'))
def update_group7(n):
    return [
        drawText2('wind_direction', str(
            data_current['wind_direction'].iloc[-1]), "success")
    ]


@app.callback(Output('live-update-text-date', 'children'),
              Input('interval-component-veryfast', 'n_intervals'))
def update_metrics(n):

    now = datetime.now()
    dt_string = now.strftime("%b-%d-%Y %H:%M:%S")
    return [html.H6(dt_string),
            ]


@app.callback(Output('live-update-text-current', 'children'),
              Input('interval-component-fast', 'n_intervals'))
def update_metrics(n):

    GetCurrentData()
    now = datetime.now()
    dt_string = now.strftime("%b-%d-%Y %H:%M:%S")
    return [html.H6('Current Data Updated at: ' + dt_string),
            ]


@app.callback(Output('live-update-text-prediction', 'children'),
              Input('interval-component-slow', 'n_intervals'))
def update_metrics(n):

    GetPrediction()
    now = datetime.now()
    dt_string = now.strftime("%b-%d-%Y %H:%M:%S")
    return [html.H6('Prediction Updated at: ' + dt_string),
            ]


@app.callback(Output('live-update-graph1', 'children'),
              Input('interval-component-fast', 'n_intervals'))
def drawFigure1(n):
    return [
    drawFigure2A("temperature", "humidity", 300)
]


@app.callback(Output('live-update-graph2', 'children'),
              Input('interval-component-fast', 'n_intervals'))
def drawFigure2(n):
    return [
    drawFigure2Abar("precipitation", "pressure", 300)
]


@app.callback(Output('live-update-graph3', 'children'),
              Input('interval-component-fast', 'n_intervals'))
def drawFigure3(n):
    return (drawFigurePredictionReal(n))


# GetCurrentData()
# GetPrediction()
# data_current[0], data_current[1] + "º", "fa fa-spinner fa-spin fa-3x fa-fw", "bg-danger")
# https://fontawesome.com/v4/examples/
app.layout = html.Div([
            dbc.CardGroup(
            [
                dbc.Card(
                    dbc.CardBody([
                        html.Div(html.H3('Data Agregator')
                        )
                    ]
                    ), color="secondary", inverse=True
                    )
            ], className="mt-0 shadow",
        ),
    dbc.Card(
        dbc.CardBody([
            dbc.Row([
                dbc.Col([
                    drawText2('EEL', "WeatherAI", "secondary")
                ], width=1),
                dbc.Col(id='live-update-text-group1', width=2),
                dbc.Col(id='live-update-text-group2', width=2),
                dbc.Col(id='live-update-text-group3', width=2),
                dbc.Col(id='live-update-text-group4', width=2),
                dbc.Col(id='live-update-text-group5', width=1),
                dbc.Col(id='live-update-text-group6', width=1),
                dbc.Col(id='live-update-text-group7', width=1),

            ], align='center'),
        ]), color='dark'
    ),
    html.Div([
        dbc.Card(
            dbc.CardBody([
                dbc.Row([
                    dbc.Col(id='live-update-graph1', width=6),
                    dbc.Col(id='live-update-graph2', width=6),
                    dbc.Col(id='live-update-graph3', width=12),
                ], align='center'),
                dbc.Row([
                    dbc.Col(id='live-update-text-date', width=4),
                    dbc.Col(id='live-update-text-current', width=4),
                    dbc.Col(id='live-update-text-prediction', width=4),
                ], align='center'),
            ]), color='dark'
        )
    ]),
    dcc.Interval(
        id='interval-component-slow',
        interval=6*60*60*1000,  # in milliseconds
        n_intervals=0
    ),
    dcc.Interval(
        id='interval-component-fast',
        interval=30*60*1000,  # in milliseconds
        n_intervals=0
    ),
    dcc.Interval(
        id='interval-component-veryfast',
        interval=2*1000,  # in milliseconds
        n_intervals=0
    )
])

if __name__ == '__main__':
    app.run_server(debug=True)
