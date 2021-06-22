import backtrader as bt


class StampDutyCommissionScheme(bt.CommInfoBase):
    params = dict(
        stamp_duty=0.001,  # 印花税率
        commission=0.02,  # 交易佣金，是百分数xx%，所以设置时必须把原小数乘以100
        stocklike=True,
        commtype=bt.CommInfoBase.COMM_PERC
    )

    def _getcommission(self, size, price, pseudoexec):
        if size > 0:
            return max(size*price*self.params.commission, 5)
        elif size < 0:
            return -size*price*self.params.stamp_duty+max(-size*price*self.params.commission, 5)
        else:
            return 0
