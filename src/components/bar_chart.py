import pandas as pd
import plotly.express as px
from dash import Dash, dcc, html, dash_table
from dash.dependencies import Input, Output
import plotly.graph_objects as go
from io import StringIO
from PS_queries import *
from datetime import datetime
from . import ids


##### SQL QUERIES #####
def render(app: Dash) -> html.Div:
    
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

    all_stock_symbols = get_stock_symbols(CONNECTION)
    stock_dropdown_data1 = dcc.Dropdown(
    id=ids.STOCK_DROPDOWN,
    options=[{"label": symbol, "value": symbol} for symbol in all_stock_symbols],
    value=all_stock_symbols[0],  # Set the default value to the first symbol
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
        candlestick_data = query_stock_data_by_date_range(CONNECTION, selected_stock, "2021-01-04", "2021-12-31")
        candlestick_fig = go.Figure(
            data=[
                go.Candlestick(
                    x=candlestick_data.index,
                    open=candlestick_data["Open"],
                    high=candlestick_data["High"],
                    low=candlestick_data["Low"],
                    close=candlestick_data["Close"],
                )
            ],
            layout=go.Layout(
                template="plotly_dark",
                font=dict(family="Arial", size=18, color="#7f7f7f"),
                # Set background color to white
            ),
        )
        alldays = set(
            candlestick_data.index[0] + pd.Timedelta(days=x)
            for x in range((candlestick_data.index[-1] - candlestick_data.index[0]).days)
        )
        missing = sorted(set(alldays) - set(candlestick_data.index))

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
            Input(ids.STOCK_DROPDOWN,"value")
        ],
    )
    def update_line_chart(selected_stock:str) -> go.Figure:
        fig = go.Figure()
        data_avg = query_stock_data_and_moving_average(CONNECTION, selected_stock, "2021-01-04", "2021-12-31")
        fig.add_trace(
            go.Scatter(
                x=data_avg.index,
                y=data_avg["Close"],
                mode="lines",
                name="Stock Price",
                # Thickness of the line (default = 2)
                line=dict(color="#f2f2f2", width=3),
            ),
        )
        fig.add_trace(
            go.Scatter(
                x=data_avg.index,
                y=data_avg["30_day_ma"],
                mode="lines",
                name="30-day MA",
                line=dict(color="#9467bd", dash="dot"),
            )
        )
        fig.add_trace(
            go.Scatter(
                x=data_avg.index,
                y=data_avg["90_day_ma"],
                mode="lines",
                name="90-day MA",
                line=dict(color="#1f77b4", dash="dot"),
            )
        )
        fig.update_layout(
            title=f"{selected_stock} Stock Price and Moving Averages",
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
