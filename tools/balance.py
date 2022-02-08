#!/usr/bin/python3
import sys
sys.path.append('../')
import argparse
import common.kline as kl
from exchange.exchange_factory import get_exchange_names, create_exchange
from tabulate import tabulate as tb
from datetime import datetime
import pprint

from common import creat_symbol, get_balance_coin, get_balance_free, get_balance_frozen


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='account infomation')
    parser.add_argument('-exchange', required=True, choices=get_exchange_names(), help='exchange name')
    parser.add_argument('-qoutecoin', default='usdt', help='assert sum by qoute coin')
    args = parser.parse_args()
    # print(args)

    exchange = create_exchange(args.exchange)
    if not exchange:
        print("exchange name error!")
        exit(1)
    exchange.connect()

    balances = exchange.get_all_balances()
    print(" %s      %s balances info:" % (datetime.now(), args.exchange) )
    #print(tb(balances))

    qoutecoin = args.qoutecoin
    total_value = 0
    for item in balances:
        amount = max(get_balance_free(item), get_balance_frozen(item))
        if amount < 0:
            continue

        coin = get_balance_coin(item)
        if coin.upper() == qoutecoin.upper():
            value = amount
        else:
            #print(coin)
            symbol = creat_symbol(coin, qoutecoin)
            price = exchange.ticker_price(symbol)
            value = price * amount

        total_value += value
        item['value'] = value

    print(tb(balances))
    print("total: %s  %s" % (total_value, qoutecoin))
