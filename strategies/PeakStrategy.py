import backtrader as bt
from indicators.PeakIndicator import Peak


class PeakStrategy(bt.Strategy):
    def __init__(self):
        self.data = self.datas[0].close
        self.peak = Peak()
