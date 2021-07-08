from datetime import datetime as dt, timedelta
from datetime import date
import backtrader as bt
import backtrader.feeds as btfeeds
import psycopg2
from psycopg2 import Error, sql
import tushare as ts
from ..config.essential import DB, TOKEN, YEARS


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
    if isinstance(fromdate, date):
        try:
            fromdate=dt.strptime(fromdate, '%Y-%m-%d')
        except ValueError as error:
            template = "An exception of type {0} occurred. Arguments:\n{1!r}"
            message = template.format(type(error).__name__, error.args)
            print (message)
    if isinstance(todate, date):
        try:
            todate=dt.strptime(todate, '%Y-%m-%d')
        except ValueError as error:
            template = "An exception of type {0} occurred. Arguments:\n{1!r}"
            message = template.format(type(error).__name__, error.args)
            print (message)

    data = btfeeds.YahooFinanceData(dataname=ticker, fromdate=fromdate, todate=todate, timeframe=bt.TimeFrame.Days)
    return data


def update_ticker_data(ticker, fromdate, todate=dt.now().date(), db=DB):
    if isinstance(fromdate, date):
        try:
            fromdate=dt.strptime(fromdate, '%Y-%m-%d')
        except ValueError as error:
            template = "An exception of type {0} occurred. Arguments:\n{1!r}"
            message = template.format(type(error).__name__, error.args)
            print (message)

    records = get_ticker_data(ticker=ticker, fromdate=fromdate, todate=todate, db=db)
    firstdate = dt.strptime(records['date', 0], '%Y-%m-%d')
    lastdate = dt.strptime(records['date', -1], '%Y-%m-%d')
    delta = (fromdate - firstdate).days
    if delta < 0:  # fromdate < firstday, the database need to fullfil data before firstdate
        data = get_online_data(ticker=ticker, fromdate=fromdate, todate=firstdate-timedelta(days=1))
        insert_ticker_data(ticker=ticker, data=data, db=db)  # insert data into db
    delta = (todate - lastdate).days
    if delta > 0:  # todate > lastday, the database need to fullfil data after lastday
        data = get_online_data(ticker, fromdate=lastdate+timedelta(days=1), todate=todate)
        insert_ticker_data(ticker=ticker, data=data, db=db)  # insert data into db


# default update recent 10 years data
def update_ticker_nyears_data(ticker, years=YEARS, db=DB):
    # Check database firstday lastday
    todate = dt.now().date()
    fromdate = todate - timedelta(days=365.25*years)
    records = get_ticker_data(ticker=ticker, fromdate=fromdate, todate=todate, db=db)
    firstdate = dt.strptime(records['date', 0], '%Y-%m-%d')
    lastdate = dt.strptime(records['date', -1], '%Y-%m-%d')
    # check if firstday was before fromdate
    delta = (fromdate - firstdate).days
    if delta < 0:  # fromdate < firstday, the database need to fullfil data before firstdate
        data = get_online_data(ticker=ticker, fromdate=fromdate, todate=firstdate-timedelta(days=1))
        insert_ticker_data(ticker=ticker, data=data, db=db)  # insert data into db
    delta = (todate - lastdate).days
    if delta > 0:  # todate > lastday, the database need to fullfil data after lastday
        data = get_online_data(ticker, fromdate=lastdate+timedelta(days=1), todate=todate)
        insert_ticker_data(ticker=ticker, data=data, db=db)  # insert data into db


def update_all_data(fromdate, todate=dt.now().date(), years=YEARS, db=DB):
    if isinstance(fromdate, date):
        try:
            fromdate=dt.strptime(fromdate, '%Y-%m-%d')
        except ValueError as error:
            template = "An exception of type {0} occurred. Arguments:\n{1!r}"
            message = template.format(type(error).__name__, error.args)
            print (message)

    tickers = get_all_tickers(token=TOKEN)
    for ticker in tickers['ts_code']:
        records = get_ticker_data(ticker=ticker, fromdate=fromdate, todate=todate, db=db)
        firstdate = dt.strptime(records['date', 0], '%Y-%m-%d')
        lastdate = dt.strptime(records['date', -1], '%Y-%m-%d')
        # check if firstday was before fromdate
        delta = (fromdate - firstdate).days
        if delta < 0:  # fromdate < firstday, the database need to fullfil data before firstdate
            data = get_online_data(ticker=ticker, fromdate=fromdate, todate=firstdate-timedelta(days=1))
            insert_ticker_data(ticker=ticker, data=data, db=db)  # insert data into db
        delta = (todate - lastdate).days
        if delta > 0:  # todate > lastday, the database need to fullfil data after lastday
            data = get_online_data(ticker, fromdate=lastdate+timedelta(days=1), todate=todate)
            insert_ticker_data(ticker=ticker, data=data, db=db)  # insert data into db


def get_csv_data(pathname, fromdate, todate):
    if isinstance(fromdate, date):
        try:
            fromdate=dt.strptime(fromdate, '%Y-%m-%d')
        except ValueError as error:
            template = "An exception of type {0} occurred. Arguments:\n{1!r}"
            message = template.format(type(error).__name__, error.args)
            print (message)
    if isinstance(todate, date):
        try:
            todate=dt.strptime(todate, '%Y-%m-%d')
        except ValueError as error:
            template = "An exception of type {0} occurred. Arguments:\n{1!r}"
            message = template.format(type(error).__name__, error.args)
            print (message)
    data = btfeeds.YahooFinanceCSVData(
        dataname=pathname,
        # Do not pass values before this date
        fromdate=fromdate,
        # Do not pass values before this date
        todate=todate,
        # Do not pass values after this date
        reverse=False)
    return data


def get_ticker_data(ticker, fromdate, todate=dt.now().date(), db=DB):
    if isinstance(fromdate, date):
        try:
            fromdate=dt.strptime(fromdate, '%Y-%m-%d')
        except ValueError as error:
            template = "An exception of type {0} occurred. Arguments:\n{1!r}"
            message = template.format(type(error).__name__, error.args)
            print (message)

    try:
        # Connect to an existing database
        connection = psycopg2.connect(user=db.username,
                                      password=db.password,
                                      host=db.host,
                                      port=db.port,
                                      database=db.database)

        # Create a cursor to perform database operations
        cursor = connection.cursor()
        query = sql.SQL('SELECT * FROM {table} WHERE DATE BETWEEN {fromdate} TO {todate} ASC').format(table=sql.Identifier(ticker), fromdate=sql.Identifier(fromdate), todate=sql.Identifier(todate))
        cursor.execute(query)
        records = cursor.fetchall()
        return records

    except (Exception, Error) as error:
        print("Error while connecting to PostgreSQL", error)
    finally:
        cursor.close()
        connection.close()
        print("PostgreSQL connection is closed")


def insert_ticker_data(ticker, data, db=DB):
    try:
        # Connect to an existing database
        connection = psycopg2.connect(user=db.username,
                                      password=db.password,
                                      host=db.host,
                                      port=db.port,
                                      database=db.database)

        # Create a cursor to perform database operations
        cursor = connection.cursor()

        if isinstance(data, list):
            try:
                data=data.values.tolist()
            except ValueError as error:
                template = "An exception of type {0} occurred. Arguments:\n{1!r}"
                message = template.format(type(error).__name__, error.args)
                print (message)

        query = sql.SQL('INSERT INTO {table} VALUES (%s, %f, %f, %f, %f, %f)').format(table=sql.Identifier(ticker))
        cursor.executemany(query, data)
        cursor.commit()

    except (Exception, Error) as error:
        print("Error while connecting to PostgreSQL", error)
    finally:
        cursor.close()
        connection.close()
