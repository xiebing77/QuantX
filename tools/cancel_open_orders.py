#!/usr/bin/python3
import sys
sys.path.append('../')
import argparse
from common import SIDE_BUY, SIDE_SELL
from common import ORDER_TYPE_MARKET
from exchange.exchange_factory import get_exchange_names, create_exchange
import pprint


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='cancel open orders')
    parser.add_argument('-exchange', choices=get_exchange_names(), help='')
    parser.add_argument('-symbol', required=True, help='eg: btc_usdt')
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

    exchange.cancel_open_orders(symbol=args.symbol)

