#!/usr/bin/python3
import sys
sys.path.append('../')
import argparse
from exchange.exchange_factory import get_exchange_names, create_exchange
import pprint
import pandas as pd


def calc_trades(exchange, trades):
    commission = {}
    position_qty = 0
    cost = 0

    for trade in trades:
        if trade[exchange.Trade_Key_CommissionQty]:
            trade_commissionQty = float(trade[exchange.Trade_Key_CommissionQty])
            asset_name = trade[exchange.Trade_Key_CommissionAsset]
            if asset_name in commission:
                commission[asset_name] += trade_commissionQty
            else:
                commission[asset_name] = trade_commissionQty
        else:
            # 提醒：bitrue的成交佣金字段为None，但是实际有，直接扣除标的资产，例如：
            #    委托 150      WASP 限价价格0.714 USDT  冻结金额 10.71 USDT
            #    成交 149.8875 WASP 成交价格0.714 USDT  结算金额 10.71 USDT(成交金额10.7019675, 佣金0.0080325)
            pass

        trade_qty = float(trade[exchange.Trade_Key_Qty])
        trade_value = float(trade[exchange.Trade_Key_Price]) * trade_qty
        if trade[exchange.Trade_Key_IsBuyer]:
            position_qty += trade_qty
            cost -= trade_value
        else:
            position_qty -= trade_qty
            cost += trade_value

    return position_qty, cost, commission


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
    b_prec, q_prec = exchange.get_assetPrecision(symbol)
    my_trades = exchange.my_trades(symbol, args.limit)
    print("%-25s: %s" % ("length", len(my_trades)) )
    if not my_trades:
        exit(1)

    #pprint.pprint(my_trades)
    my_trades_df = pd.DataFrame(my_trades)
    my_trades_df['price'] = pd.to_numeric(my_trades_df['price'])
    my_trades_df['qty'] = pd.to_numeric(my_trades_df['qty'])
    print(my_trades_df)

    head_dt = exchange.get_time_from_data_ts(my_trades[0][exchange.Order_Time_Key])
    tail_dt = exchange.get_time_from_data_ts(my_trades[-1][exchange.Order_Time_Key])
    print("%-25s: %s  ~  %s" % ("time range", head_dt, tail_dt) )

    position_qty, cost, commission = calc_trades(exchange, my_trades)
    cur_price = exchange.ticker_price(symbol)
    floating_gross_profit = cur_price * position_qty + cost
    print("%-25s: %s" % ("position qty", round(position_qty,b_prec)))
    print("%-25s: %s" % ("cost", cost))
    print("%-25s: %s" % ("commission", commission))
    print("%-25s: %s" % ("floating grossprofit", floating_gross_profit))
