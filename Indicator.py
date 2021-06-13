# from analyze import rolling_poly9
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
        self.lines.expo = bt.talib.EMA(self.datas[0].close,
                                       timeperiod=self.params.ema
                                       )
        self.lines.atr = bt.talib.ATR(self.datas[0].high,
                                      self.datas[0].low,
                                      self.datas[0].close,
                                      timeperiod=self.params.atr
                                      )
        self.lines.upper = self.lines.expo + self.lines.atr
        self.lines.lower = self.lines.expo + self.lines.atr


class HMA(bt.Indicator):
    lines = ('hma',)
    params = dict(period=10)
    plotinfo = dict(subplot=False)

    def __init__(self):
        self.lines.hma = btind.HullMovingAverage(period=self.params.period)


class POLY(bt.Indicator):
    # 采用九次多项式(poly=9)进行拟合，默认窗口大小(window=252)，滑动步长(step=1)
    lines = ('poly',)
    params = dict(poly=9,
                  window=252,
                  step=1
                  )
    plotinfo = dict(subplot=False)

    def __init__(self):
        # 设定该指标运算所需最小的时间周期
        self.addminperiod(self.params.window)
        # 生成HMA对象
        self.hma = HMA()

    def next(self):
        # self.hma.get获取当前日(ago=0)之前(size=self.params.window)时间周期的数据
        self.fit = np.polynomial.Chebyshev.fit(
            range(self.params.window),
            self.hma.get(ago=0, size=self.params.window),
            self.params.poly
            )
        self.lines.poly[0] = self.fit(range(self.params.window))[-1]
