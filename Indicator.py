import backtrader as bt
from backtrader import indicators as btind


class Ketler(bt.Indicator):
    lines = ('expo', 'atr', 'upper', 'lower')
    params = dict(ema=20, atr=17)
    plotinfo = dict(subplot=False)
    plotlines = dict(
        buy=dict(marker='^', markersize=8.0, color='red', fillstyle='full'),
        sell=dict(marker='v', markersize=8.0, color='green', fillstyle='full'),
        expo=dict(ls='--'),
        upper=dict(_samecolor=True),
        lower=dict(_samecolor=True)
    )

    def __init__(self):
        # self.lines.expo = btind.EMA(self.data.close, period=self.params.ema)
        # self.lines.atr = btind.ATR(
        #     self.data.high,
        #     self.data.low,
        #     self.data.close,
        #     period=self.params.atr)
        self.lines.expo = bt.talib.EMA(self.datas[0].close, timeperiod=self.params.ema)
        self.lines.atr = bt.talib.ATR(self.datas[0].high, self.datas[0].low, self.datas[0].close, timeperiod=self.params.atr)
        self.lines.upper = self.lines.expo + self.lines.atr
        self.lines.lower = self.lines.expo + self.lines.atr

class HMA(bt.Indicator):
    lines = ('wma', 'hma',)