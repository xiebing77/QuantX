#!/usr/bin/python3
import sys
sys.path.append('../')
import argparse
from exchange.exchange_factory import get_exchange_names, create_exchange
import pprint


def calc_trades(exchange, trades):
    commission = {}
    position_qty = 0
    gross_profit = 0

    for trade in trades:
        trade_commissionQty = float(trade[exchange.Trade_Key_CommissionQty])
        asset_name = trade[exchange.Trade_Key_CommissionAsset]
        if asset_name in commission:
            commission[asset_name] += trade_commissionQty
        else:
            commission[asset_name] = trade_commissionQty

        trade_qty = float(trade[exchange.Trade_Key_Qty])
        trade_value = float(trade[exchange.Trade_Key_Price]) * trade_qty
        if trade[exchange.Trade_Key_IsBuyer]:
            position_qty += trade_qty
            gross_profit -= trade_value
        else:
            position_qty -= trade_qty
            gross_profit += trade_value

    return position_qty, gross_profit, commission


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='quary my trades')
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
    my_trades = exchange.my_trades(symbol, args.limit)
    print("%-25s: %s" % ("length", len(my_trades)) )
    if not my_trades:
        exit(1)
    pprint.pprint(my_trades)

    head_dt = exchange.get_time_from_data_ts(my_trades[0][exchange.Order_Time_Key])
    tail_dt = exchange.get_time_from_data_ts(my_trades[-1][exchange.Order_Time_Key])
    print("%-25s: %s  ~  %s" % ("time range", head_dt, tail_dt) )

    position_qty, gross_profit, commission = calc_trades(exchange, my_trades)
    cur_price = exchange.ticker_price(symbol)
    floating_gross_profit = cur_price * position_qty + gross_profit
    print("%-25s: %s" % ("position qty", position_qty))
    print("%-25s: %s" % ("floating grossprofit", floating_gross_profit))
    print("%-25s: %s" % ("commission", commission))
