#!/usr/bin/python3
import sys
sys.path.append('../')
import argparse
from exchange.exchange_factory import get_exchange_names, create_exchange
from common import SIDE_BUY, SIDE_SELL


def diff_price(price, ticker_price):
    if not price:
        return None
    return abs(price - ticker_price) * 100 / ticker_price


def calc_average_price(book, side, qty):
    if side == SIDE_BUY:
        orders = book['asks']
    else:
        orders = book['bids']

    deal = 0
    cost = 0
    for order in orders:
        order_qty = float(order[1])
        order_price = float(order[0])
        if qty - deal >= order_qty:
            deal += order_qty
            cost += order_qty * order_price
        else:
            cost += (qty - deal) * order_price
            deal = qty
            break

    if deal < qty:
        #print("The order book depth is not enough.(%5s: %20s) Please get more orders"%(side, deal))
        return None, None, None
    average_price = cost / qty
    return average_price, cost, order_price


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Slippage Calculation')
    parser.add_argument('-exchange', choices=get_exchange_names(), help='exchange name')
    parser.add_argument('-symbol', required=True, help='symbol, eg: btc_usdt')
    #parser.add_argument('-side', required=True, choices=[SIDE_BUY, SIDE_SELL], help='side')
    parser.add_argument('-qty', type=float, required=True, help='qty')

    args = parser.parse_args()
    # print(args)

    symbol = args.symbol
    #side = args.side
    qty = args.qty

    exchange = create_exchange(args.exchange)
    if not exchange:
        print("exchange name error!")
        exit(1)
    exchange.connect()

    exchange.ping()
    print(exchange.time())

    ticker_price = exchange.ticker_price(symbol)
    book = exchange.depth(symbol)
    # print(book)
    print("ticker price: %s" % (ticker_price))

    buy_average_price, buy_cost, buy_edge_price = calc_average_price(book, SIDE_BUY, qty)
    sell_average_price, sell_cost, sell_edge_price = calc_average_price(book, SIDE_SELL, qty)
    sl_str = '-'*75
    print(sl_str)
    sl_fmt = '%20s:  %25s  %25s'
    print(sl_fmt % ('Side', SIDE_BUY, SIDE_SELL))
    print(sl_fmt % ('Average deal price', buy_average_price, sell_average_price))
    print(sl_fmt % ('Total cost', buy_cost, sell_cost))
    print(sl_fmt % ('Slippage(%)', diff_price(buy_average_price, ticker_price),
        diff_price(sell_average_price, ticker_price)))
    print(sl_str)

