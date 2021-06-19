def log(date, txt, dt=None):
    ''' Logging function for this strategy'''
    dt = dt or date[0]
    print('%s, %s' % (dt.isoformat(), txt))


def order_log(order):
    if order.status in [order.Submitted, order.Accepted]:
            # Buy/Sell order submitted/accepted to/by broker - Nothing to do
            return
    # Check if an order has been completed
    # Attention: broker could reject order if not enough cash
    if order.status in [order.Completed]:
        if order.isbuy():
            log(
                '【开仓】  价格： {:.2f}  数量： {:d}  总价： {:.2f}  佣金： {:.2f}'.
                format(
                    order.executed.price,
                    order.size,
                    order.executed.value,
                    order.executed.comm
                    ))
            buyprice = order.executed.price
            buycomm = order.executed.comm
        elif order.issell():
            log(
                '【平仓】  价格： {:.2f}  数量： {:d}  总价： {:.2f}  佣金： {:.2f}'.
                format(
                    order.executed.price,
                    order.size,
                    order.executed.value,
                    order.executed.comm
                    ))
    elif order.status in [order.Canceled, order.Margin, order.Rejected]:
        log('Order Canceled/Margin/Rejected')

    order = None

