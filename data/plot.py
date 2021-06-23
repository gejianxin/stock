import mplfinance as mpf
import pandas as pd
import talib
import analyze


f = 'C:\\Users\\User\\Documents\\data\\sh600000.csv'
df = pd.read_csv(f, index_col=0, parse_dates=True)
# 设置k线图颜色
my_color = mpf.make_marketcolors(up='red',  # 上涨时为红色
                                 down='green',  # 下跌时为绿色
                                 edge='i',  # 隐藏k线边缘
                                 volume='in',  # 成交量用同样的颜色
                                 inherit=True)

my_style = mpf.make_mpf_style(gridaxis='both',  # 设置网格
                              gridstyle='-.',
                              y_on_right=True,
                              marketcolors=my_color)
# 计算OBV
# df['OBV'] = talib.OBV(df.Close,df.Volume)
# #计算布林带上中下轨
# #matype=talib.MA_Type.T3表示用指数移动平均的方法进行平均
# df['upper'],df['middle'],df['lower'] = talib.BBANDS(df.Close, matype=talib.MA_Type.T3)
# #设置要显示的信息
# add_plot = [mpf.make_addplot(df[['upper','lower']],linestyle='dashdot'),
#             mpf.make_addplot(df['middle'],linestyle='dotted',color='y'),
#             mpf.make_addplot(df['OBV'],panel='lower',color='b')]#panel为lower表示在附图中显示

# mpf.plot(df,type='candle',
#          style=my_style,
#          addplot=add_plot,
#          volume=True,
#          figratio=(2,1),
#          figscale=5,)
# df['rsi'] = talib.RSI(df['close'].values)
poly9_hma10 = analyze.poly9(df['close'].values, 252, 10)
poly9_hma5 = analyze.poly9(df['close'].values, 252, 5)

add_plot = [mpf.make_addplot(poly9_hma10, color='b'),
            mpf.make_addplot(poly9_hma5, color='r'), ]
# k, d = talib.ST
mpf.plot(df, type='candle',
         style=my_style,
         volume=True,  # 展示成交量副图
         addplot=add_plot,
         figratio=(2, 1),  # 设置图片大小
         figscale=5)
