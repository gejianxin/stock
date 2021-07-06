import backtrader as bt
import backtrader.feeds as btfeeds
from datetime import datetime as dt


# docker run command
# docker run -it -e POSTGRES_PASSWORD=123456 -v /d/project/data:/var/lib/postgresql/data -p 5432:5432 --name db postgres:latest bash
# chown postgres:postgres /var/lib/postgresql/data
# initdb /var/lib/postgresql/data
# 后台启动pg server
# pg_ctl -D /var/lib/postgresql/data -l logfile start


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

def get_db_data(db, ticker):

