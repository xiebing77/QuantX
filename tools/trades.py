#!/usr/bin/python3
import sys
sys.path.append('../')
import argparse
from exchange.exchange_factory import get_exchange_names, create_exchange
import pprint
import pandas as pd
import engine.quote as quote


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='quary my trades')
    parser.add_argument('-exchange', choices=get_exchange_names(), help='exchange name')
    parser.add_argument('-symbol', required=True, help='symbol, eg: btc_usdt')
    parser.add_argument('-limit', help='')
    parser.add_argument('--stat', action="store_true", help=' stat position ...')
    parser.add_argument('--agg', action="store_true", help=' agg trades ...')
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

    sever_time = exchange.time()
    print('sever time: ', sever_time)

    symbol = args.symbol
    b_prec, q_prec = exchange.get_assetPrecision(symbol)
    params = {}
    if args.limit:
        params['limit'] = args.limit
    if args.agg:
        trades = exchange.agg_trades(symbol, **params)
    else:
        trades = exchange.trades(symbol, **params)

    print('market trades({}): {} ~ {} '.format(len(trades),
        exchange.get_time_from_trade_data(trades[-1]),
        exchange.get_time_from_trade_data(trades[0])))
    if not trades:
        exit(1)
    for trade in trades:
        trade['datatime'] = exchange.get_time_from_trade_data(trade)
    #pprint.pprint(trades)

    trades_df = pd.DataFrame(trades)
    #trades_df['price'] = pd.to_numeric(trades_df['price'])
    #trades_df['qty'] = pd.to_numeric(trades_df['qty'])
    print(trades_df)

    maker_buyer, maker_seller = quote.stat_trades(exchange, trades)
    fmt = '{}  qty: {:16.8f};  asset: {:16.8f}'
    print(fmt.format('maker buyer  ', maker_buyer['qty'], maker_buyer['asset']))
    print(fmt.format('maker seller ', maker_seller['qty'], maker_seller['asset']))

    if args.stat:
        head_dt = exchange.get_time_from_data_ts(trades[0][exchange.Trade_Key_Time])
        tail_dt = exchange.get_time_from_data_ts(trades[-1][exchange.Trade_Key_Time])
        print("%-25s: %s  ~  %s" % ("time range", head_dt, tail_dt) )

