#!/usr/bin/python3
import sys
sys.path.append('../')
import argparse
from exchange.exchange_factory import get_exchange_names, create_exchange
from common import SIDE_BUY, SIDE_SELL


def calc_slippage_by_side(book, side, amount):
    if side == SIDE_BUY:
        orders = book['asks']
    else:
        orders = book['bids']

    deal = 0
    cost = 0
    for order in orders:
        order_amount = float(order[1])
        order_price = float(order[0])
        if amount - deal > order_amount:
            deal += order_amount
            cost += order_amount * order_price
        else:
            cost += (amount - deal) * order_price
            deal = amount
            break

    if deal < amount:
        print("The order book depth is not enough.(%5s: %20s) Please get more orders"%(side, deal))
        return None, None, None
    average_price = cost / amount
    if side == SIDE_BUY:
        slippage = (average_price - cur_price) * 100 / cur_price
    else:
        slippage = (cur_price - average_price) * 100 / cur_price
    return average_price, cost, slippage


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Slippage Calculation')
    parser.add_argument('-exchange', choices=get_exchange_names(), help='exchange name')
    parser.add_argument('-symbol', required=True, help='symbol, eg: btc_usdt')
    #parser.add_argument('-side', required=True, choices=[SIDE_BUY, SIDE_SELL], help='side')
    parser.add_argument('-amount', type=float, required=True, help='amount')

    args = parser.parse_args()
    # print(args)

    symbol = args.symbol
    #side = args.side
    amount = args.amount

    exchange = create_exchange(args.exchange)
    if not exchange:
        print("exchange name error!")
        exit(1)
    exchange.connect()

    exchange.ping()
    print(exchange.time())

    cur_price = exchange.ticker_price(symbol)
    depth_limit = 1000
    book = exchange.depth(symbol, depth_limit)
    # print(book)
    print("Current price: %s  depth limit: %s" % (cur_price, depth_limit))

    buy_average_price, buy_cost, buy_slippage = calc_slippage_by_side(book, SIDE_BUY, amount)
    sell_average_price, sell_cost, sell_slippage = calc_slippage_by_side(book, SIDE_SELL, amount)
    sl_str = '-'*75
    print(sl_str)
    sl_fmt = '%20s:  %25s  %25s'
    print(sl_fmt % ('Side', SIDE_BUY, SIDE_SELL))
    print(sl_fmt % ('Average deal price', buy_average_price, sell_average_price))
    print(sl_fmt % ('Total cost', buy_cost, sell_cost))
    print(sl_fmt % ('Slippage(%)', buy_slippage, sell_slippage))
    print(sl_str)

