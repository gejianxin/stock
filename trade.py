import numpy as np
import pandas as pd


indicator_long = False
indicator_short = False
indicator_buy = False
indicator_sell = False
is_buy = False

if not is_buy and indicator_buy: # 空仓遇到买点
    pass
else:
    pass

if is_buy and indicator_buy: # 持仓遇到买点
    pass
elif is_buy and indicator_sell: # 持仓遇到卖点
    # to sell
elif is_buy and indicator_long: # 持仓遇到持有信号
    pass
elif is_buy and indicator_short: # 持仓遇到看跌信号
    pass


def cal_indicator(df: pd.DataFrame):
    for trade_date in df.index:
        # item = df.loc[df.index == '2020-05-08'] date列自动转化为df索引
        # print('type of df item is: {}'.format(type(item)))
        # type of df item is: <class 'pandas.core.frame.DataFrame'>
        # print('the content of item is: {}'.format(item)
        # the content of item is:             open  high   low  close      volume  outstanding_share  turnover
        item = df.loc[df.index == trade_date]
        if not is_buy and item.poly9_hma5 < item.poly9_hma10 and item.close > item.poly9_hma5:
            is_buy = True
            #TODO