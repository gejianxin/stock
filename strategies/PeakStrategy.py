import backtrader as bt
import talib
from indicators.PeakIndicator import Peak


class PeakStrategy(bt.Strategy):
    def __init__(self):
        self.data = self.datas[0].close
        self.peak = Peak()
        print('Start')
    
        def notify_order(self, order):
            if order.status in [order.Submitted, order.Accepted]:
                # Buy/Sell order submitted/accepted to/by broker - Nothing to do
                return

            # Check if an order has been completed
            # Attention: broker could reject order if not enough cash
            if order.status in [order.Completed]:
                if order.isbuy():
                    self.log(
                        '【开仓】  价格： {:6.2f}  数量： {:6d}  总价： {:8.2f}  佣金： {:6.2f}'.
                        format(
                            order.executed.price,
                            order.size,
                            order.executed.value,
                            order.executed.comm
                            ))
                    self.buyprice = order.executed.price
                    self.buycomm = order.executed.comm
                elif order.issell():
                    self.log(
                        '【平仓】  价格： {:6.2f}  数量： {:6d}  总价： {:8.2f}  佣金： {:6.2f}'.
                        format(
                            order.executed.price,
                            order.size,
                            order.executed.value,
                            order.executed.comm
                            ))

                self.bar_executed = len(self)

            elif order.status in [order.Canceled, order.Margin, order.Rejected]:
                self.log('Order Canceled/Margin/Rejected')

            self.order = None

    def notify_trade(self, trade):
        if trade.isclosed:
            self.log('【单笔交易盈利】  毛利： {:8.2f}  净利： {:8.2f}'.format(
                trade.pnl, trade.pnlcomm))

    def next(self):
        if not self.position:
            if self.peak.algo[0] == -1:
            # if self.peak.algo[0] == -1 & talib.RSI(self.data, timeperiod=6)[0] < 20:
                self.order = self.buy()
        else:
            if self.peak.algo[0] == 1:
                self.order = self.sell()
