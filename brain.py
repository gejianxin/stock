from baostock.login.loginout import login
import numpy as np
import pandas as pd
import backtrader as bt
from datetime import datetime as dt
import requests
import json
from fake_headers import Headers
import baostock as bs


def get_s2n_bar():
    login = bs.login()
    # 显示登陆返回信息
    print('login respond error_code:'+login.error_code)
    print('login respond  error_msg:'+login.error_msg)

    #### 获取交易日信息 ####
    # 2014年11月17日，沪股通启动，总额度为3000亿元人民币，每日额度为130亿元人民币。
    # 2016年12月5日，深股通启动，不设总额度限制，每日额度为130亿元人民币。
    # 2018年4月11日，证监会同意将沪股通和深股通每日额度调整为520亿元人民币，自2018年5月1日起生效。
    # 返回记录有两列 calendar_date & is_trading_day
    # is_trading_day 值为 0 或 1，字符类型
    records = bs.query_trade_dates(start_date='2014-11-17', end_date=dt.today().strftime('%Y-%m-%d'))
    print('query_trade_dates respond error_code:'+records.error_code)
    print('query_trade_dates respond  error_msg:'+records.error_msg)
    result = []
    while (records.error_code == '0') & records.next():
        # 获取一条记录，将记录合并在一起
        result.append(records.get_row_data())
    result = pd.DataFrame(result, columns=records.fields)
    result = result[result['is_trading_day'] == '1']
    #### 登出系统 ####
    bs.logout()

    return len(result)

class S2N():
    data = get_s2n_bar()

def choose_time():
    # 根据北向资金选择入市时机
    # 从 eastmoney 获取北向资金
    # 接口地址：https://push2his.eastmoney.com/api/qt/kamt.kline/get?fields1=f1,f3,f5&fields2=f51,f52&klt=101&lmt=500
    # 返回数据：{"rc":0,"rt":19,"svr":182482249,"lt":1,"full":1,"data":{"hk2sh":["2021-08-27,536923.82"],"hk2sz":["2021-08-27,486030.88"],"s2n":["2021-08-27,1022954.70"]}}
    # '''
    # params: klt, 101 日线； 102 周线； 103 月线； 104 季线； 105 年线
    # params: lmt, 获取 lmt=xxx 时间单位长度数据
    # return: data 数据集合，包含后面几项； hk2sh 沪港通； hk2sz 深港通； s2n 北向资金
    # '''
    bar = S2N.data # 数据长度
    URL = 'https://push2his.eastmoney.com/api/qt/kamt.kline/get?fields1=f1,f3,f5&fields2=f51,f52&klt=101&lmt='+bar
    headers = Headers(os="win", headers=True).generate()
    response = requests.get(URL, headers=headers)
    records = response.json() if response and response.status_code == 200 else None
    records = records['data']['s2n']
    result = []
    for record in records:
        result.append(record.split(','))
    result = pd.DataFrame(result, columns=['date', 'net_flowin'])
    result['date'] = pd.to_datetime(result['date'])
    result['net_flowin'] = pd.to_numeric(result['net_flowin'])
    result.set_index('date', inplace=True)

    # print(result)
    #             net_flowin
    # date                  
    # 2021-08-23   557556.37
    # 2021-08-24   983928.38
    # 2021-08-25   758189.81
    # 2021-08-26   527087.19
    # 2021-08-27  1022954.70

    money
    for i in range(3, bar):


    pass


def choose_ticker(number=1):
    # Calculate all tickers next 

if __name__ == '__main__':
    # Choose right time to trade
