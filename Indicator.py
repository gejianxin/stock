from analyze import rolling_poly9
import backtrader as bt
from backtrader import indicators as btind
import numpy as np


class Ketler(bt.Indicator):
    lines = ('expo', 'atr', 'upper', 'lower')
    params = dict(ema=20, atr=17)
    plotinfo = dict(subplot=False)
    plotlines = dict(
        buy=dict(marker='^', markersize=8.0, color='red', fillstyle='full'),
        sell=dict(marker='v', markersize=8.0, color='green', fillstyle='full'),
        expo=dict(ls='--'),
        upper=dict(_samecolor=True),
        lower=dict(_samecolor=True)
    )

    def __init__(self):
        # self.lines.expo = btind.EMA(self.data.close, period=self.params.ema)
        # self.lines.atr = btind.ATR(
        #     self.data.high,
        #     self.data.low,
        #     self.data.close,
        #     period=self.params.atr)
        self.lines.expo = bt.talib.EMA(self.datas[0].close, timeperiod=self.params.ema)
        self.lines.atr = bt.talib.ATR(self.datas[0].high, self.datas[0].low, self.datas[0].close, timeperiod=self.params.atr)
        self.lines.upper = self.lines.expo + self.lines.atr
        self.lines.lower = self.lines.expo + self.lines.atr


# class CUS_HMA(bt.Indicator):
    # lines = ('hma')
    # params = dict(period=10)
    # plotinfo = dict(subplot=False)

    # def __init__(self):
    #     self.lines.hma = btind.HullMovingAverage(period=self.params.period)


class POLY(bt.Indicator):
    lines = ('poly', 'hma')
    # lines = ('poly',)
    params = dict(poly=9, window=252, step=1, period=10)

    def __init__(self, data):
        self.lines.hma = bt.indicators.HullMovingAverage(period=self.params.period) 
        # 尝试把HMA数据作为POLY指标的参数传入
        # print('hma length is : {}'.format(len(self.lines.hma.values)))
        # self.data = data
        # print('self.data length is : {}'.format(len(self.data)))

    def next(self):
        if len(self.data) < self.params.window:
            self.lines.poly = np.polynomial.Chebyshev.fit(range(len(self.data)), self.data, self.params.poly)
        if len(self.data) >= self.params.window:
            self.fit = np.polynomial.Chebyshev.fit(range(self.params.window), self.data.get(ago=-self.params.window, size=self.params.window), self.params.poly)
            self.lines.poly[0] = self.fit(range(self.params.window))[-1]


    # def rolling_poly(data, window, step, poly):
    #     if len(data) < window:
    #         index = range(len(data))
    #         fit_params = np.polynomial.Chebyshev.fit(index, data, poly)
    #         fit_data = fit_params(index)
    #         return fit_data
    #     else:
    #         index = range(window)
    #         fit_params = np.polynomial.Chebyshev.fit(index, data, poly)
    #         fit_data = fit_params(index)[-1]

