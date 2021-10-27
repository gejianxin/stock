import backtrader as bt

class ExtendDataframe(bt.feeds.PandasData):
    lines = ('adjust',) # 增加 adjust 线
    params = (
        ('adjust', 6), # 默认第 8 列
    )