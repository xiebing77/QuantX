#!/usr/bin/python3
import sys
sys.path.append('../')
import argparse
from exchange.exchange_factory import get_exchange_names, create_exchange
from common import SIDE_BUY, SIDE_SELL
from tools.slippage import calc_average_price, diff_price


def format_float(fmt, f):
    return format(f, fmt) if f else None

def calc_total_qty(orders):
    total_qty = 0
    for order in orders:
        order_qty = float(order[1])
        order_price = float(order[0])
        total_qty += order_qty
    return total_qty

def handicap_spread(sell1_price, buy1_price, ticker_price):
    return (sell1_price - buy1_price) / ticker_price

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='analyze depth')
    parser.add_argument('-exchange', choices=get_exchange_names(), help='exchange name')
    parser.add_argument('-symbol', required=True, help='symbol, eg: btc_usdt')

    args = parser.parse_args()
    # print(args)
    symbol = args.symbol

    exchange = create_exchange(args.exchange)
    if not exchange:
        print("exchange name error!")
        exit(1)
    exchange.connect()
    exchange.ping()
    print(exchange.time())

    ticker_price = exchange.ticker_price(symbol)
    print("ticker price: %s" % (ticker_price))

    book = exchange.depth(symbol)
    # print(book)
    sell_orders = book['asks']
    buy_orders = book['bids']

    # Handicap spread
    sell1_order = sell_orders[0]
    buy1_order = buy_orders[0]

    sell1_price = float(sell1_order[0])
    buy1_price = float(buy1_order[0])
    print('sell1 price: %s, buy1 price: %s' % (sell1_price, buy1_price))
    spread = handicap_spread(sell1_price, buy1_price, ticker_price)
    print('Handicap spread: %.8f%%' % (spread*100))

    #slippage
    #print('  slippage  '.ljust(80, '~'))
    depth_sell_qty = calc_total_qty(sell_orders)
    depth_buy_qty = calc_total_qty(buy_orders)
    qtys = []
    qty = 1
    while qty < min(depth_buy_qty, depth_sell_qty):
        qtys.append(qty)
        qty *= 10
    qtys += [min(depth_buy_qty, depth_sell_qty), max(depth_buy_qty, depth_sell_qty)]
    #print(qtys)

    slippage_fmt = '12.4f'
    det_fmt = '14.4f'
    print('%20s | %s | %s' % ('', SIDE_BUY.center(93, '-'), SIDE_SELL.center(93, '-')))
    t_fmt = '%20s | %12s  %20s %20s %20s(%14s)  | %12s  %20s %20s %20s(%14s)'
    print(t_fmt % ('qty', 'slippage(%)', 'cost', 'avg price', 'edge price', 'diff ticker(%)',
        'slippage(%)', 'cost', 'avg price', 'edge price', 'diff ticker(%)'))
    for qty in qtys:
        buy_avg_price, buy_cost, buy_edge_price = calc_average_price(book, SIDE_BUY, qty)
        sell_avg_price, sell_cost, sell_edge_price = calc_average_price(book, SIDE_SELL, qty)
        buy_slippage = diff_price(buy_avg_price, ticker_price)
        sell_slippage = diff_price(sell_avg_price, ticker_price)
        buy_diff_et = diff_price(buy_edge_price, ticker_price)
        sell_diff_et = diff_price(sell_edge_price, ticker_price)
        print(t_fmt % (qty,
            format_float(slippage_fmt, buy_slippage),
            buy_cost,
            buy_avg_price,
            buy_edge_price,
            format_float(det_fmt, buy_diff_et),
            format_float(slippage_fmt, sell_slippage),
            sell_cost,
            sell_avg_price,
            sell_edge_price,
            format_float(det_fmt, sell_diff_et)
            )
        )

