import backtrader as bt
import pandas as pd

# import data, sizer, indicator, analyzer
from data import get_csv_data
from sizer import MaxRiskSizer
from indicator import Ketler, HMA, POLY
import backtrader.analyzers as btanalyzers


class MyStrategy(bt.Strategy):
    def log(self, txt, dt=None):
        ''' Logging function for this strategy'''
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))

    def __init__(self):
        self.close = self.datas[0].close
        self.ketler = Ketler()
        # self.hma = bt.indicators.HullMovingAverage(period=10)
        self.hma = HMA()
        self.poly = POLY()

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            # Buy/Sell order submitted/accepted to/by broker - Nothing to do
            return

        # Check if an order has been completed
        # Attention: broker could reject order if not enough cash
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(
                    '【开仓】  价格： {:.2f}  数量： {:d}  总价： {:.2f}  佣金： {:.2f}'.
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
                    '【平仓】  价格： {:.2f}  数量： {:d}  总价： {:.2f}  佣金： {:.2f}'.
                    format(
                        order.executed.price,
                        order.size,
                        order.executed.value,
                        order.executed.comm
                        ))

            # self.bar_executed = len(self)

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
        if not self.position:
            if self.close[0] > self.ketler.lower[0]:
                self.order = self.buy()
        else:
            if self.close[0] < self.ketler.upper[0]:
                self.order = self.sell()


if __name__ == '__main__':
    data = get_csv_data('data.csv', '2003-01-01', '2005-12-31')
    cerebro = bt.Cerebro()
    cerebro.adddata(data)
    cerebro.addstrategy(MyStrategy)
    cerebro.broker.setcommission(commission=0.0012, margin=False, mult=1)
    cerebro.broker.setcash(10000)
    cerebro.addsizer(MaxRiskSizer)
    cerebro.addanalyzer(btanalyzers.SharpeRatio, _name='sharpe')
    cerebro.addanalyzer(btanalyzers.DrawDown, _name='drawdown')
    cerebro.addanalyzer(btanalyzers.Returns, _name='returns')

    # Print out the starting conditions
    print('【初始资金】  %.2f' % cerebro.broker.getvalue())

    # Run over everything
    back = cerebro.run()

    # Print out the final result
    print('【结束资金】  %.2f' % cerebro.broker.getvalue())

    par_list = [[x.analyzers.returns.get_analysis()['rtot'],
                 x.analyzers.returns.get_analysis()['rnorm100'],
                 x.analyzers.drawdown.get_analysis()['max']['drawdown'],
                 x.analyzers.sharpe.get_analysis()['sharperatio']
                 ] for x in back]
    par_df = pd.DataFrame(
        par_list,
        columns=['Total Return', 'APR', 'Drawdown', 'SharpRatio']
        )
    print(par_df)

    # cerebro.plot()
    cerebro.plot(style='candle')
