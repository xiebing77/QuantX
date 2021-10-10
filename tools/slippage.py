#!/usr/bin/python3
import sys
sys.path.append('../')
import argparse
from exchange.exchange_factory import get_exchange_names, create_exchange
from common import SIDE_BUY, SIDE_SELL


def format_percent(fmt, f):
    return format(f*100, fmt) if f else None


def calc_total_qty(orders):
    total_qty = 0
    for order in orders:
        order_qty = float(order[1])
        order_price = float(order[0])
        total_qty += order_qty
    return total_qty


def diff_price(price, ticker_price):
    if not price:
        return None
    return abs(price - ticker_price) / ticker_price


def calc_average_price(orders, qty):
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
    depth_limit = exchange.depth_limits[-1]
    book = exchange.depth(symbol, depth_limit)
    # print(book)
    maker_asks = book['asks']
    maker_bids = book['bids']
    print('depth limit: %s,  asks: %s,  bids: %s' % (
        depth_limit, len(maker_asks), len(maker_bids)))
    print("ticker price: %s" % (ticker_price))

    maker_asks_total_qty = calc_total_qty(maker_asks)
    maker_bids_total_qty = calc_total_qty(maker_bids)
    print("asks total qty: %20s,  bids total qty: %20s" % (maker_asks_total_qty, maker_bids_total_qty))
    if maker_asks_total_qty < qty or maker_bids_total_qty < qty:
        print("The order book depth is not enough. Please get more orders")

    taker_buy_avg_price, taker_buy_cost, _ = calc_average_price(maker_asks, qty)
    taker_sell_avg_price, taker_sell_cost, _ = calc_average_price(maker_bids, qty)
    sl_str = '-'*75
    print(sl_str)
    slippage_fmt = '12.4f'
    sl_fmt = '%20s:  %25s  %25s'
    print(sl_fmt % ('Side', 'buy (take asks)', 'sell (take bids)'))
    print(sl_fmt % ('Average deal price', taker_buy_avg_price, taker_sell_avg_price))
    print(sl_fmt % ('Total cost', taker_buy_cost, taker_sell_cost))
    print(sl_fmt % ('Slippage(%)',
        format_percent(slippage_fmt, diff_price(taker_buy_avg_price, ticker_price)),
        format_percent(slippage_fmt, diff_price(taker_sell_avg_price, ticker_price))))
    print(sl_str)

