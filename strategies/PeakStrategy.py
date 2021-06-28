import backtrader as bt
from indicators.PeakIndicator import Peak


class PeakStrategy(bt.Strategy):
    def __init__(self):
        self.data = self.datas[0].close
        self.peak = Peak()

    def next(self):
        if not self.position:
            if self.peak[0] == -1:
                self.order = self.buy()
        else:
            if self.peak[0] == 1:
                self.order = self.sell()
