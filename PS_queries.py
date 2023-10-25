import psycopg2
import os
import pandas as pd
from dotenv import load_dotenv
load_dotenv()

def query_stock_data_by_date_range(CONNECTION, ticker, start_date, end_date):
    query = f"""WITH DailySummary AS (
        SELECT
            DATE_TRUNC('day', date) AS trading_date,
            TICKER,
            MIN(date) AS min_time,
            MAX(date) AS max_time,
            MAX(HIGH) AS High,
            MIN(LOW) AS Low
        FROM
            ts_stock -- Replace with the actual table name
        WHERE
            TICKER = '{ticker}' AND date BETWEEN '{start_date}' AND '{end_date}'
        GROUP BY
            DATE_TRUNC('day', date), TICKER
    )
    SELECT
        trading_date,
        TICKER,
        High,
        (SELECT OPEN FROM ts_stock WHERE TICKER = ds.TICKER AND date = ds.min_time) AS Open,
        (SELECT CLOSE FROM ts_stock WHERE TICKER = ds.TICKER AND date = ds.max_time) AS Close,
        Low
    FROM
        DailySummary ds
    ORDER BY
        trading_date;"""
    with psycopg2.connect(CONNECTION) as conn:
        cursor = conn.cursor()
        cursor.execute(query)
        cursor_v = cursor.fetchall()
        columns = ["Date", "Ticker", "High", "Open", "Close", "Low"]
        df = pd.DataFrame(cursor_v, columns=columns)
        df.set_index("Date", inplace=True)
    return df

def get_stock_symbols(CONNECTION):
    query = f"""SELECT DISTINCT TICKER FROM ts_stock;"""
    with psycopg2.connect(CONNECTION) as conn:
        cursor = conn.cursor()
        cursor.execute(query)
        cursor_v = cursor.fetchall()

    return [x[0] for x in cursor_v]
def query_stock_data_and_moving_average(CONNECTION, ticker, start_date, end_date):
    query = f"""WITH DailyClosing AS (
        SELECT
            DATE_TRUNC('day', date) AS trading_date,
            TICKER,
            MAX(date) AS max_time,
            MAX(CLOSE) AS Close
        FROM
            ts_stock -- Replace with the actual table name
        WHERE
            TICKER = '{ticker}' AND date BETWEEN '{start_date}' AND '{end_date}'
        GROUP BY
            DATE_TRUNC('day', date), TICKER
    ), MovingAverages AS (
        SELECT
            trading_date,
            TICKER,
            Close,
            AVG(Close) OVER (PARTITION BY TICKER ORDER BY trading_date ROWS BETWEEN 29 PRECEDING AND CURRENT ROW) AS "30_Day_MA",
            AVG(Close) OVER (PARTITION BY TICKER ORDER BY trading_date ROWS BETWEEN 89 PRECEDING AND CURRENT ROW) AS "90_Day_MA"
        FROM
            DailyClosing
    )
    SELECT
        trading_date,
        TICKER,
        Close,
        "30_Day_MA",
        "90_Day_MA"
    FROM
        MovingAverages
    ORDER BY
        trading_date;"""
    with psycopg2.connect(CONNECTION) as conn:
        cursor = conn.cursor()
        cursor.execute(query)
        cursor_v = cursor.fetchall()
        columns = ["Date", "Ticker","Close", "30_day_ma","90_day_ma"]
        df = pd.DataFrame(cursor_v, columns=columns)
        df.set_index("Date", inplace=True)
    return df

def query_top_gainers_losers(CONNECTION, start_date, end_date):
    query = f"""WITH GainLoss AS (
        SELECT
            first_open.TICKER,
            first_open.NAME,
            (last_close.CLOSE - first_open.OPEN) / first_open.OPEN AS percentage_change
        FROM
            (SELECT TICKER, NAME, OPEN
            FROM ts_stock
            WHERE DATE = (SELECT MIN(DATE) FROM ts_stock WHERE DATE_TRUNC('day', DATE) = '2021-01-05')) AS first_open
        JOIN
            (SELECT TICKER, CLOSE
            FROM ts_stock
            WHERE DATE = (SELECT MAX(DATE) FROM ts_stock WHERE DATE_TRUNC('day', DATE) = '2021-01-06')) AS last_close
        ON first_open.TICKER = last_close.TICKER
        ORDER BY percentage_change DESC
        LIMIT 3
    ), LossGain AS (
        SELECT
            first_open.TICKER,
            first_open.NAME,
            (last_close.CLOSE - first_open.OPEN) / first_open.OPEN AS percentage_change
        FROM
            (SELECT TICKER, NAME, OPEN
            FROM ts_stock
            WHERE DATE = (SELECT MIN(DATE) FROM ts_stock WHERE DATE_TRUNC('day', DATE) = '2021-01-05')) AS first_open
        JOIN
            (SELECT TICKER, CLOSE
            FROM ts_stock
            WHERE DATE = (SELECT MAX(DATE) FROM ts_stock WHERE DATE_TRUNC('day', DATE) = '2021-01-06')) AS last_close
        ON first_open.TICKER = last_close.TICKER
        ORDER BY percentage_change DESC
        LIMIT 3
    )
    SELECT * FROM GainLoss
    UNION ALL
    SELECT * FROM LossGain;"""
    with psycopg2.connect(CONNECTION) as conn:
        cursor = conn.cursor()
        cursor.execute(query)
        cursor_v = cursor.fetchall()
        columns = ["Ticker", "Percentage_Change"]
        df = pd.DataFrame(cursor_v, columns=columns)
    return df

# Example usage:
CONNECTION = os.getenv("CONNECTION")
start_date = "2023-01-04"  # Replace with the desired start date
end_date = "2023-01-11"  # Replace with the desired end date

#this is returning empty? need to check
#query_top_gainers_losers(CONNECTION, start_date, end_date)

ticker = "AAPL"  # Replace with the desired company's ticker symbol
start_date = "2021-01-04"  # Replace with the desired start date
end_date = "2021-01-06"  # Replace with the desired end date

if __name__ == "__main__":
    # query_stock_data_by_date_range(CONNECTION, ticker, start_date, end_date)
    # query_stock_data_and_moving_average(CONNECTION, ticker, start_date, end_date)
    # get_stock_symbols(CONNECTION)
    print(query_top_gainers_losers(CONNECTION, start_date, end_date))