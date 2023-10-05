import pandas as pd
import plotly.express as px
from dash import Dash, dcc, html
from dash.dependencies import Input, Output
import plotly.graph_objects as go

from ..data.loader import DataSchema
from . import ids

def calculate_moving_averages(data):
    data['30_day_ma'] = data[DataSchema.CLOSE].rolling(window=30).mean()
    data['90_day_ma'] = data[DataSchema.CLOSE].rolling(window=90).mean()
    return data

def calculate_hourly_moving_averages(data):
    data['30_hourly_ma'] = data.groupby(pd.Grouper(key=DataSchema.DATE, freq='H'))[DataSchema.CLOSE].transform(
        lambda x: x.rolling(window=30, min_periods=1).mean()
    )
    data['90_hourly_ma'] = data.groupby(pd.Grouper(key=DataSchema.DATE, freq='H'))[DataSchema.CLOSE].transform(
        lambda x: x.rolling(window=90, min_periods=1).mean()
    )
    return data

def calculate_weekly_moving_averages(data):
    data.set_index(DataSchema.DATE,inplace=True)
    data['30_weekly_ma'] = data[DataSchema.CLOSE].rolling(window=30).mean()
    
    data['90_weekly_ma'] = data[DataSchema.CLOSE].rolling(window=90).mean()
    data.reset_index(inplace=True)
    return data

def render(app: Dash, data: pd.DataFrame) -> html.Div:
    data_avg = calculate_moving_averages(data.copy())
    min_date = int(pd.Timestamp(data[DataSchema.DATE].min()).timestamp() / 86400)
    max_date = int(pd.Timestamp(data[DataSchema.DATE].max()).timestamp() / 86400)
    start_range_dropdown = dcc.Dropdown(
        id=ids.START_RANGE_DROPDOWN,
        options=[
            {"label": pd.Timestamp(86400 * date, unit="s").strftime("%Y-%m-%d"), "value": date}
            for date in range(min_date, max_date + 1)
        ],
        value=min_date,
        clearable=False,
        style={"width": "150px"},
    )
    choose_date_dropdown = dcc.Dropdown(
        id=ids.CHOOSE_DATE_DROPDOWN,
        options=[
            {"label": pd.Timestamp(86400 * date, unit="s").strftime("%Y-%m-%d"), "value": date}
            for date in range(min_date, max_date + 1)
        ],
        value = "2021-01-4",
        clearable=False,
        style={"width": "150px"},
    )

    end_range_dropdown = dcc.Dropdown(
        id=ids.END_RANGE_DROPDOWN,
        options=[
            {"label": pd.Timestamp(86400 * date, unit="s").strftime("%Y-%m-%d"), "value": date}
            for date in range(min_date, max_date + 1)
        ],
        value=max_date,
        clearable=False,
        style={"width": "150px"},
    )    
    range_dropdowns_div = html.Div(
    children=[
        html.Div([
            html.H4("Start Date"),
            start_range_dropdown,
        ], style={"margin-right": "10px"}),
        html.Div([
            html.H4("End Date"),
            end_range_dropdown,
        ], style={"margin-left": "10px"}),
    ],
    style={"display": "flex", "justify-content": "center", "margin-bottom": "10px"},
    )

    choose_option_dropdown = dcc.Dropdown(
        id=ids.CHOOSE_OPTION_DROPDOWN,
        options=[
            {"label": "Hourly", "value": "Hourly"},
            {"label": "Weekly", "value": "Weekly"},
            {"label": "Daily", "value": "Daily"},
        ],
        value="Daily",
        clearable=False,
        style={"width": "150px"},
    )

    # slider = dcc.Slider(
    #     id=ids.SLIDER,
    #     min=min_date,
    #     max=max_date,
    #     step=1,
    #     value=min_date,
    #     marks={
    #         min_date: pd.Timestamp(86400 * min_date, unit="s").strftime("%Y-%m-%d"),
    #         max_date: pd.Timestamp(86400 * max_date, unit="s").strftime("%Y-%m-%d")
    #     }
    # )

    @app.callback(
        Output(ids.BAR_CHART, "children"),
        [
            # Input(ids.MONTH_DROPDOWN, "value"),
            # Input(ids.DAY_DROPDOWN, "value"),
            # Input(ids.TIME_DROPDOWN, "value"),
            Input(ids.CHOOSE_DATE_DROPDOWN,"value"),
        ],
    )
    def update_bar_chart(
        date_value: int
    ) -> html.Div:
        date = pd.Timestamp(date_value * 86400, unit="s").strftime("%Y-%m-%d")
        print(date)
        filtered_data = data.query(
            "date == @date"
        )

        if filtered_data.shape[0] == 0:
            return html.Div("No data selected.", id=ids.BAR_CHART)

        def create_pivot_table() -> pd.DataFrame:
            pt = filtered_data.pivot_table(
                values=DataSchema.CLOSE,
                index=[DataSchema.TIME],
                aggfunc="mean",
                fill_value=0,
                dropna=False,
            )
            return pt.reset_index()

        fig = px.bar(
            create_pivot_table(),
            x=DataSchema.TIME,
            y=DataSchema.CLOSE,
            color=DataSchema.TIME,
        )
       
        return html.Div([
            html.Div([
            html.H4("View Trade Data For Date"),
            choose_date_dropdown,
        ], style={"margin-right": "10px"}),
            dcc.Graph(figure=fig),
        ],id=ids.BAR_CHART)
    candlestick_fig = go.Figure(data=[go.Candlestick(x=data[DataSchema.DATE],
                open=data[DataSchema.OPEN],
                high=data[DataSchema.HIGH],
                low=data[DataSchema.LOW],
                close=data[DataSchema.CLOSE])])

    candlestick_fig.update_layout(title='Apple stock candlestick chart')
    candlestick_graph = dcc.Graph(figure=candlestick_fig, style={'width': '50%', 'height': '40%', 'margin': 'auto'})
    bar_chart_div = html.Div(id=ids.BAR_CHART, style={'width': '50%', 'height': '40%', 'margin': 'auto'})

    graph_div = html.Div(
        children=[candlestick_graph, bar_chart_div],
        style={'display': 'flex', 'flex-wrap': 'wrap', 'justify-content': 'space-between'}
    )

    @app.callback(
        Output("graph", "figure"),
        [
            Input(ids.START_RANGE_DROPDOWN, "value"),
            Input(ids.END_RANGE_DROPDOWN, "value"),
        ],
    )
    def update_candlestick_chart(start_date: int, end_date: int) -> go.Figure:
        filtered_data = data.query(
            "@start_date <= date <= @end_date"
        )

        fig = go.Figure(
            data=[
                go.Candlestick(
                    x=filtered_data[DataSchema.DATE],
                    open=filtered_data[DataSchema.OPEN],
                    high=filtered_data[DataSchema.HIGH],
                    low=filtered_data[DataSchema.LOW],
                    close=filtered_data[DataSchema.CLOSE],
                )
            ]
        )

        fig.update_layout(title="Apple stock candlestick chart")

        return fig

    #### INSERT HERE ####
    line_chart_div = dcc.Graph(id=ids.LINE_CHART)
    @app.callback(
        Output(ids.LINE_CHART, "figure"),
        [
            Input(ids.CHOOSE_OPTION_DROPDOWN, "value"),
        ],
    )
    def update_line_chart(interval: str) -> go.Figure:
        fig = go.Figure()
        nonlocal data_avg
        if interval == "Hourly":
            data_avg = calculate_hourly_moving_averages(data_avg.copy())
            ma_30_col = '30_hourly_ma'
            ma_90_col = '90_hourly_ma'
        elif interval == "Daily":
            ma_30_col = '30_day_ma'
            ma_90_col = '90_day_ma'
        elif interval == "Weekly":
            data_avg = calculate_weekly_moving_averages(data_avg.copy())
            ma_30_col = '30_weekly_ma'
            ma_90_col = '90_weekly_ma'
        
        fig.add_trace(go.Scatter(x=data_avg[DataSchema.DATE], y=data_avg[DataSchema.CLOSE], mode='lines', name='Stock Price'))
        
        # Add the 30-day moving average line in red
        fig.add_trace(go.Scatter(x=data_avg[DataSchema.DATE], y=data_avg[ma_30_col], mode='lines', name='30-day MA', line=dict(color='red')))
        
        # Add the 90-day moving average line in blue
        fig.add_trace(go.Scatter(x=data_avg[DataSchema.DATE], y=data_avg[ma_90_col], mode='lines', name='90-day MA', line=dict(color='blue')))
        
        fig.update_layout(title=f'Stock Price and Moving Averages ({interval} interval)',
                          xaxis_title='Date', yaxis_title='Price',
                          legend=dict(x=0, y=1))

        return fig

    return html.Div([
        range_dropdowns_div,
        graph_div,
        html.Div([
            html.H4("Choose the type of View: "),
            choose_option_dropdown,
        ],style={"margin-left": "10px"}),
        line_chart_div
        # line_chart_div
    ])