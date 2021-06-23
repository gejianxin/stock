import backtrader as bt


class StampDutyCommissionScheme(bt.CommInfoBase):
    params = dict(
        stamp_duty=0.001,  # 印花税率
        commission=0.0002,  # 交易佣金
        stocklike=True,
        commtype=bt.CommInfoBase.COMM_PERC
    )

    def _getcommission(self, size, price, pseudoexec):
        if size > 0:
            return max(size*price*self.params.commission*100, 5)
        elif size < 0:
            # 在_getcommission中得到的commission是params参数中的值除以100
            return -size*price*(self.params.stamp_duty+self.params.commission*100)
        else:
            return 0
