import backtrader as bt
import backtrader.feeds as btfeeds
import backtrader.indicators as btind
import datetime


class MyStrategy(bt.Strategy):
    def log(self, txt, dt=None):
        ''' Logging function for this strategy'''
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))

    def __init__(self):
        self.close = self.datas[0].close
        bt.indicators.SMA(period=15)

        self.sma = btind.rsi(period=15)

    def next(self):
        if self.sma > self.data.close:
            # Do something
            pass

        elif self.sma < self.data.close:
            # Do something else
            pass


if __name__ == '__main__':
    data = btfeeds.YahooFinanceData(dataname='600000.SS',
                                    fromdate=datetime.datetime(2018, 1, 1),
                                    todate=datetime.datetime(2021, 10, 10),
                                    timeframe=bt.TimeFrame.Days
                                    )
    cerebro = bt.Cerebro()
    cerebro.adddata(data)
    cerebro.addstrategy(MyStrategy)
    cerebro.broker.setcommission(commission=0.001, margin=False, mult=1)
    cerebro.broker.setcash(10000)

    # Print out the starting conditions
    print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())

    # Run over everything
    cerebro.run()

    # Print out the final result
    print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())

    cerebro.plot()
