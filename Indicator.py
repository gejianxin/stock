import backtrader as bt


class Ketler(bt.Indicator):
    lines = dict(upper='upperline',
                 middle='middleline',
                 lower='lowerline')
    params = dict(ema=20, atr=17)
    plotinfo = dict(subplot=False)
    plotlines = dict()
