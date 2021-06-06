import backtrader as bt
import backtrader.feeds as btfeeds
from datetime import datetime as dt


def get_online_data(ticker, fromdate, todate):
    data = btfeeds.YahooFinanceData(dataname=ticker,
                                    fromdate=dt.strptime(fromdate, '%Y-%m-%d'),
                                    todate=dt.strptime(todate, '%Y-%m-%d'),
                                    timeframe=bt.TimeFrame.Days
                                    )
    return data


def get_csv_data(pathname, fromdate, todate):
    data = btfeeds.YahooFinanceCSVData(
        dataname=pathname,
        # Do not pass values before this date
        fromdate=dt.strptime(fromdate, '%Y-%m-%d'),
        # Do not pass values before this date
        todate=dt.strptime(todate, '%Y-%m-%d'),
        # Do not pass values after this date
        reverse=False)
    return data
