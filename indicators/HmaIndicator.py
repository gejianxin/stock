import backtrader as bt
from backtrader import indicators as btind


class Hma(bt.Indicator):
    lines = ('hma',)
    params = dict(period=10)
    plotinfo = dict(subplot=False)

    def __init__(self):
        self.lines.hma = btind.HullMovingAverage(period=self.params.period)