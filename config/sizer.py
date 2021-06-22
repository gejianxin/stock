import backtrader as bt
import math


class MaxRiskSizer(bt.Sizer):
    '''
    Returns the number of shares rounded down that can be purchased for the
    max rish tolerance
    '''
    params = dict(
        risk=1,
        )

    def __init__(self):
        if self.params.risk > 1 or self.params.risk < 0:
            raise ValueError('The risk parameter is a percentage which must be entered as a float. e.g. 0.5')

    def _getsizing(self, comminfo, cash, data, isbuy):
        if isbuy:
            self.params.stake = math.floor(cash / ((1+comminfo.params.commission+comminfo.params.stamp_duty)*100*data[0])) * 100
        return self.params.stake
