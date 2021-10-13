#!/usr/bin/python3
import sys
sys.path.append('../')
import argparse
from common import SIDE_BUY, SIDE_SELL
from common.order import ORDER_TYPE_LIMIT
from exchange.exchange_factory import get_exchange_names, create_exchange
import pprint


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='limit new order')
    parser.add_argument('-exchange', choices=get_exchange_names(), help='')
    parser.add_argument('-symbol', required=True, help='eg: btc_usdt')
    parser.add_argument('-side', choices=[SIDE_BUY, SIDE_SELL], help='')
    parser.add_argument('-price', required=True, type=float, help='price')
    parser.add_argument('-qty', required=True, type=float, help='quantity')
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

    order_id = exchange.new_order(
        side=args.side,
        type=ORDER_TYPE_LIMIT,
        symbol=args.symbol,
        price=args.price,
        qty=args.qty)
    print(order_id)

