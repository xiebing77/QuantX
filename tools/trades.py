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
    parser.add_argument('--stat', action="store_true", help=' stat position ...')
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
    trades = exchange.trades(symbol, args.limit)
    print("%-25s: %s" % ("length", len(trades)) )
    if not trades:
        exit(1)
    
    buyer_taker = {
        'qty': 0,
        'asset': 0
    }
    seller_taker = {
        'qty': 0,
        'asset': 0
    }
    for trade in trades:
        trade['datatime'] = exchange.get_time_from_trade_data(trade)

        qty = float(trade[exchange.Trade_Key_Qty])
        asset = qty * float(trade[exchange.Trade_Key_Price])
        if exchange.taker_is_buyer(trade):
            buyer_taker['qty'] += qty
            buyer_taker['asset'] += asset
        else:
            seller_taker['qty'] += qty
            seller_taker['asset'] += asset


    #pprint.pprint(trades)
    trades_df = pd.DataFrame(trades)
    #trades_df['price'] = pd.to_numeric(trades_df['price'])
    #trades_df['qty'] = pd.to_numeric(trades_df['qty'])
    print(trades_df)

    fmt = '{}  qty: {:16.8f};  asset: {:16.8f}'
    print(fmt.format(' buyer taker', buyer_taker['qty'], buyer_taker['asset']))
    print(fmt.format('seller taker', seller_taker['qty'], seller_taker['asset']))

    if args.stat:
        head_dt = exchange.get_time_from_data_ts(trades[0][exchange.Order_Time_Key])
        tail_dt = exchange.get_time_from_data_ts(trades[-1][exchange.Order_Time_Key])
        print("%-25s: %s  ~  %s" % ("time range", head_dt, tail_dt) )

        position_qty, cost, commission = calc_trades(exchange, trades)
        cur_price = exchange.ticker_price(symbol)
        floating_gross_profit = cur_price * position_qty + cost
        print("%-25s: %s" % ("position qty", round(position_qty,b_prec)))
        print("%-25s: %s" % ("cost", cost))
        print("%-25s: %s" % ("commission", commission))
        print("%-25s: %s" % ("floating grossprofit", floating_gross_profit))
