#!/usr/bin/python3
import sys
sys.path.append('../')
import argparse
from common import SIDE_BUY, SIDE_SELL
from order import ORDER_TYPE_MARKET
from exchange.exchange_factory import get_exchange_names, create_exchange
import pprint


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='cancel order')
    parser.add_argument('-exchange', choices=get_exchange_names(), help='')
    parser.add_argument('-symbol', required=True, help='eg: btc_usdt')
    parser.add_argument('-orderId', required=True, help='')
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

    exchange.cancel_order(
        symbol=args.symbol,
        order_id=args.orderId)

