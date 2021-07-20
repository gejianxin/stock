import numpy as np
import numba as nb
import backtrader as bt
import talib


@nb.jit(nopython=True)
def thresholding_algo(y, lag, threshold, influence):
    """
    Robust peak detection algorithm (using z-scores)
    自带鲁棒性极值点识别，利用方差和ZSCORE进行时间序列极值检测。算法源自：
    https://stackoverflow.com/questions/22583391/
    本实现使用Numba JIT优化，比原版（上面）大约快了500倍。
    """
    signals = np.zeros((3, len(y),))  # 生成3行、len(y)列的全0二维数组
    idx_signals = 0
    idx_avgFilter = 1
    idx_stdFilter = 2

    filteredY = np.copy(y)
    # signals二维数组的第一行全0
    signals[idx_avgFilter, lag-1] = np.mean(y[0:lag])  # signals二维数组第二行首个非0元素计算公式
    signals[idx_stdFilter, lag-1] = np.std(y[0:lag])  # signals二维数组第三行首个非0元素计算公式
    for i in range(lag, len(y)):
        # 把y当前元素与signals第二行前一个元素的差与阈值threshold乘以signals第三行前一个元素的积进行比较
        if abs(y[i] - signals[idx_avgFilter, i-1]) > threshold * signals[idx_stdFilter, i-1]:
            if y[i] > signals[idx_avgFilter, i-1]:
                signals[idx_signals, i] = 1
            else:
                signals[idx_signals, i] = -1

            # filteredY从0~lag-1等于y[0:lag]，从filteredY[lag]开始
            # 当前元素值等于影响因子influence和y当前位置元素乘积
            # 并加上1-influence乘以filteredY前一位置元素
            filteredY[i] = influence * y[i] + (1-influence) * filteredY[i-1]
            # signals第二行第i+1个元素等于filteredY前lag个元素的均值
            signals[idx_avgFilter, i] = np.mean(filteredY[(i-lag):i])
            # signals第三行第i+1个元素等于filteredY前lag个元素的均值
            signals[idx_stdFilter, i] = np.std(filteredY[(i-lag):i])
        else:
            signals[idx_signals, i] = 0
            filteredY[i] = y[i]
            signals[idx_avgFilter, i] = np.mean(filteredY[(i-lag):i])
            signals[idx_stdFilter, i] = np.std(filteredY[(i-lag):i])

    return signals


def ma_power(data, range_list=range(5, 30)):
    def inverse_num(series):
        # 计算逆序
        count = 0
        for i in range(len(series)):
            value = series[i]
            for j in range(i):
                if value < series[j]:
                    count += 1
        return count

    # 准备收盘价，初始化ma多维数组
    ma_np = np.empty((len(data), len(range_list)))
    ma_count = 0

    # 列向量对应MA5-MA30
    for r in range_list:
        ma = talib.EMA(data, r)
        ma_np[:, ma_count] = ma
        ma_count += 1

    ma_max = max(range_list)
    len_range_list = len(range_list)
    num = np.zeros(len(data))
    ratio = np.zeros(len(data))
    with np.errstate(invalid='ignore', divide='ignore'):
        for i in range(ma_max, len(data)):
            num[i] = inverse_num(ma_np[i, :])
            ratio[i] = num[i] / (len_range_list * (len_range_list - 1)) * 2
    print(ratio)
    return ratio


class Peak(bt.Indicator):
    lines = ('algo','power')
    params = dict(
        lag=5,
        threshold=3.5,
        influence=0.5,
        )

    def __init__(self):
        # self.addminperiod(self.params.lag)
        self.lines.algo = thresholding_algo(
            y=np.array(self.datas[0].close),
            lag=self.params.lag,
            threshold=self.params.threshold,
            influence=self.params.influence
            )[0,:]
        self.lines.power = ma_power(self.datas[0].close)