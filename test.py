# import numpy as np
import pandas as pd
import analyze


f = 'C:\\Users\\User\\Documents\\data\\sh600000.csv'
df = pd.read_csv(f, index_col=0, parse_dates=True)

hma_array = analyze.hma(df['close'].values, 10)
analyze.calculate(hma_array, 252)
