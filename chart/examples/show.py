import sys
sys.path.append('../../')
import argparse
import pandas as pd
import common
import common.kline as kl
from exchange.exchange_factory import get_exchange_names, create_exchange
from engine.quote import DBQuoteEngine
from chart import chart_mpf2, chart_add_all_argument


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='show')
    parser.add_argument('-exchange', choices=get_exchange_names(), help='exchange name')
    parser.add_argument('-symbol', help='symbol (btc_usdt)')
    parser.add_argument('-interval', help='interval')
    parser.add_argument('-range', help='time range')
    #parser.add_argument('-di', nargs='*', help='display indicators,egg: MACD KDJ RSI')
    parser.add_argument('-yscale', default="linear", choices=["linear", "log", "symlog", "logit"], help='yscale')

    parser.add_argument('--volume', action="store_true", help='volume')
    parser.add_argument('--okls', nargs='*', help='other klines')
    chart_add_all_argument(parser)
    args = parser.parse_args()

    symbol = args.symbol
    interval = args.interval
    exchange = create_exchange(args.exchange)
    if not exchange:
        print("exchange name error!")
        exit(1)
    exchange.name = 'binance'
    quote_engine = DBQuoteEngine(exchange)

    start_time, end_time = common.parse_date_range(args.range)
    display_count = int((end_time - start_time).total_seconds()/kl.get_interval_seconds(interval))
    print("display_count: %s" % display_count)
    kline_collection = kl.get_kline_collection(symbol, interval)
    klines = quote_engine.get_original_klines(kline_collection, start_time, end_time)

    title = symbol + '  ' + interval
    chart_mpf2(title, args, symbol, pd.DataFrame(klines), quote_engine.quoter, display_count)
