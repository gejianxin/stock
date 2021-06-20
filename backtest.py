import pandas as pd
import backtrader as bt
import backtrader.analyzers as btanalyzers
from data import get_csv_data
from sizer import MaxRiskSizer
from strategy import KetlerStrategy
from commission import StampDutyCommissionScheme


if __name__ == '__main__':
    data = get_csv_data('data.csv', '2003-01-01', '2005-12-31')
    cerebro = bt.Cerebro()
    cerebro.adddata(data)
    cerebro.addstrategy(KetlerStrategy)
    comminfo = StampDutyCommissionScheme(stamp_duty=0.001, commission=0.0002)
    # cerebro.broker.setcommission(commission=0.0012, margin=False, mult=1)
    cerebro.broker.addcommissioninfo(comminfo)
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
