import psycopg2

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
    conn.close()

# Example usage:
CONNECTION = "postgres://postgres:timescale@13.233.139.76:5432/tsdb"
ticker = "GOOGL"  # Replace with the desired company's ticker symbol
start_date = "2021-01-04"  # Replace with the desired start date
end_date = "2021-01-31"  # Replace with the desired end date

query_stock_data_by_date_range(CONNECTION, ticker, start_date, end_date)