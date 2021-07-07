import backtrader as bt
import backtrader.feeds as btfeeds
from datetime import datetime as dt, timedelta
from datetime import date
import psycopg2
from psycopg2 import Error
import tushare as ts
from ..config.essential import TOKEN, YEARS


# docker run command
# docker run -it -e POSTGRES_PASSWORD=123456 -v /d/project/data:/var/lib/postgresql/data -p 5432:5432 --name db postgres:latest bash
# chown postgres:postgres /var/lib/postgresql/data
# initdb /var/lib/postgresql/data
# 后台启动pg server
# pg_ctl -D /var/lib/postgresql/data -l logfile start

# Get all tickers
def get_all_tickers(token=TOKEN):
    pro = ts.pro_api(token)
    data = pro.query('stock_basic', exchange='', list_status='L', fields='ts_code, symbol, name, area, industry, list_date')
    return data


def get_online_data(ticker, fromdate, todate):
    data = btfeeds.YahooFinanceData(dataname=ticker,
                                    fromdate=dt.strptime(fromdate, '%Y-%m-%d'),
                                    todate=dt.strptime(todate, '%Y-%m-%d'),
                                    timeframe=bt.TimeFrame.Days
                                    )
    return data


# default update recent 10 years data
def update_all_data(ticker, year=YEARS):
    # TODO: check database firstday lastday
    # Beaware firstday and lastday datatype, if not is date, you need to covert it to date object
    todate = dt.now().date()
    fromdate = todate - timedelta(days=365.25*year)
    # check if firstday was before fromdate
    delta = fromdate - firstday
    if delta < 0:  # fromdate < firstday, the database need to fullfil data before firstdate
        data = get_online_data(ticker, fromdate, todate=firstdate-timedelta(days=1))
        # TODO: insert data into db
    delta = todate - lastday
    if delta > 0:  # todate > lastday, the database need to fullfil data after lastday
        data = get_online_data(ticker, fromdate=lastday+timedelta(days=1), todate=todate)
        # TODO: insert data into db


def update_data(ticker, fromdate, todate):
    # TODO: check database firstday lastday
    # Beaware firstday and lastday datatype, if not is date, you need to covert it to date object
    fromdate = dt.strptime(fromdate, '%Y-%m-%d')
    todate = dt.strptime(todate, '%Y-%m-%d')
    # check if firstday was before fromdate
    delta = fromdate.date() - firstday
    if delta < 0:  # fromdate < firstday, the database need to fullfil data before firstdate
        data = get_online_data(ticker, fromdate, todate=firstdate-timedelta(days=1))
        # TODO: insert data into db
    delta = todate.date() - lastday
    if delta > 0:  # todate > lastday, the database need to fullfil data after lastday
        data = get_online_data(ticker, fromdate=lastday+timedelta(days=1), todate=todate)
        # TODO: insert data into db


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
    try:
        # Connect to an existing database
        connection = psycopg2.connect(user=db.username,
                                      # password="123456",
                                      host=db.host,
                                      port=db.port,
                                      database=db.database)

        # Create a cursor to perform database operations
        cursor = connection.cursor()
        # Print PostgreSQL details
        # print("PostgreSQL server information")
        # print(connection.get_dsn_parameters(), "\n")
        # Executing a SQL query
        # cursor.execute("SELECT version();")
        # Fetch result
        # record = cursor.fetchone()
        # print("You are connected to - ", record, "\n")

    except (Exception, Error) as error:
        print("Error while connecting to PostgreSQL", error)
    finally:
        if (connection):
            cursor.close()
            connection.close()
            print("PostgreSQL connection is closed")
