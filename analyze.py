import math
import numpy as np
import talib


# 滑动窗口切分列表alist，按照宽度width，步长step切分
# 功能等于基于numpy的rolling()函数
def strided_app(origin_array: np.ndarray,
                window: int = 252, step=1) -> np.ndarray:
    if origin_array.size > window:
        nrows = ((origin_array.size - window) // step) + 1
    else:
        return origin_array
    n = origin_array.strides[0]
    return np.lib.stride_tricks.as_strided(origin_array,
                                           shape=(nrows, window),
                                           strides=(step * n, n))


def rolling_poly9(origin_array: np.ndarray, window: int = 252) -> np.ndarray:
    '''
    一次九项式滚动分解拟合
    '''
    index = range(window)

    def last_poly9(array_input):
        fit_params = np.polynomial.Chebyshev.fit(index, array_input, 9)
        return fit_params(index)[-1]

    if (len(origin_array) > window):
        stride_matrix = strided_app(origin_array, window, 1)
        # numpy.r_[]按照行方向拼接array，list是列向量形式存储，故仅能拼接array
        # numpy.c_[]按照列方向拼接array
        # np.full()填充ndarray
        return np.r_[np.full(window - 1, np.nan),
                     np.array(list(map(last_poly9, stride_matrix)))]
    else:
        index = range(len(origin_array))
        fit_params = np.polynomial.Chebyshev.fit(index, origin_array, 9)
        y_fit_n = fit_params(index)
        return y_fit_n


def poly9(array2fit: np.ndarray, window: int = 252, n: int = 10):
    hma_array = hma(array2fit, n)
    count = len(hma_array)
    hma_array = hma_array[~np.isnan(hma_array)]
    count = count - len(hma_array)
    poly9 = rolling_poly9(hma_array, window)
    return np.append(np.full((1, count), np.nan), poly9)


def hma(array2hma: np.ndarray, n: int = 10):
    return talib.WMA(2*talib.WMA(array2hma, int(n/2)) - talib.WMA(array2hma, n), int(math.sqrt(n)))
