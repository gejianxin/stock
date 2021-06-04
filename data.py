import backtrader.feeds as btfeeds
from datetime import datetime as dt


def get_data(pathname, startdate, enddate):
    # data = btfeeds.YahooFinanceData(dataname='600000.SS',
    #                                 fromdate=datetime.datetime(2018, 1, 1),
    #                                 todate=datetime.datetime(2021, 10, 10),
    #                                 timeframe=bt.TimeFrame.Days
    #                                 )
    data = btfeeds.YahooFinanceCSVData(
            dataname=pathname,
            # Do not pass values before this date
            fromdate=dt.strptime(startdate, '%Y-%m-%d'),
            # Do not pass values before this date
            todate=dt.strptime(startdate, '%Y-%m-%d'),
            # Do not pass values after this date
            reverse=False)
    return data
