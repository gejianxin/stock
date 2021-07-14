import pandas as pd
import re
import math
from datetime import datetime as dt, timedelta
from datetime import date
import backtrader as bt
import backtrader.feeds as btfeeds
import psycopg2
from psycopg2 import Error, sql
import tushare as ts
import yfinance as yf
import baostock as bs


# Get all tickers
def get_all_tickers(token):
    pro = ts.pro_api(token)
    data = pro.query('stock_basic', exchange='', list_status='L', fields='ts_code, symbol, name, area, industry, list_date')
    return data


def btfeeds_csv_data(pathname, fromdate, todate):
    if not isinstance(fromdate, date):
        try:
            fromdate=dt.strptime(fromdate, '%Y-%m-%d').date()
        except ValueError as error:
            template = 'An exception of type {0} occurred. Arguments:\n{1!r}'
            message = template.format(type(error).__name__, error.args)
            print (message)
    if not isinstance(todate, date):
        try:
            todate=dt.strptime(todate, '%Y-%m-%d').date()
        except ValueError as error:
            template = 'An exception of type {0} occurred. Arguments:\n{1!r}'
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


def btfeeds_online_data(ticker, fromdate, todate):
    if not isinstance(fromdate, date):
        try:
            fromdate=dt.strptime(fromdate, '%Y-%m-%d').date()
        except ValueError as error:
            template = 'An exception of type {0} occurred. Arguments:\n{1!r}'
            message = template.format(type(error).__name__, error.args)
            print (message)
    if not isinstance(todate, date):
        try:
            todate=dt.strptime(todate, '%Y-%m-%d').date()
        except ValueError as error:
            template = 'An exception of type {0} occurred. Arguments:\n{1!r}'
            message = template.format(type(error).__name__, error.args)
            print (message)

    data = btfeeds.YahooFinanceData(dataname=ticker, fromdate=fromdate, todate=todate, timeframe=bt.TimeFrame.Days)
    return data


def btfeeds_db_data(ticker, db, fromdate, todate):
    if not isinstance(fromdate, date):
        try:
            fromdate=dt.strptime(fromdate, '%Y-%m-%d')
        except ValueError as error:
            template = 'An exception of type {0} occurred. Arguments:\n{1!r}'
            message = template.format(type(error).__name__, error.args)
            print (message)
    if not isinstance(todate, date):
        try:
            todate=dt.strptime(todate, '%Y-%m-%d')
        except ValueError as error:
            template = 'An exception of type {0} occurred. Arguments:\n{1!r}'
            message = template.format(type(error).__name__, error.args)
            print (message)
    records = get_ticker_data(ticker=ticker, db=db, fromdate=fromdate, todate=todate)
    # 删除close列，保留ajust close列
    records = [record[:4]+record[5:] for record in records]
    df = pd.DataFrame(data=records)
    df.columns = ['date', 'open', 'high', 'low', 'close', 'volume']
    df['date'] = pd.to_datetime(df['date'], format='%Y-%m-%d')
    df['openinterest'] = 0
    df.set_index(keys='date', inplace=True)

    data = btfeeds.PandasData(dataname=df)
    return data


def update_ticker_data(ticker, db, proxy, fromdate, todate=dt.now().date()):
    if not isinstance(fromdate, date):
        try:
            fromdate=dt.strptime(fromdate, '%Y-%m-%d').date()
        except ValueError as error:
            template = 'An exception of type {0} occurred. Arguments:\n{1!r}'
            message = template.format(type(error).__name__, error.args)
            print (message)
    if not isinstance(todate, date):
        try:
            todate=dt.strptime(todate, '%Y-%m-%d').date()
        except ValueError as error:
            template = 'An exception of type {0} occurred. Arguments:\n{1!r}'
            message = template.format(type(error).__name__, error.args)
            print (message)

    timespan = check_ticker_date(ticker, db=db)
    if timespan == None:
        print('None data of {ticker}! '.format(ticker=ticker))
        data = yf.download(tickers=ticker, start=fromdate, end=todate, proxy=proxy)
        insert_ticker_data(ticker=ticker, data=data, db=db)  # insert data into db
    else:
        firstdate = timespan['firstdate']
        lastdate = timespan['lastdate']

        delta = (fromdate - firstdate).days
        if delta < 0:  # fromdate < firstday, the database need to fullfil data before firstdate
            # using yfinance to get data, make sure data type is list or Dataframe
            data = yf.download(tickers=ticker, start=fromdate, end=firstdate-timedelta(days=1), proxy=proxy)
            insert_ticker_data(ticker=ticker, data=data, db=db)  # insert data into db

        delta = (todate - lastdate).days
        if delta > 0:  # todate > lastday, the database need to fullfil data after lastday
            data = yf.download(tickers=ticker, start=lastdate+timedelta(days=1), end=todate, proxy=proxy)
            insert_ticker_data(ticker=ticker, data=data, db=db)  # insert data into db
        print('{ticker} data update complete!'.format(ticker=ticker))


# def update_all_data(fromdate, db, todate=dt.now().date()):
#     if not isinstance(fromdate, date):
#         try:
#             fromdate=dt.strptime(fromdate, '%Y-%m-%d').date()
#         except ValueError as error:
#             template = 'An exception of type {0} occurred. Arguments:\n{1!r}'
#             message = template.format(type(error).__name__, error.args)
#             print (message)
#     if not isinstance(todate, date):
#         try:
#             todate=dt.strptime(todate, '%Y-%m-%d').date()
#         except ValueError as error:
#             template = 'An exception of type {0} occurred. Arguments:\n{1!r}'
#             message = template.format(type(error).__name__, error.args)
#             print (message)
#     tickers = get_all_tickers(token=TOKEN)
#     for i in range(len(tickers)):
#         update_ticker_data(ticker=tickers['ts_code'][i], fromdate=fromdate, todate=todate, db=db)


def get_ticker_data(ticker, db, fromdate, todate=dt.now().date()):
    if not isinstance(fromdate, date):
        try:
            fromdate=dt.strptime(fromdate, '%Y-%m-%d').date()
        except ValueError as error:
            template = 'An exception of type {0} occurred. Arguments:\n{1!r}'
            message = template.format(type(error).__name__, error.args)
            print (message)
    if not isinstance(todate, date):
        try:
            todate=dt.strptime(todate, '%Y-%m-%d').date()
        except ValueError as error:
            template = 'An exception of type {0} occurred. Arguments:\n{1!r}'
            message = template.format(type(error).__name__, error.args)
            print (message)

    try:
        # Connect to an existing database
        connection = psycopg2.connect(user=db['username'],
                                      password=db['password'],
                                      host=db['host'],
                                      port=db['port'],
                                      database=db['database'])

        # Create a cursor to perform database operations
        cursor = connection.cursor()
        query = sql.SQL('SELECT * FROM {table} WHERE DATE BETWEEN %s AND %s ORDER BY {date} ASC').format(table=sql.Identifier(ticker), date=sql.Identifier('date'))
        cursor.execute(query, (fromdate, todate))
        records = cursor.fetchall()
        return records
    except (Exception, Error) as error:
        print('Error while connecting to PostgreSQL', error)
    finally:
        cursor.close()
        connection.close()
        print('Query complete.')


def insert_ticker_data(ticker, data, db):
    if not isinstance(data, list):
        try:
            # 从yfinance获得的Dataframe以日期为索引，所以插入数据库之前必须把索引转换为列
            # 从tushare获得的数据列与数据库不一致，必须进行数据转换，此处仅以yfinance数据为准
            data.reset_index(inplace=True)
            data=data.values.tolist()
        except ValueError as error:
            template = 'An exception of type {0} occurred. Arguments:\n{1!r}'
            message = template.format(type(error).__name__, error.args)
            print (message)

    try:
        # Connect to an existing database
        connection = psycopg2.connect(user=db['username'],
                                      password=db['password'],
                                      host=db['host'],
                                      port=db['port'],
                                      database=db['database'])
        # Create a cursor to perform database operations
        cursor = connection.cursor()
        query = sql.SQL('CREATE TABLE IF NOT EXISTS {table} (date DATE PRIMARY KEY, open FLOAT4, high FLOAT4, low FLOAT4, close FLOAT4, adjust FLOAT4, volumn INT)').format(table=sql.Identifier(ticker))
        cursor.execute(query)
        connection.commit()
        query = sql.SQL('INSERT INTO {table} VALUES (%s, %s, %s, %s, %s, %s, %s)').format(table=sql.Identifier(ticker))
        cursor.executemany(query, data)
        connection.commit()
    except (Exception, Error) as error:
        print('Error while connecting to PostgreSQL', error)
    finally:
        cursor.close()
        connection.close()
        print('Insert complete.')


def check_ticker_date(ticker, db):
    try:
        # Connect to an existing database
        connection = psycopg2.connect(user=db['username'],
                                      password=db['password'],
                                      host=db['host'],
                                      port=db['port'],
                                      database=db['database'])
        # Create a cursor to perform database operations
        cursor = connection.cursor()
        # query = sql.SQL('SELECT {date} FROM {table} WHERE dateti BETWEEN %s AND %s ORDER BY date ASC').format(date=sql.Identifier('date'), table=sql.Identifier(ticker))
        # cursor.execute(query, ('2000-01-01', '2003-01-10'))
        query = sql.SQL('CREATE TABLE IF NOT EXISTS {table} (date DATE PRIMARY KEY, open FLOAT4, high FLOAT4, low FLOAT4, close FLOAT4, adjust FLOAT4, volumn INT)').format(table=sql.Identifier(ticker))
        cursor.execute(query)
        connection.commit()
        query = sql.SQL('SELECT {date} FROM {table} ORDER BY {date} ASC').format(date=sql.Identifier('date'), table=sql.Identifier(ticker))
        cursor.execute(query)
        records = cursor.fetchall()
        if records == []:
            return None
        else:
            timespan = dict(
                firstdate=records[0][0], # records是list类型， records[0]是tuple类型（每行记录包含多个字段）， 再取记录中第一个字段
                lastdate=records[-1][0]
            )
        return timespan
    except (Exception, Error) as error:
        print('Error while connecting to PostgreSQL', error)
    finally:
        cursor.close()
        connection.close()


def convert_ticker_type(ticker, style):
    if style == 'yahoo':  # yfinance接受的股票代码格式
        market = re.search('[a-zA-Z]{2}', ticker).group()
        code = re.search('\d{6}', ticker).group()
        ticker = '.'.join([code, market.upper()])
        return ticker
    elif style == 'baostock':  # baostock接受的股票代码模式
        market = re.search('[a-zA-Z]{2}', ticker).group()
        code = re.search('\d{6}', ticker).group()
        ticker = '.'.join([market.lower(), code])
        return ticker
