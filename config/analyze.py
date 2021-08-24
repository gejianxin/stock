import math
import numpy as np
import talib


# 把原始数组按照滑动窗口大小依次截取，并拼接
# 例如：原始数组为[1,2,3,4,5,6,7,8,9,10]
# 滑动窗口大小为5
# 则顺序取窗口大小数组[1,2,3,4,5]，向后滑动一个窗口得到[2,3,4,5,6]
# 纵向拼接得到array([[1,2,3,4,5],[2,3,4,5,6]])
# 其余同理

# slip_window_concat_array功能等于strided_app，不知道效率是否后者更高

# def slip_window_concat_array(origin_array: np.array, window: int = 252, step: int = 1):
#     new_array = origin_array[0:window]
#     for i in range(step, len(origin_array)-window, step):
#         slip_array = origin_array[i:i+window]
#         new_array = np.vstack((new_array, slip_array))
#     return new_array

# =======Test Code Start=======
# a = np.array([1,2,3,4,5,6,7,8,9,10])
# new_array=slip_window_concat_array(a)
# new_array

# Output
# array([[1, 2, 3, 4, 5],
#        [2, 3, 4, 5, 6],
#        [3, 4, 5, 6, 7],
#        [4, 5, 6, 7, 8],
#        [5, 6, 7, 8, 9]])
# =======Test Code End=======

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
        # .full()填充ndarray
        return np.r_[np.full(window - 1, np.nan),
                     np.array(list(map(last_poly9, stride_matrix)))]
    else:
        index = range(len(origin_array))
        fit_params = np.polynomial.Chebyshev.fit(index, origin_array, 9)
        y_fit_n = fit_params(index)
        return y_fit_n


def hma(array2hma: np.array, n: int = 10):
    return talib.WMA(2*talib.WMA(array2hma, int(n/2)) - talib.WMA(array2hma, n), int(math.sqrt(n)))


# =======Test Code Start=======
# df = pd.read_csv('data.csv', parse_dates=True, index_col=0)
# df['HMA10'] = hma(df['Close'].values)

# 读取HMA10列中所有非NAN项，拟合时必须剔除NAN项
# new_array = df['HMA10'][~np.isnan(df['HMA10'])]

# 因为计算POLYNOMIAL9剔除了HMA10中的NAN项，所以结果长度与剔除NAN项的HMA10等长
# 要在DataFrame中增加POLYNOMIAL9列，则必须把结果长度补齐
# np.full(len(df)-len(new_array),np.nan)用np.nan生成数组，用于补齐列
# df['POLYNOMIAL9'] = np.r_[np.full(len(df)-len(new_array), np.nan), rolling_poly9(df['HMA10'][~np.isnan(df['HMA10'])].values,252)]
# print(df)
# =======Test Code End=======
