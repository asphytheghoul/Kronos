import pandas as pd


class DataSchema:
    TICKER = "ticker"
    NAME = "name"
    OPEN = "open"
    HIGH = "high"
    LOW = "low"
    CLOSE = "close"
    ADJUSTED_CLOSE = "adjusted close"
    VOLUME = "volume"
    DATE = "date"
    DAY = "day"
    MONTH = "month"
    TIME = "time"
    DATE_ONLY = "date_only"


def load_data(
    path: str,
) -> (
    pd.DataFrame
):  # modify this as required later to query db instead of reading from csv
    data = pd.read_csv(
        path,
        dtype={
            DataSchema.TICKER: str,
            DataSchema.NAME: str,
            DataSchema.OPEN: float,
            DataSchema.HIGH: float,
            DataSchema.LOW: float,
            DataSchema.CLOSE: float,
            DataSchema.ADJUSTED_CLOSE: float,
            DataSchema.VOLUME: int,
            DataSchema.DATE_ONLY: str,
        },
    )

    # Extract day, month, and time from the "date" column
    data[DataSchema.TIME] = data[DataSchema.DATE].str.split(" ").str[1].astype(str)
    data[DataSchema.DATE_ONLY] = data[DataSchema.DATE].str.split(" ").str[0]
    data[DataSchema.DAY] = data[DataSchema.DATE_ONLY].str.split("-").str[2].astype(str)
    data[DataSchema.MONTH] = (
        data[DataSchema.DATE_ONLY].str.split("-").str[1].astype(str)
    )

    return data
