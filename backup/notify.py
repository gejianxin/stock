# def log(self, txt, dt=None):
#     ''' Logging function for this strategy'''
#     dt = dt or self.datas[0].datetime.date(0)
#     print(dt)
#     print('%s, %s' % (dt.isoformat(), txt))


def order_log(date, order):
    if order.status in [order.Submitted, order.Accepted]:
        # Buy/Sell order submitted/accepted to/by broker - Nothing to do
        return
    # Check if an order has been completed
    # Attention: broker could reject order if not enough cash
    if order.status in [order.Completed]:
        if order.isbuy():
            print(date, '||', '【开仓】  价格： {:.2f}  数量： {:d}  总价： {:.2f}  佣金： {:.2f}'.format(
                    order.executed.price,
                    order.size,
                    order.executed.value,
                    order.executed.comm
                    ))
            # buyprice = order.executed.price
            # buycomm = order.executed.comm
        elif order.issell():
            print(date, '||', '【平仓】  价格： {:.2f}  数量： {:d}  总价： {:.2f}  佣金： {:.2f}'.format(
                    order.executed.price,
                    order.size,
                    order.executed.value,
                    order.executed.comm
                    ))
    elif order.status in [order.Canceled, order.Margin, order.Rejected]:
        print(date, '||', 'Order Canceled/Margin/Rejected')

    order = None


def trade_log(date, trade):
    if not trade.isclosed:
        pass
    else:
        print(date, '||', '【单笔交易盈利】  毛利： {:.2f}  净利： {:.2f}'.format(
            trade.pnl, trade.pnlcomm))
