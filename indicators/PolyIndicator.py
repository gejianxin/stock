import backtrader as bt
from backtrader import indicators as btind
import numpy as np
from .HmaIndicator import Hma


class Poly(bt.Indicator):
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
        self.hma = Hma()

    def next(self):
        # self.hma.get获取当前日(ago=0)之前(size=self.params.window)时间周期的数据
        self.fit = np.polynomial.Chebyshev.fit(
            range(self.params.window),
            self.hma.get(ago=0, size=self.params.window),
            self.params.poly
            )
        self.lines.poly[0] = self.fit(range(self.params.window))[-1]
