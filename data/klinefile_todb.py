import sys
sys.path.append('../')
import argparse
import json
import time
from datetime import datetime, timedelta
import db.mongodb as md
import common.kline as kl
from exchange.exchange_factory import get_exchange_names, create_exchange
from db.mongodb import get_mongodb
from setup import *
import pandas as pd


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('-source', required=True, choices=get_exchange_names(), help='market data source')
    parser.add_argument('-symbol', required=True, help='symbol: btc_usdt')
    parser.add_argument('-interval', required=True, help='kline types: 1m,4h,1d')
    parser.add_argument('-file', required=True, help='')
    args = parser.parse_args()

    symbol = args.symbol
    interval = args.interval
    if interval == KLINE_INTERVAL_5MINUTE:
        sec = 5*60
    else:
        exit(1)

    exchange = create_exchange(args.source)
    if not exchange:
        print("market data source error!")
        exit(1)
    open_time_key = exchange.kline_key_open_time
    close_time_key = exchange.kline_key_close_time

    kdf = pd.read_csv(args.file)
    print(kdf)

    #kdf[open_time_key] = kdf[open_time_key].apply(lambda x: (int(datetime.timestamp(datetime.strptime(x, '%Y-%m-%d %H:%M:%S')))))
    kdf[open_time_key] = kdf[open_time_key].apply(lambda x: int(x/1000000))
    kdf[close_time_key] = kdf[open_time_key] + sec*1000 - 1
    print('{} ~ {}'.format(exchange.get_time_from_data_ts(kdf.iloc[0][open_time_key]),
                           exchange.get_time_from_data_ts(kdf.iloc[-1][open_time_key])))
    print(kdf)
    del kdf['datetime']

    db_datalines = kdf.to_dict('records')
    
    db = get_mongodb(args.source)
    collection = kl.get_kline_collection(symbol, interval)
    db.ensure_index(collection, [(open_time_key,1)], unique=True)
    db.insert_many(collection, db_datalines)
