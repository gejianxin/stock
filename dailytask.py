# import math
# import requests
# from requests.exceptions import Timeout, ProxyError
# from config.essential import DB, TOKEN, PROXY, BASEURL, URL
# from tools.data import get_all_tickers, update_ticker_data
# from tools.proxy import get_proxy
from datetime import datetime as dt
import pandas as pd
from config.essential import DB, TOKEN
from tools.data_baostock import get_all_tickers, update_db_data, get_db_data
from tools.algrorithm import thresholding_algo, ma_power


# docker run command
# docker run -it -e POSTGRES_PASSWORD=123456 -v /d/project/data:/var/lib/postgresql/data -p 5432:5432 --name db postgres:latest bash
# chown postgres:postgres /var/lib/postgresql/data
# initdb /var/lib/postgresql/data
# docker start db
# docker attach db
# 后台启动pg server
# pg_ctl -D /var/lib/postgresql/data -l /var/lib/postgresql/data/logfile start


if __name__ == '__main__':
    tickers = get_all_tickers(token=TOKEN)
    for i in range(len(tickers)):
        update_db_data(ticker=tickers['code'][i], db=DB, fromdate='2010-01-01')

    for ticker in tickers:
        records = get_db_data(ticker=ticker, db=DB, fromdate='2018-01-01', todate=dt.today().date())
        df = pd.DataFrame(data=records)
        df.columns = ['date', 'open', 'high', 'low', 'close', 'adjust close', 'volume']
        df = df[['date', 'open', 'high', 'low', 'close', 'volume']]
        df['date'] = pd.to_datetime(df['date'], format='%Y-%m-%d')
        # df['date'] = df['date'].data()
        # df['openinterest'] = 0
        df.set_index(keys='date', inplace=True)
        fit = thresholding_algo(df['close'], lag=5, threshold=3.5, influence=0.5)
        print(fit)

    



    # 1. 获取所有股票名称
    # tickers = get_all_tickers(token=TOKEN)
    # 2. 获取代理列表
    # proxies = get_proxy(BASEURL, URL, proxies=[])
    # 3. 验证代理有效性
    # for proxy in proxies:
    #     try:
    #         response = requests.get('https://finance.yahoo.com/', timeout=5, proxies=dict(https=proxy))
    #         if response.status_code != 200:
    #             proxies.remove(proxy)
    #     except Timeout as error:
    #         proxies.remove(proxy)
    #         print(proxy, ' timeout')
    #     except ProxyError as error:
    #         proxies.remove(proxy)
    #         print(proxy, ' error')
    # 4. 股票分组，使用对应代理下载，避免过多爬取数据被封
    # step = math.ceil(len(tickers)/len(proxies))
    # for proxy in proxies:
    #     i,j = 0,0
    #     while j >= i*step and j <= (i+1)*step and j < len(tickers):
    #         update_ticker_data(ticker=tickers['ts_code'][j], db=DB, proxy=proxy, fromdate='2010-01-01')
    #         j += 1



# PROCEDURE DELETE ALL POSTGRESQL TABLES
# DO $$
#   DECLARE
#     r RECORD;
# BEGIN
#   FOR r IN
#     (
#       SELECT table_name
#       FROM information_schema.tables
#       WHERE table_schema=current_schema()
#     )
#   LOOP
#      EXECUTE 'DROP TABLE IF EXISTS ' || quote_ident(r.table_name) || ' CASCADE';
#   END LOOP;
# END $$ ;
