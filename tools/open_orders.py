#!/usr/bin/python3
import sys
sys.path.append('../')
import argparse
from exchange.exchange_factory import get_exchange_names, create_exchange
import pprint
import numpy as np
import pandas as pd


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='quary open orders')
    parser.add_argument('-exchange', choices=get_exchange_names(), help='exchange name')
    parser.add_argument('-symbol', required=True, help='symbol, eg: btc_usdt')
    args = parser.parse_args()
    # print(args)
    if not (args.exchange):
        parser.print_help()
        exit(1)

    exchange = create_exchange(args.exchange)
    if not exchange:
        print("exchange name error!")
        exit(1)
    exchange.connect()

    symbol = args.symbol
    open_orders = exchange.get_open_orders(symbol)
    print("%-25s: %s" % ("open orders length", len(open_orders)) )
    for o in open_orders:
        o['datatime'] = exchange.get_time_from_data_ts(o[exchange.Order_Time_Key])
    #pprint.pprint(open_orders)

    pd.set_option('display.max_rows', None)
    open_orders_df = pd.DataFrame(open_orders)
    open_orders_df.replace(to_replace=r'^\s*$', value=np.nan, regex=True, inplace=True)
    open_orders_df = open_orders_df.dropna(axis=1, how='all')
    print(open_orders_df)

