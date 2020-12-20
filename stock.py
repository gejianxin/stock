# -*- coding: UTF-8 -*-

import akshare
import os
import pandas as pd


def getStock(path, symbol, start_date='', end_date='', adjust='qfq'):
    f = os.path.join(path, symbol + '.csv')
    if os.path.exists(f) and os.path.isfile(f):
        data = pd.read_csv(f)
        last_date = pd.to_datetime(pd.Series.to_list(data.date)[-1])
        if pd.to_datetime(end_date, format="%Y-%m-%d").__le__(last_date):
            print('您请求的数据已包含在当前磁盘文件中，获取失败退出！')
            return
        if pd.to_datetime(start_date, format="%Y-%m-%d").__gt__(last_date):
            pass
        else:
            start_date = last_date + pd.Timedelta('1 day')

        stock = akshare.stock_zh_a_daily(symbol, start_date, end_date, adjust)
        print('数据文件已存在，将从', start_date.strftime('%Y-%m-%d'), '开始更新数据')
        stock.to_csv(f, header=None, mode='a')
        print('数据已更新至', end_date)

    else:
        stock = akshare.stock_zh_a_daily(symbol, start_date, end_date, adjust)
        if os.path.exists(path) and not os.path.isfile(path):
            stock.to_csv(f)
            print('找到路径，数据文件不存在，新建数据文件！')

        else:
            os.mkdir(path)
            stock.to_csv(f)
            print('未找到路径，新建路径，新建数据文件！')
