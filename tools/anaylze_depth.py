#!/usr/bin/python3
import sys
sys.path.append('../')
import argparse
from exchange.exchange_factory import get_exchange_names, create_exchange
from common import SIDE_BUY, SIDE_SELL
from tools.slippage import calc_average_price, diff_price, format_percent, calc_total_qty
from pprint import pprint


def calc_qty_by_diff(orders, ticker_price, diff_rate):
    qty = 0
    for order in orders:
        order_qty = float(order[1])
        order_price = float(order[0])
        if diff_price(order_price, ticker_price) > diff_rate:
            break
        qty += order_qty
    return [qty, qty+order_qty]


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

    b_prec, q_prec = exchange.get_assetPrecision(symbol)
    ticker_price = exchange.ticker_price(symbol)

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
    print('sell 1 price: %s' % (sell1_price))
    print("ticker price: %s" % (ticker_price))
    print(' buy 1 price: %s' % (buy1_price))
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
    qtys += [maker_bids_total_qty, maker_asks_total_qty]
    qtys += calc_qty_by_diff(maker_asks, ticker_price, 0.01)
    qtys += calc_qty_by_diff(maker_bids, ticker_price, 0.01)
    qtys += calc_qty_by_diff(maker_asks, ticker_price, 0.1)
    qtys += calc_qty_by_diff(maker_bids, ticker_price, 0.1)
    qtys += calc_qty_by_diff(maker_asks, ticker_price, 0.3)
    qtys += calc_qty_by_diff(maker_bids, ticker_price, 0.3)

    qtys = list(set(qtys))
    qtys.sort()
    if qtys[0] == 0:
        qtys = qtys[1:]

    slippage_fmt = '10.5f'
    print('%15s | %s | %s' % ('', ' buy (take asks) '.center(80, '-'), ' sell (take bids) '.center(80, '-')))
    t_fmt = '%15s | %11s  %20s %16s %15s(%11s)  | %11s  %20s %16s %15s(%11s)'
    print(t_fmt % ('qty', 'slippage', 'cost', 'avg price', 'edge price', 'slippage',
        'slippage', 'cost', 'avg price', 'edge price', 'slippage'))
    for qty in qtys:
        taker_buy_avg_price, taker_buy_cost, taker_buy_edge_price = calc_average_price(maker_asks, qty)
        taker_sell_avg_price, taker_sell_cost, taker_sell_edge_price = calc_average_price(maker_bids, qty)
        taker_buy_slippage = diff_price(taker_buy_avg_price, ticker_price)
        taker_sell_slippage = diff_price(taker_sell_avg_price, ticker_price)
        taker_buy_diff_et = diff_price(taker_buy_edge_price, ticker_price)
        taker_sell_diff_et = diff_price(taker_sell_edge_price, ticker_price)
        if (not taker_buy_slippage or not taker_sell_slippage):
            print('-'*181)
        print(t_fmt % (round(qty, b_prec),
            format_percent(slippage_fmt, taker_buy_slippage),
            round(taker_buy_cost, 9) if taker_buy_cost else None,
            round(taker_buy_avg_price, q_prec+1) if taker_buy_avg_price else None,
            taker_buy_edge_price,
            format_percent(slippage_fmt, taker_buy_diff_et),
            format_percent(slippage_fmt, taker_sell_slippage),
            round(taker_sell_cost, 9) if taker_sell_cost else None,
            round(taker_sell_avg_price, q_prec+1) if taker_sell_avg_price else None,
            taker_sell_edge_price,
            format_percent(slippage_fmt, taker_sell_diff_et)
            )
        )
        if qty%10 == 0:
            print('-'*181)

