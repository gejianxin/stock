import pandas as pd
import backtrader as bt
import backtrader.analyzers as btanalyzers
import backtrader.feeds as btfeeds
# from backtrader_plotting import Bokeh
from tools.data_baostock import btfeeds_db_data, btfeeds_online_data
from config.sizer import MaxRiskSizer
from config.commission import StampDutyCommissionScheme
from config.essential import DB
from strategies.KetlerStrategy import KetlerStrategy
# from strategies.PolyStrategy import PolyStrategy
# from strategies.PeakStrategy import PeakStrategy
# from indicators.MAPower import ma_power


if __name__ == '__main__':
    data = btfeeds_db_data(ticker='sz.000009', db=DB, fromdate='2014-01-01', todate='2015-12-31')
    # # print(dataframe)
    # dataframe= pd.read_csv(filepath_or_buffer='./data/data.csv',
    #                         # skiprows=skiprows,
    #                         # header=header,
    #                         parse_dates=True,
    #                         index_col=0)
    # dataframe = dataframe.iloc[:,[0,1,2,4,5]]
    # dataframe.columns = ['open', 'high', 'low', 'close', 'volume']
    # print(dataframe)
    # data = bt.feeds.PandasData(dataname=dataframe)
    print(dir(data.params))
    # data = btfeeds.YahooFinanceCSVData('data/data.csv', fromdate='2003-01-01', todate='2005-12-31')
    cerebro = bt.Cerebro()
    cerebro.adddata(data)
    cerebro.addstrategy(KetlerStrategy)
    # cerebro.addstrategy(PolyStrategy)
    # cerebro.addstrategy(PeakStrategy)
    comminfo = StampDutyCommissionScheme(stamp_duty=0.001, commission=0.02)
    # cerebro.broker.setcommission(commission=0.0012, margin=False, mult=1)
    cerebro.broker.addcommissioninfo(comminfo)
    cerebro.broker.setcash(10000)
    cerebro.addsizer(MaxRiskSizer)
    cerebro.addanalyzer(btanalyzers.SharpeRatio, _name='sharpe')
    cerebro.addanalyzer(btanalyzers.DrawDown, _name='drawdown')
    cerebro.addanalyzer(btanalyzers.Returns, _name='returns')

    # Print out the starting conditions

    # Run over everything
    back = cerebro.run()
    back.analyze

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
    # b = Bokeh(style='bar', plot_mode='single')
    # cerebro.plot(b)
    # cerebro.plot(style='candle')
