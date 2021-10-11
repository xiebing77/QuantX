#!/usr/bin/python3
import sys
sys.path.append('../')
import argparse
from exchange.exchange_factory import get_exchange_names, create_exchange
import pprint
import pandas as pd


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='quary open orders')
    parser.add_argument('-exchange', choices=get_exchange_names(), help='exchange name')
    parser.add_argument('-symbol', required=True, help='symbol, eg: btc_usdt')
    parser.add_argument('-limit', default=100, help='')
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
    orders = exchange.get_orders(symbol, args.limit)

    b_prec, q_prec = exchange.get_assetPrecision(symbol)
    print(b_prec)
    for order in orders:
        order[exchange.Order_Key_OrigQty] = round(float(order[exchange.Order_Key_OrigQty]), b_prec)
        order[exchange.Order_Key_ExecutedQty] = round(float(order[exchange.Order_Key_ExecutedQty]), b_prec)

        order[exchange.Order_Key_Price] = round(float(order[exchange.Order_Key_Price]), q_prec)

    print("%-25s: %s" % ("all orders length", len(orders)) )
    pprint.pprint(orders)

    #orders_df = pd.DataFrame(orders)
    #print(orders_df)



