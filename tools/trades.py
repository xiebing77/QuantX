#!/usr/bin/python3
import sys
sys.path.append('../')
import argparse
from exchange.exchange_factory import get_exchange_names, create_exchange
import pprint
import pandas as pd


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
        head_dt = exchange.get_time_from_data_ts(trades[0][exchange.Trade_Key_Time])
        tail_dt = exchange.get_time_from_data_ts(trades[-1][exchange.Trade_Key_Time])
        print("%-25s: %s  ~  %s" % ("time range", head_dt, tail_dt) )

