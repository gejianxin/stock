from config.essential import DB, TOKEN, PROXY
from tools.data import get_all_tickers, update_ticker_data


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
    for i in range(643, len(tickers)):
        update_ticker_data(ticker=tickers['ts_code'][i], db=DB, proxy=PROXY, fromdate='2010-01-01')



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