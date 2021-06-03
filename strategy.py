import backtrader as bt
# import backtrader.feeds as btfeeds
# import backtrader.indicators as btind
from data import get_data


class MyStrategy(bt.Strategy):
    def log(self, txt, dt=None):
        ''' Logging function for this strategy'''
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))

    def __init__(self):
        self.close = self.datas[0].close
        # bt.indicators.SMA(period=15)
        # self.sma = btind.rsi(period=15)
        # Write down: no pending order

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            # Buy/Sell order submitted/accepted to/by broker - Nothing to do
            return

        # Check if an order has been completed
        # Attention: broker could reject order if not enough cash
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log('【开仓】  价格： {:.2f}  总价： {.2f}  佣金： {.2f}'.format(
                    order.executed.price,
                    order.executed.value,
                    order.executed.comm))
            elif order.issell():
                self.log('【平仓】  价格： {:.2f}  总价： {.2f}  佣金： {.2f}'.format(
                    order.executed.price,
                    order.executed.value,
                    order.executed.comm))

            self.bar_executed = len(self)

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')

        self.order = None

    def notify_trade(self, trade):
        if not trade.isclosed:
            pass
        else:
            self.log('【单笔交易盈利】  毛利： {:.2f}  净利： {:.2f}'.format(
                trade.pnl, trade.pnlcomm))

    def next(self):
        # if self.sma > self.data.close:
        #     # Do something
        #     pass

        # elif self.sma < self.data.close:
        #     # Do something else
        #     pass
        # Simply log the closing price of the series from the reference
        self.log('Close, %.2f' % self.close[0])

        if self.close[0] < self.close[-1]:
            # current close less than previous close

            if self.close[-1] < self.close[-2]:
                # previous close less than the previous close

                # BUY, BUY, BUY!!! (with all possible default parameters)
                self.log('BUY CREATE, %.2f' % self.close[0])
                self.buy()


if __name__ == '__main__':
    # data = btfeeds.YahooFinanceData(dataname='600000.SS',
    #                                 fromdate=datetime.datetime(2018, 1, 1),
    #                                 todate=datetime.datetime(2021, 10, 10),
    #                                 timeframe=bt.TimeFrame.Days
    #                                 )

    cerebro = bt.Cerebro()
    cerebro.adddata(get_data('data.csv', '2003-01-01', '2005-12-31'))
    cerebro.addstrategy(MyStrategy)
    cerebro.broker.setcommission(commission=0.001, margin=False, mult=1)
    cerebro.broker.setcash(10000)
    # cerebro.addsizer

    # Print out the starting conditions
    print('【初始资金】  %.2f' % cerebro.broker.getvalue())

    # Run over everything
    cerebro.run()

    # Print out the final result
    print('【结束资金】  %.2f' % cerebro.broker.getvalue())

    cerebro.plot(style='candle')
