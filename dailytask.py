import math
import requests
from requests.exceptions import Timeout, ProxyError
from config.essential import DB, TOKEN, PROXY, BASEURL, URL
from tools.data import get_all_tickers, update_ticker_data
from tools.proxy import get_proxy


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
    proxies = get_proxy(BASEURL, URL, proxies=[])
    # Test proxy validity
    for proxy in proxies:
        try:
            response = requests.get('https://finance.yahoo.com/', timeout=5, proxies=dict(https=proxy))
            if response.status_code != 200:
                proxies.remove(proxy)
        except Timeout as error:
            proxies.remove(proxy)
            print(proxy, ' timeout')
        except ProxyError as error:
            proxies.remove(proxy)
            print(proxy, ' error')
    print(proxies)
    step = math.ceil(len(tickers)/len(proxies))
    for proxy in proxies:
        i,j = 0,0
        while j >= i*step and j <= (i+1)*step and j < len(tickers):
            update_ticker_data(ticker=tickers['ts_code'][j], db=DB, proxy=proxy, fromdate='2010-01-01')
            j += 1



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