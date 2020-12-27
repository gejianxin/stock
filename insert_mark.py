import numpy as np
import pandas as pd


def cal_mark(df:pd.DataFrame, buy_index, sell_index, cal_buy:string, cal_sell:string):
    buy_list = []
    sell_list = []
    is_buy = False
    for i in df[buy_index]:
        if df[cal_buy][i] > df[buy_index][i] and is_buy:
            buy_list.append(df[buy_index][i])
            is_buy = True
        else:
            buy_list.append(np.nan)  # 这里添加nan的目的是，对齐主图的k线数量
        if df[sell_index][i] < df[cal_sell][i] and is_buy:
            sell_list.append(df[sell_index][i])
            is_buy = False
        else:
            sell_list.append(np.nan)
    return buy_list, sell_list

def plot_mark(buy_list, sell_list):
    add_plot = [
        mpf.make_addplot(buy_list, scatter=True, markersize=200, marker='^', color='y'),
        mpf.make_addplot(sell_list, scatter=True, markersize=200, marker='v', color='r'),
    ]
    return add_plot