#!/usr/bin/python3
import sys
sys.path.append('../')
import argparse
from decimal import *
from exchange.exchange_factory import get_exchange_names, create_exchange
from pprint import pprint
import pandas as pd


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='quary open orders')
    parser.add_argument('-exchange', choices=get_exchange_names(), help='exchange name')
    parser.add_argument('-symbol', required=True, help='symbol, eg: btc_usdt')
    parser.add_argument('-limit', default=1000, help='')
    parser.add_argument('-ignore', nargs='*', default=[], help='key value1 value2 eg: status CANCELED REJECTED')
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
    orders = exchange.get_orders(symbol, limit=args.limit)
    print("%-25s: %s" % ("orders length", len(orders)))
    for o in orders:
        o['datatime'] = exchange.get_time_from_data_ts(o[exchange.Order_Time_Key])
        #o[exchange.Order_Key_CummulativeQuoteQty] = Decimal(o[exchange.Order_Key_CummulativeQuoteQty])
        #o[exchange.Order_Key_ExecutedQty] = float(o[exchange.Order_Key_ExecutedQty])
    #pprint(orders)

    pd.set_option('display.max_rows', None)
    #print(pd.get_option("display.max_columns"))
    pd.set_option('display.max_columns', None)
    orders_df = pd.DataFrame(orders)
    if len(args.ignore)>1:
        orders_df = orders_df.drop(orders_df[orders_df[args.ignore[0]].isin(args.ignore[1:])].index)
    
    print(orders_df)



