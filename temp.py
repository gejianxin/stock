from _typeshed import StrOrBytesPath
import numpy as np
import talib


# 把原始数组按照滑动窗口大小依次截取，并拼接
# 例如：原始数组为[1,2,3,4,5,6,7,8,9,10]
# 滑动窗口大小为5
# 则顺序取窗口大小数组[1,2,3,4,5]，向后滑动一个窗口得到[2,3,4,5,6]
# 纵向拼接得到array([[1,2,3,4,5],[2,3,4,5,6]])
# 其余同理
def slip_window_concat_array(origin_array: np.array, window: int = 252, step: int = 1):
    new_array = origin_array[0:window]
    for i in range(step, len(origin_array)-window, step):
        slip_array = origin_array[i:i+window]
        new_array = np.vstack((new_array, slip_array))
    return new_array

# Test Code
# a = np.array([1,2,3,4,5,6,7,8,9,10])
# new_array=slip_window_concat_array(a)
# new_array

# Output
# array([[1, 2, 3, 4, 5],
#        [2, 3, 4, 5, 6],
#        [3, 4, 5, 6, 7],
#        [4, 5, 6, 7, 8],
#        [5, 6, 7, 8, 9]])


def last_poly(x, y, poly=9):
    fit_params = np.polynomial.Chebyshev.fit(x, y, 9)
    return fit_params(x)[-1]


def rolling_poly(origin_array: np.array, window: int = 252, poly: int = 9) -> np.ndarray:
    '''
    一次九项式滚动分解拟合
    '''
    index = range(window)

    if (len(origin_array) > window):
        # stride_matrix = strided_app(origin_array, window, 1)
        # # numpy.r_[]按照行方向拼接array，list是列向量形式存储，故仅能拼接array
        # # numpy.c_[]按照列方向拼接array
        # # numpy.full()填充ndarray
        # return np.r_[np.full(window, np.nan),
        #              np.array(list(map(last_poly9, slip_window_concat_array(origin_array, window))))]
        new_array = slip_window_concat_array(origin_array, window)
        nrow = np.size(new_array, axis=0)
        ncol = np.size(new_array, axis=1)
        result = []
        for i in range(nrow):
            fit_params = last_poly(range(ncol), new_array[i, :])
            result.append(fit_params(range(ncol)[-1]))
            print(result)
        return np.r_[np.full(window, np.nan),
                     np.array(list(map(last_poly, index, slip_window_concat_array(origin_array, window))))]

    else:
        index = range(len(origin_array))
        fit_params = np.polynomial.Chebyshev.fit(index, origin_array, poly)
        y_fit_n = fit_params(index)
        return y_fit_n
