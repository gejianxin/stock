import re
import math
from datetime import date
from datetime import datetime as dt, timedelta
import pandas as pd
import backtrader as bt
import backtrader.feeds as btfeeds
import psycopg2
from psycopg2 import Error, sql
import baostock as bs
import tushare as ts


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


def get_hs300_stock():
    # 登陆系统
    lg = bs.login()
    # 显示登陆返回信息
    print('login respond error_code:'+lg.error_code)
    print('login respond  error_msg:'+lg.error_msg)

    # 获取沪深300成分股
    records = bs.query_hs300_stocks()
    print('query_hs300 error_code:'+records.error_code)
    print('query_hs300  error_msg:'+records.error_msg)

    # 打印结果集
    hs300_stocks = []
    while (records.error_code == '0') & records.next():
        # 获取一条记录，将记录合并在一起
        hs300_stocks.append(records.get_row_data())
    result = pd.DataFrame(hs300_stocks, columns=records.fields)
    # 结果集输出到csv文件
    # result.to_csv("D:/hs300_stocks.csv", encoding="gbk", index=False)
    # print(result)
    # 登出系统
    bs.logout()
    return result


def get_all_tickers(token):
    pro = ts.pro_api(token)
    tickers = pro.query('stock_basic', exchange='', list_status='L', fields='ts_code, name, area, industry, list_date')
    # 把列名按照baostock格式进行修改
    tickers.columns = ['code', 'code_name', 'area', 'industry', 'list_date']
    code_list = []
    for ticker in tickers['code']:
        code_list.append(convert_ticker_type(ticker, 'baostock'))
    tickers['code'] = code_list
    return tickers


def get_hist_data(ticker, fromdate, todate):
    #### 登陆系统 ####
    lg = bs.login()
    # 显示登陆返回信息
    print('login respond error_code:'+lg.error_code)
    print('login respond  error_msg:'+lg.error_msg)
    ticker = convert_ticker_type(ticker, 'baostock')
    records = bs.query_history_k_data_plus(ticker, 'date,open,high,low,close,volume', start_date=fromdate, end_date=todate, frequency='d', adjustflag='3')
    print('query_history_k_data_plus respond error_code: ', records.error_code)
    print('query_history_k_data_plus respond  error_msg: ', records.error_msg)
    
    # 查询复权因子
    rs_list = []
    rs_factor = bs.query_adjust_factor(code=ticker, start_date=fromdate, end_date=todate)
    while (rs_factor.error_code == '0') & rs_factor.next():
        rs_list.append(rs_factor.get_row_data())
    result_factor = pd.DataFrame(rs_list, columns=rs_factor.fields)
    # 返回示例数据
    # code	dividOperateDate	foreAdjustFactor	backAdjustFactor	adjustFactor
    # sh.600000	2015-06-23	0.663792	6.295967	6.295967
    # sh.600000	2016-06-23	0.751598	7.128788	7.128788
    # sh.600000	2017-05-25	0.989551	9.385732	9.385732
    # 返回数据说明
    # 参数名称	参数描述	算法说明
    # code	证券代码
    # dividOperateDate	除权除息日期	
    # foreAdjustFactor	向前复权因子	除权除息日前一个交易日的收盘价/除权除息日最近的一个交易日的前收盘价
    # backAdjustFactor	向后复权因子	除权除息日最近的一个交易日的前收盘价/除权除息日前一个交易日的收盘价
    # adjustFactor	本次复权因子
    # TODO: 时间段在最后一次除权除息之后
    if dt.strptime(result_factor['dividOperateDate'][-1], format='%Y-%m-%d') < fromdate:
        pass
    elif dt.strptime(result_factor['dividOperateDate'][0], format='%Y-%m-%d') > todate:
        pass
    elif 

    # 打印输出
    print(result_factor)
    

    data_list = []
    while (records.error_code == '0') & records.next():
        # 获取一条记录，将记录合并在一起
        data_list.append(records.get_row_data())
    result = pd.DataFrame(data_list, columns=records.fields)
    # 获取复权后数据
    records = bs.query_history_k_data_plus(ticker, 'close', start_date=fromdate, end_date=todate, frequency='d', adjustflag='2')
    print('query_history_k_data_plus respond error_code: ', records.error_code)
    print('query_history_k_data_plus respond  error_msg: ', records.error_msg)
    data_list = []
    while (records.error_code == '0') & records.next():
        # 获取一条记录，将记录合并在一起
        data_list.append(records.get_row_data())
    result['adjust'] = pd.DataFrame(data_list)
    result = result[['date','open','high','low','close','adjust','volume']]
    result['date'] = pd.to_datetime(result['date']).dt.date
    bs.logout()
    return result


def check_db_date(ticker, db):
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


def get_db_data(ticker, db, fromdate, todate=dt.now().date()):
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


def insert_db_data(ticker, data, db):
    if not isinstance(data, list):
        try:
            # 从baostock获得的数据类型为Dataframe，且不含索引
            # 必须转换为list
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


def update_db_data(ticker, db, fromdate, todate=dt.now().strftime('%Y-%m-%d')):
    # if not isinstance(fromdate, date):
    #     try:
    #         fromdate=dt.strptime(fromdate, '%Y-%m-%d').date()
    #     except ValueError as error:
    #         template = 'An exception of type {0} occurred. Arguments:\n{1!r}'
    #         message = template.format(type(error).__name__, error.args)
    #         print (message)
    # if not isinstance(todate, date):
    #     try:
    #         todate=dt.strptime(todate, '%Y-%m-%d').date()
    #     except ValueError as error:
    #         template = 'An exception of type {0} occurred. Arguments:\n{1!r}'
    #         message = template.format(type(error).__name__, error.args)
    #         print (message)

    timespan = check_db_date(ticker=ticker, db=db)
    if timespan is None:
        print('None data of {ticker}! '.format(ticker=ticker))
        data = get_hist_data(ticker=ticker, fromdate=fromdate, todate=todate)
        insert_db_data(ticker=ticker, data=data, db=db)  # insert data into db
    else:
        firstdate = timespan['firstdate']
        lastdate = timespan['lastdate']

        delta = (dt.strptime(fromdate, '%Y-%m-%d') - firstdate).days
        if delta < 0:  # fromdate < firstday, the database need to fullfil data before firstdate
            # using baostock to get data, make sure data type is list or Dataframe
            data = get_hist_data(ticker=ticker, fromdate=fromdate, todate=dt.strptime(firstdate-timedelta(days=1), '%Y-%m-%d'))
            insert_db_data(ticker=ticker, data=data, db=db)  # insert data into db

        delta = (todate - lastdate).days
        if delta > 0:  # todate > lastday, the database need to fullfil data after lastday
            data = get_hist_data(ticker=ticker, fromdate=dt.strptime(lastdate+timedelta(days=1), '%Y-%m-%d'), todate=todate)
            insert_db_data(ticker=ticker, data=data, db=db)  # insert data into db
        print('{ticker} data update complete!'.format(ticker=ticker))


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
    records = get_db_data(ticker=ticker, db=db, fromdate=fromdate, todate=todate)
    # 删除close列，保留ajust close列
    # records = [record[:4]+record[5:] for record in records]
    df = pd.DataFrame(data=records)
    df.columns = ['date', 'open', 'high', 'low', 'close', 'adjust close', 'volume']
    df = df[['date', 'open', 'high', 'low', 'close', 'volume']]
    print(df)
    df['date'] = pd.to_datetime(df['date'], format='%Y-%m-%d')
    # df['date'] = df['date'].data()
    # df['openinterest'] = 0
    df.set_index(keys='date', inplace=True)
    data = btfeeds.PandasData(dataname=df)
    # data = btfeeds.PandasData(
    #     dataname=df,
    #     fromdate=fromdate,
    #     todate=todate,
    #     datetime=None,
    #     open=-1,
    #     high=-1,
    #     low=-1,
    #     close=-1,
    #     volume=-1,
    #     openinterest=None,
    # )
    return data
