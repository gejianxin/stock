def log(obj, txt, dt=None):
    ''' Logging function for this strategy'''
    dt = dt or obj.datas[0].datetime.date(0)
    print('%s, %s' % (dt.isoformat(), txt))


def order_logger(obj, order):
    if order.status in [order.Completed]:
        if order.isbuy():
            log(obj, '【开仓】  价格： {:6.2f}  数量： {:6d}  总价： {:8.2f}  佣金： {:6.2f}'.format(
                order.executed.price,
                order.size,
                order.executed.value,
                order.executed.comm))
            obj.buyprice = order.executed.price
            obj.buycomm = order.executed.comm
        elif order.issell():
            log(obj, '【平仓】  价格： {:6.2f}  数量： {:6d}  总价： {:8.2f}  佣金： {:6.2f}'.format(
                order.executed.price,
                order.size,
                order.executed.value,
                order.executed.comm))
