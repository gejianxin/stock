import backtrader as bt


class KDJ(bt.Indicator):
    lines = ('K', 'D', 'J')

    params = (
        ('period', 9),
        ('period_dfast', 3),
        ('period_dslow', 3),
    )

    def __init__(self):
        # Add a KDJ indicator
        self.kd = bt.indicators.StochasticFull(
            self.data,
            period=self.params.period,
            period_dfast=self.params.period_dfast,
            period_dslow=self.params.period_dslow,
        )

        self.lines.K = self.kd.percD
        self.lines.D = self.kd.percDSlow
        self.lines.J = self.K * 3 - self.D * 2
