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
    parser.add_argument('-interval', required=True, help='kline types: 1m, 5m, 1h, 1d')
    parser.add_argument('-files', required=True, nargs='*', help='')
    args = parser.parse_args()

    exchange = create_exchange(args.source)
    if not exchange:
        print("market data source error!")
        exit(1)

    open_time_key = exchange.kline_key_open_time
    for f in args.files:
        print('handle file: ', f)
        cost_start = datetime.now()
        df = pd.read_csv(f)
        print('  cost: %s'%(datetime.now()-cost_start))

        open_times = df[open_time_key]
        open_time_0 = exchange.get_time_from_data_ts(open_times[0])
        open_time_1 = exchange.get_time_from_data_ts(open_times[1])
        interval_td = kl.get_interval_timedelta(args.interval)
        if not interval_td:
            print('interval {} not support'.format(args.interval))
        if open_time_1 - open_time_0 != interval_td:
            print('open time error! {} {}'.format(open_time_0, open_time_1))
            exit(1)

        print(df)
        db_datalines = df.to_dict('records')

        db = get_mongodb(args.source)
        collection = kl.get_kline_collection(args.symbol, args.interval)
        db.create_index(collection, [(open_time_key,1)])
        db.insert_many(collection, db_datalines)

