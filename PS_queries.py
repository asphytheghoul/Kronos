import psycopg2
import os

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
        for row in cursor.fetchall():
            print(row)

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
        for row in cursor.fetchall():
            print(row)

def query_top_gainers_losers(CONNECTION, start_date, end_date):
    query = f"""WITH GainLoss AS (
        SELECT
            first_open.TICKER,
            first_open.NAME,
            (last_close.CLOSE - first_open.OPEN) / first_open.OPEN AS percentage_change
        FROM
            (SELECT TICKER, NAME, OPEN
            FROM ts_stock
            WHERE DATE = '{start_date}') AS first_open
        JOIN
            (SELECT TICKER, CLOSE
            FROM ts_stock
            WHERE DATE = '{end_date}') AS last_close
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
            WHERE DATE = '{start_date}') AS first_open
        JOIN
            (SELECT TICKER, CLOSE
            FROM ts_stock
            WHERE DATE = '{end_date}') AS last_close
        ON first_open.TICKER = last_close.TICKER
        ORDER BY percentage_change
        LIMIT 3
    )
    SELECT * FROM GainLoss
    UNION ALL
    SELECT * FROM LossGain;"""
    with psycopg2.connect(CONNECTION) as conn:
        cursor = conn.cursor()
        cursor.execute(query)
        for row in cursor.fetchall():
            print(row)

# Example usage:
CONNECTION = os.getenv("CONNECTION")
start_date = "2023-01-04"  # Replace with the desired start date
end_date = "2023-01-11"  # Replace with the desired end date

#this is returning empty? need to check
#query_top_gainers_losers(CONNECTION, start_date, end_date)

ticker = "AAPL"  # Replace with the desired company's ticker symbol
start_date = "2021-01-04"  # Replace with the desired start date
end_date = "2021-05-31"  # Replace with the desired end date

query_stock_data_by_date_range(CONNECTION, ticker, start_date, end_date)
query_stock_data_and_moving_average(CONNECTION, ticker, start_date, end_date)
