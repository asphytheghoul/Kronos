# Kronos - A Stock Market Analysis Application with efficient queries

This repository contains the source code for a robust stock market analysis application designed to provide efficient data insights for financial analysis.

## Project Overview

The stock market analysis application is built to leverage TimeScaleDB, incorporating advanced features such as hypertables and time buckets to optimize data management and query performance for time series data. We also provide a comparison against vanilla PSQL.

## Dataset Details

### Description

The dataset includes historical hourly prices for over 7000 stocks traded on NASDAQ. The data spans the period from January 1, 2021, to December 30, 2021.

### Data Columns

- **ticker** (string): Symbol name.
- **name** (string): Security name.
- **date** (string): Trading date in the Eastern Time Zone.
- **open** (float): Opening price on the given day.
- **high** (float): Maximum price recorded on the given day.
- **low** (float): Minimum price recorded on the given day.
- **close** (float): Closing price on the given day.
- **adjusted close** (float): Closing price adjusted for dividends and splits.
- **volume** (int): Share volume traded on the given day.

## Usage

1. Clone the repository.
2. Install the requirements using requirements.txt or conda.yaml from 'environment' directory
3. Set up the TimeScaleDB database and configure the necessary environment.


## Running the app

Run the following commands and open the local host web address chosen by Dash.

```shell
python ./main.py
```

An example of the expected terminal messages are shown below:

```shell
Dash is running on http://127.0.0.1:8050/

 * Serving Flask app 'app' (lazy loading)
 * Environment: production
   WARNING: This is a development server. Do not use it in a production deployment.
   Use a production WSGI server instead.
 * Debug mode: on
```
