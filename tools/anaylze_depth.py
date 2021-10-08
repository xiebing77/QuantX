#!/usr/bin/python3
import sys
sys.path.append('../')
import argparse
from exchange.exchange_factory import get_exchange_names, create_exchange
from common import SIDE_BUY, SIDE_SELL
from tools.slippage import calc_average_price, diff_price
from pprint import pprint

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

    depth_limit = exchange.depth_limits[-1]
    book = exchange.depth(symbol, depth_limit)
    #pprint(book)
    maker_asks = book['asks']
    maker_bids = book['bids']
    print('depth limit: %s,  sell: %s,  buy: %s' % (
        depth_limit, len(maker_asks), len(maker_bids)))

    # Handicap spread
    sell1_price = float(maker_asks[0][0])
    buy1_price = float(maker_bids[0][0])
    print('sell1 price: %s, buy1 price: %s' % (sell1_price, buy1_price))
    spread = handicap_spread(sell1_price, buy1_price, ticker_price)
    print('Handicap spread: %.8f%%' % (spread*100))

    #slippage
    #print('  slippage  '.ljust(80, '~'))
    maker_asks_total_qty = calc_total_qty(maker_asks)
    maker_bids_total_qty = calc_total_qty(maker_bids)
    qtys = []
    qty = 1
    while qty < min(maker_bids_total_qty, maker_asks_total_qty):
        qtys.append(qty)
        qty *= 10
    qtys += [min(maker_bids_total_qty, maker_asks_total_qty), max(maker_bids_total_qty, maker_asks_total_qty)]
    #print(qtys)

    slippage_fmt = '12.4f'
    det_fmt = '14.4f'
    print('%20s | %s | %s' % ('', ' buy (take asks) '.center(93, '-'), ' sell (take bids) '.center(93, '-')))
    t_fmt = '%20s | %12s  %20s %20s %20s(%14s)  | %12s  %20s %20s %20s(%14s)'
    print(t_fmt % ('qty', 'slippage(%)', 'cost', 'avg price', 'edge price', 'diff ticker(%)',
        'slippage(%)', 'cost', 'avg price', 'edge price', 'diff ticker(%)'))
    for qty in qtys:
        taker_buy_avg_price, taker_buy_cost, taker_buy_edge_price = calc_average_price(maker_asks, qty)
        taker_sell_avg_price, taker_sell_cost, taker_sell_edge_price = calc_average_price(maker_bids, qty)
        taker_buy_slippage = diff_price(taker_buy_avg_price, ticker_price)
        taker_sell_slippage = diff_price(taker_sell_avg_price, ticker_price)
        taker_buy_diff_et = diff_price(taker_buy_edge_price, ticker_price)
        taker_sell_diff_et = diff_price(taker_sell_edge_price, ticker_price)
        print(t_fmt % (qty,
            format_float(slippage_fmt, taker_buy_slippage),
            taker_buy_cost,
            taker_buy_avg_price,
            taker_buy_edge_price,
            format_float(det_fmt, taker_buy_diff_et),
            format_float(slippage_fmt, taker_sell_slippage),
            taker_sell_cost,
            taker_sell_avg_price,
            taker_sell_edge_price,
            format_float(det_fmt, taker_sell_diff_et)
            )
        )

