def log(obj, txt, dt=None):
    ''' Logging function for this strategy'''
    dt = dt or obj.datas[0].datetime.date(0)
    print('%s, %s' % (dt.isoformat(), txt))


def order_logger(func):
    def wrapper(*args, **kwargs):
        if args[1].status in [args[1].Completed]:
            if args[1].isbuy():
                log(args[0], '【开仓】  价格： {:6.2f}  数量： {:6d}  总价： {:8.2f}  佣金： {:6.2f}'.format(
                    args[1].executed.price,
                    args[1].size,
                    args[1].executed.value,
                    args[1].executed.comm))
                args[0].buyprice = args[1].executed.price
                args[0].buycomm = args[1].executed.comm
            elif args[1].issell():
                log(args[0], '【平仓】  价格： {:6.2f}  数量： {:6d}  总价： {:8.2f}  佣金： {:6.2f}'.format(
                    args[1].executed.price,
                    args[1].size,
                    args[1].executed.value,
                    args[1].executed.comm))
        return func(*args, **kwargs)
    return wrapper
