import numpy as np
import backtrader as bt
import talib
from indicators.PeakIndicator import Peak
from tools.logger import order_logger, trade_logger


class PeakStrategy(bt.Strategy):
    def __init__(self):
        self.data = self.datas[0].close
        self.peak = Peak()
        print('Start')
    
    @order_logger
    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            # Buy/Sell order submitted/accepted to/by broker - Nothing to do
            return

        self.order = None

    @trade_logger
    def notify_trade(self, trade):
        pass

    def next(self):
        ma5 = bt.talib.MA(self.data, timeperiod=5)
        ma30 = bt.talib.MA(self.data, timeperiod=30)
        rsi = bt.talib.RSI(self.data, timeperiod=6)
        print('rsi = ', rsi)
        algo = self.peak.algo[-1] + self.peak.algo[-2] + self.peak.algo[-3]
        if not self.position:
            if algo <= -1 and bt.indicators.CrossUp(ma5[0], ma30[0]) and rsi[0] < 20:
                self.order = self.buy()
        else:
            if algo >= 1 and bt.indicators.CrossDown(ma5[0], ma30[0]) and rsi[0] > 80:
                self.order = self.sell()
