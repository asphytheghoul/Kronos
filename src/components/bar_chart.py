import pandas as pd
import plotly.express as px
from dash import Dash, dcc, html, dash_table
from dash.dependencies import Input, Output
import plotly.graph_objects as go
from datetime import datetime
from ..data.loader import DataSchema
from . import ids


def resample_to_daily(data):
    # Create a copy of the data to avoid modifying the original DataFrame
    data_copy = data.copy()
    
    # Convert 'date' column to datetime and set it as index for the copy
    data_copy['date'] = pd.to_datetime(data_copy['date'], utc=True)
    data_copy.set_index('date', inplace=True)
    
    # Resample the data to daily scale
    df_daily = data_copy.resample("D").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"}
    )
    print(df_daily)
    df_daily.dropna(inplace=True)
    return df_daily


def calculate_moving_averages(data):
    data = resample_to_daily(data)
    data.reset_index(inplace=True)
    data["date"] = pd.to_datetime(data["date"], utc=True)
    data["30_day_ma"] = data[DataSchema.CLOSE].rolling(window=30).mean()
    data["90_day_ma"] = data[DataSchema.CLOSE].rolling(window=90).mean()
    return data


def calculate_gain(data):
    data["gain"] = (
        (data[DataSchema.CLOSE] - data[DataSchema.OPEN]) / data[DataSchema.OPEN] * 100
    )
    return data


def calculate_loss(data):
    data["loss"] = (
        (data[DataSchema.OPEN] - data[DataSchema.CLOSE]) / data[DataSchema.OPEN] * 100
    )
    return data


def calculate_hourly_moving_averages(data):
    data["30_hourly_ma"] = data.groupby(pd.Grouper(key=DataSchema.DATE, freq="H"))[
        DataSchema.CLOSE
    ].transform(lambda x: x.rolling(window=30, min_periods=1).mean())
    data["90_hourly_ma"] = data.groupby(pd.Grouper(key=DataSchema.DATE, freq="H"))[
        DataSchema.CLOSE
    ].transform(lambda x: x.rolling(window=90, min_periods=1).mean())
    return data


def calculate_weekly_moving_averages(data):
    data = resample_to_daily(data)
    data.reset_index(inplace=True)
    data["date"] = pd.to_datetime(data["date"], utc=True)
    data["30_weekly_ma"] = data.groupby(pd.Grouper(key=DataSchema.DATE, freq="W"))[
        DataSchema.CLOSE
    ].transform(lambda x: x.rolling(window=30, min_periods=1).mean())
    data["90_weekly_ma"] = data.groupby(pd.Grouper(key=DataSchema.DATE, freq="W"))[
        DataSchema.CLOSE
    ].transform(lambda x: x.rolling(window=90, min_periods=1).mean())
    return data


def render(app: Dash, data: list[pd.DataFrame]) -> html.Div:
    data,data2 = data
    data[DataSchema.DATE] = pd.to_datetime(data[DataSchema.DATE], utc=True)
    data2[DataSchema.DATE] = pd.to_datetime(data2[DataSchema.DATE], utc=True)
    data_avg = calculate_moving_averages(data.copy())
    min_date = min(
        int(pd.Timestamp(data[DataSchema.DATE].min()).timestamp() / 86400),
        int(pd.Timestamp(data2[DataSchema.DATE].min()).timestamp() / 86400)
    )       
    max_date = max(
        int(pd.Timestamp(data[DataSchema.DATE].max()).timestamp() / 86400),
        int(pd.Timestamp(data2[DataSchema.DATE].max()).timestamp() / 86400)
    )       
    stock_symbols_data1 = data[DataSchema.TICKER].unique()
    stock_symbols_data2 = data2[DataSchema.TICKER].unique()
    all_stock_symbols = list(set(stock_symbols_data1) | set(stock_symbols_data2))

    # choose_date_dropdown = dcc.Dropdown(
    #     id=ids.CHOOSE_DATE_DROPDOWN,
    #     options=[
    #         {
    #             "label": pd.Timestamp(86400 * date, unit="s").strftime("%Y-%m-%d"),
    #             "value": date,
    #         }
    #         for date in range(min_date, max_date + 1)
    #     ],
    #     value=min_date,
    #     clearable=False,
    #     style={"width": "150px"},
    # )

    stock_dropdown_data1 = dcc.Dropdown(
        id=ids.STOCK_DROPDOWN,
        options=[{"label": symbol, "value": symbol} for symbol in all_stock_symbols],
        value=all_stock_symbols[0],  # Set the default value to the first symbol
        clearable=False,
        style={"width": "150px"},
    )

    # summary_table = dash_table.DataTable(
    #     id=ids.SUMMARY_TABLE,
    #     columns=[
    #         {"name": "Ticker Name", "id": DataSchema.TICKER},
    #         {"name": "Last Price", "id": DataSchema.CLOSE},
    #         {"name": "Previous Day Peak", "id": "previous_day_peak"},
    #         {"name": "Price Change", "id": "price_change"},
    #         {"name": "% Change", "id": "percent_change"},
    #         {"name": "Max Price Till Date", "id": "max_price_till_date"},
    #         {"name": "Lowest Price Till Date", "id": "lowest_price_till_date"},
    #     ],
    #     style_table={"height": "400px", "overflowY": "auto"},
    # )
    
    # @app.callback(
    #     Output(ids.SUMMARY_TABLE, "data"),
    #     [
    #         Input(ids.CHOOSE_DATE_DROPDOWN, "value"),
    #     ],
    # )
    # def update_summary_table(chosen_date: int):
    #     chosen_date_timestamp = pd.Timestamp(chosen_date*86400 ,unit="s").strftime("%Y-%m-%d")

    #     # Apply the chosen date to both data and data2 DataFrames
    #     data["date"] = chosen_date_timestamp
    #     data2["date"] = chosen_date_timestamp

    #     data1_filtered = data[data[DataSchema.DATE] == chosen_date_timestamp]
    #     data2_filtered = data2[data2[DataSchema.DATE] == chosen_date_timestamp]
        
    #     filtered_data = pd.concat([data1_filtered, data2_filtered])
    #     # print("filtered_data",filtered_data,sep="/n")
    #     summary_data_list = []

    #     for symbol in all_stock_symbols:
    #         selected_stock_data = filtered_data[filtered_data[DataSchema.TICKER] == symbol]

    #         if not selected_stock_data.empty:
    #             latest_data = selected_stock_data.tail(1)
    #             previous_day_data = filtered_data[filtered_data[DataSchema.TICKER] == symbol].shift(1).tail(1)
    #             previous_day_peak = previous_day_data[DataSchema.CLOSE].values[0]
    #             last_price = latest_data[DataSchema.CLOSE].values[0]
    #             price_change = last_price - previous_day_peak
    #             percent_change = (price_change / previous_day_peak) * 100
    #             max_price_till_date = filtered_data[filtered_data[DataSchema.TICKER] == symbol][DataSchema.HIGH].max()
    #             lowest_price_till_date = filtered_data[filtered_data[DataSchema.TICKER] == symbol][DataSchema.LOW].min()

    #             summary_data_list.append(
    #                 {
    #                     DataSchema.TICKER: symbol,
    #                     DataSchema.CLOSE: last_price,
    #                     "previous_day_peak": previous_day_peak,
    #                     "price_change": price_change,
    #                     "percent_change": percent_change,
    #                     "max_price_till_date": max_price_till_date,
    #                     "lowest_price_till_date": lowest_price_till_date,
    #                 }
    #             )

    #     return summary_data_list

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

    line_chart_div = dcc.Graph(
        id=ids.LINE_CHART, style={"height": "40%", "margin": "auto"}
    )
    
    candlestick_graph = dcc.Graph(
        id=ids.CANDLESTICK_CHART, style={"height": "40%", "margin": "auto"}
    )
    @app.callback(
        Output(ids.CANDLESTICK_CHART, "figure"),
        [
            Input(ids.STOCK_DROPDOWN, "value"),
        ],
    )
    def update_candlestick_chart(selected_stock:str) -> go.Figure:
        if selected_stock in stock_symbols_data1:
            filter = data.query(f"{DataSchema.TICKER} == @selected_stock")
        elif selected_stock in stock_symbols_data2:
            filter = data2.query(f"{DataSchema.TICKER} == @selected_stock")
        
        df_daily = resample_to_daily(filter.copy())
        candlestick_fig = go.Figure(
            data=[
                go.Candlestick(
                    x=df_daily.index,
                    open=df_daily["open"],
                    high=df_daily["high"],
                    low=df_daily["low"],
                    close=df_daily["close"],
                )
            ],
            layout=go.Layout(
                template="plotly_dark",
                font=dict(family="Arial", size=18, color="#7f7f7f"),
                # Set background color to white
            ),
        )
        alldays = set(
            df_daily.index[0] + pd.Timedelta(days=x)
            for x in range((df_daily.index[-1] - df_daily.index[0]).days)
        )
        missing = sorted(set(alldays) - set(df_daily.index))

        candlestick_fig.update_xaxes(
            rangebreaks=[dict(values=missing)],
        )

        candlestick_fig.update_layout(
            title=f"{selected_stock} Stock candlestick chart",
            xaxis_showgrid=False,
            yaxis_showgrid=False,
        )

        return candlestick_fig

    @app.callback(
        Output(ids.LINE_CHART, "figure"),
        [
            Input(ids.CHOOSE_OPTION_DROPDOWN, "value"),
            Input(ids.STOCK_DROPDOWN,"value")
        ],
    )
    def update_line_chart(interval: str,selected_stock:str) -> go.Figure:
        if selected_stock in stock_symbols_data1:
            selected_data = data
        elif selected_stock in stock_symbols_data2:
            selected_data = data2
        fig = go.Figure()
        nonlocal data_avg
        interval = "Daily"
        if interval == "Hourly":
            data_avg = calculate_hourly_moving_averages(selected_data.copy())
            ma_30_col = "30_hourly_ma"
            ma_90_col = "90_hourly_ma"
        elif interval == "Daily":
            ma_30_col = "30_day_ma"
            ma_90_col = "90_day_ma"
        elif interval == "Weekly":
            data_avg = calculate_weekly_moving_averages(selected_data.copy())
            ma_30_col = "30_weekly_ma"
            ma_90_col = "90_weekly_ma"

        fig.add_trace(
            go.Scatter(
                x=data_avg[DataSchema.DATE],
                y=data_avg[DataSchema.CLOSE],
                mode="lines",
                name="Stock Price",
                # Thickness of the line (default = 2)
                line=dict(color="#f2f2f2", width=3),
            ),
        )
        fig.add_trace(
            go.Scatter(
                x=data_avg[DataSchema.DATE],
                y=data_avg[ma_30_col],
                mode="lines",
                name="30-day MA",
                line=dict(color="#9467bd", dash="dot"),
            )
        )
        fig.add_trace(
            go.Scatter(
                x=data_avg[DataSchema.DATE],
                y=data_avg[ma_90_col],
                mode="lines",
                name="90-day MA",
                line=dict(color="#1f77b4", dash="dot"),
            )
        )
        fig.update_layout(
            title=f"{selected_stock} Stock Price and Moving Averages ({interval} interval)",
            xaxis_title="Date",
            yaxis_title="Price",
            legend=dict(x=0, y=1),
            template="plotly_dark",
            font=dict(family="Arial", size=18, color="#7f7f7f"),
            xaxis_showgrid=False,
            yaxis_showgrid=False,
        )

        return fig
    
    # top_gainers_bar_chart = dcc.Graph(
    #     id=ids.TOP_GAINERS_BAR_CHART, style={"height": "40%", "margin": "auto"}
    # )

    # @app.callback(
    # Output(ids.TOP_GAINERS_BAR_CHART, "figure"),
    # [
    #     Input(ids.START_RANGE_DROPDOWN, "value"),
    #     Input(ids.END_RANGE_DROPDOWN, "value"),
    #     Input(ids.STOCK_DROPDOWN, "value"),
    # ],
    # )
    # def update_top_gainers_bar_chart(start_date: int, end_date: int, selected_stock: str) -> go.Figure:
    #     if selected_stock in stock_symbols_data1:
    #         filtered_data = data.query(
    #             f"@start_date <= date <= @end_date and {DataSchema.TICKER} == @selected_stock"
    #         )
    #     elif selected_stock in stock_symbols_data2:
    #         filtered_data = data2.query(
    #             f"@start_date <= date <= @end_date and {DataSchema.TICKER} == @selected_stock"
    #         )

    #     filtered_data = calculate_gain(filtered_data)

    #     top_gainers = filtered_data.sort_values(by="gain", ascending=False).head(3)
    #     fig = px.bar(
    #         top_gainers,
    #         x="gain",
    #         y="date_only",
    #         orientation="h",
    #         labels={DataSchema.DATE: "Date"},
    #         title=f"Top 3 Gainers - {selected_stock}",
    #     )

    #     return fig

    # top_losers_bar_chart = dcc.Graph(
    #     id=ids.TOP_LOSERS_BAR_CHART, style={"height": "40%", "margin": "auto"}
    # )
    # @app.callback(
    #     Output(ids.TOP_LOSERS_BAR_CHART, "figure"),
    #     [
    #         Input(ids.START_RANGE_DROPDOWN, "value"),
    #         Input(ids.END_RANGE_DROPDOWN, "value"),
    #         Input(ids.STOCK_DROPDOWN, "value"),
    #     ],
    # )
    # def update_top_losers_bar_chart(start_date: int, end_date: int, selected_stock: str) -> go.Figure:
    #     if selected_stock in stock_symbols_data1:
    #         filtered_data = data.query(
    #             f"@start_date <= date <= @end_date and {DataSchema.TICKER} == @selected_stock"
    #         )
    #     elif selected_stock in stock_symbols_data2:
    #         filtered_data = data2.query(
    #             f"@start_date <= date <= @end_date and {DataSchema.TICKER} == @selected_stock"
    #         )

    #     filtered_data = calculate_loss(filtered_data)

    #     top_losers = filtered_data.sort_values(by="loss", ascending=False).head(3)
    #     fig = px.bar(
    #         top_losers,
    #         x="loss",
    #         y="date_only",
    #         orientation="h",
    #         labels={DataSchema.DATE: "Date"},
    #         title=f"Top 3 Losers - {selected_stock}",
    #     )

    #     return fig
    
    return html.Div(
        [
            # Dropdowns, charts, and other components (right side)
            html.Div(
                [
                    html.H4("Choose the Stock: "),
                    stock_dropdown_data1,
                    candlestick_graph,
                    choose_option_dropdown,
                    line_chart_div,
                    # top_gainers_bar_chart,
                    # top_losers_bar_chart,
                ],
                style={"width": "50%", "display": "inline-block", "float": "right"},
            ),
            # Summary statistics table (left side)
            # html.Div(
            #     [
            #         html.H2("Summary Statistics"),
            #         html.H4("Choose the Date: "),
            #         choose_date_dropdown,
            #         summary_table,
            #     ],
            #     style={"width": "50%", "display": "inline-block"},
            # ),
        ]
    )
