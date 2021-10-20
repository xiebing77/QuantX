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
    parser.add_argument('-orderId',required=True, help='order id')
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
    order = exchange.get_order(symbol,args.orderId)
    print(order)


