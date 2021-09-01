import os
from datetime import datetime as dt
import pandas as pd
import backtrader as bt
# import backtrader.analyzers as btanalyzers
# import backtrader.feeds as btfeeds
# from backtrader_plotting import Bokeh
from tools.data_baostock import btfeeds_db_data, btfeeds_online_data, get_db_data
from config.sizer import MaxRiskSizer
from config.commission import StampDutyCommissionScheme
from config.essential import DB
# from strategies.KetlerStrategy import KetlerStrategy
# from strategies.PolyStrategy import PolyStrategy
from strategies.PeakStrategy import PeakStrategy
# from indicators.MAPower import ma_power


if __name__ == '__main__':
    ticker = 'sz.000009'
    fromdate = '2014-01-01'
    todate = '2018-12-31'
    data = btfeeds_db_data(ticker=ticker, db=DB, fromdate=fromdate, todate=todate)
    # calculate natural return ratio of ticker
    # records columns are ['date', 'open', 'high', 'low', 'close', 'adjust close', 'volume']
    records = get_db_data(ticker=ticker, db=DB, fromdate=fromdate, todate=todate)
    stock_return = (records[len(records)-1][5] - records[0][5])/records[0][5]

    # calculate shanghai index return of the same period
    records = get_db_data(ticker='sh.600036', db=DB, fromdate=fromdate, todate=todate)
    sh_return = (records[len(records)-1][5] - records[0][5])/records[0][5]
    # calculate shenzhen index return of the same period
    records = get_db_data(ticker='sh.600037', db=DB, fromdate=fromdate, todate=todate)
    sz_return = (records[len(records)-1][5] - records[0][5])/records[0][5]

    # dataframe= pd.read_csv(filepath_or_buffer='./data/data.csv',
    #                         # skiprows=skiprows,
    #                         # header=header,
    #                         parse_dates=True,
    #                         index_col=0)
    # dataframe = dataframe.iloc[:,[0,1,2,4,5]]
    # dataframe.columns = ['open', 'high', 'low', 'close', 'volume']
    # data = bt.feeds.PandasData(dataname=dataframe)

    # data = btfeeds.YahooFinanceCSVData('data/data.csv', fromdate='2003-01-01', todate='2005-12-31')

    # create Cerebro instance without default observers
    cerebro = bt.Cerebro(stdstats=False)

    # add data
    cerebro.adddata(data)
    # add strategy
    # cerebro.addstrategy(KetlerStrategy)
    # cerebro.addstrategy(PolyStrategy)
    cerebro.addstrategy(PeakStrategy)

    # setup commission and add commission
    comminfo = StampDutyCommissionScheme(stamp_duty=0.001, commission=0.02)
    # cerebro.broker.setcommission(commission=0.0012, margin=False, mult=1)
    cerebro.broker.addcommissioninfo(comminfo)

    # setup cash
    cerebro.broker.setcash(10000)

    # add risk factor
    cerebro.addsizer(MaxRiskSizer)

    # add observer
    # Broker 包含 Cash 和 Value ，可以根据需要分别添加相应 observer 或者使用 Broker 同时添加两者
    # cerebro.addobserver(bt.observers.Broker)
    # cerebro.addobserver(bt.observers.Cash)
    cerebro.addobserver(bt.observers.Value)
    cerebro.addobserver(bt.observers.Trades)
    cerebro.addobserver(bt.observers.BuySell)
    # cerebro.addobserver(bt.observers.DrawDown)
    cerebro.addobserver(bt.observers.TimeReturn)

    # add analyzer
    cerebro.addanalyzer(bt.analyzers.SharpeRatio)
    cerebro.addanalyzer(bt.analyzers.DrawDown)
    cerebro.addanalyzer(bt.analyzers.TradeAnalyzer)
    cerebro.addanalyzer(bt.analyzers.Transactions)
    cerebro.addanalyzer(bt.analyzers.Returns)

    # Print out the starting conditions

    # Run over everything
    res = cerebro.run()[0]

    # 总交易完成次数
    # res.analyzers.tradeanalyzer.get_analysis()['total']['closed']
    # 总盈利次数
    # res.analyzers.tradeanalyzer.get_analysis()['won']['total']

    # 盈利交易总金额、平均每笔盈利、最高单笔盈利
    # res.analyzers.tradeanalyzer.get_analysis()['won']['pnl']['total']
    # res.analyzers.tradeanalyzer.get_analysis()['won']['pnl']['average']
    # res.analyzers.tradeanalyzer.get_analysis()['won']['pnl']['max']

    # 总亏损次数
    # res.analyzers.tradeanalyzer.get_analysis()['lost']['total']

    # 亏损交易总金额、平均每笔盈利、最高单笔盈利
    # res.analyzers.tradeanalyzer.get_analysis()['lost']['pnl']['total']
    # res.analyzers.tradeanalyzer.get_analysis()['lost']['pnl']['average']
    # res.analyzers.tradeanalyzer.get_analysis()['lost']['pnl']['max']

    # 总K线数量
    # res.analyzers.tradeanalyzer.get_analysis()['len']['total']
    # 平均每笔交易间隔
    # res.analyzers.tradeanalyzer.get_analysis()['len']['average']
    # 单笔交易最长间隔
    # res.analyzers.tradeanalyzer.get_analysis()['len']['max']
    # 单笔最短间隔
    # res.analyzers.tradeanalyzer.get_analysis()['len']['min']


    # Print out the final cash value
    # print('【结束资金】  %.2f' % cerebro.broker.getvalue())

    outcome = [[cerebro.broker.getvalue(),
                stock_return,
                sh_return,
                sz_return,
                res.analyzers.returns.get_analysis()['rtot'],
                res.analyzers.returns.get_analysis()['rnorm'],
                res.analyzers.drawdown.get_analysis()['max']['drawdown']/100,
                res.analyzers.sharperatio.get_analysis()['sharperatio'],
                res.analyzers.tradeanalyzer.get_analysis()['total']['closed'],
                res.analyzers.tradeanalyzer.get_analysis()['won']['total']/res.analyzers.tradeanalyzer.get_analysis()['total']['closed']
                ]]
    df = pd.DataFrame(
        outcome,
        columns=['Total', 'NaturalReturn', 'SHNaturalReturn', 'SZNaturalReturn', 'StrategyReturn', 'AnnualReturn', 'MaxDrawdown', 'SharpRatio', 'Trades Count', 'WinRatio']
        )
    print(df)
    if os.path.isfile('./data/{date}.csv'.format(date=dt.today().date())):
        df.to_csv('./data/{date}.csv'.format(date=dt.today().date()), mode='a', index=False, header=False)
    else:
        df.to_csv('./data/{date}.csv'.format(date=dt.today().date()), index=False)
    # print(df)
    # b = Bokeh(style='bar', plot_mode='single')
    # cerebro.plot(b)
    # cerebro.plot(style='candle')
