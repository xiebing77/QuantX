
import sys
sys.path.append('../')
import argparse
import json
import time
from datetime import datetime, timedelta
import db.mongodb as md
import common.kline as kl
from exchange.exchange_factory import get_exchange_names, create_exchange
from db.mongodb import get_mongodb
from setup import *
import pandas as pd
import csv

tick_prefix = ''#'KQ.m@SHFE.rb.'
tick_key_last   = tick_prefix + 'last_price'
tick_key_highest = tick_prefix + 'highest'
tick_key_lowest = tick_prefix + 'lowest'
tick_key_volume = tick_prefix + 'volume'
tick_key_oi     = tick_prefix + 'open_interest'


def is_day(t):
    return 9 <= t.hour < 15

def is_night(t):
    if 21 <= t.hour:
        return True
    if t.hour < 3:
        return True
    return False

def not_a_day(pre_t, t):
    return pre_t.date() != t.date()


def init_k_hl(pre_tick, tick, open_time, open_price):
    last_price = tick[tick_key_last]
    day_highest = tick[tick_key_highest]
    day_lowest  = tick[tick_key_lowest]

    if pre_tick is None:
        return day_highest, day_lowest

    # first k of a day
    pre_tick_time = pre_tick.last_time
    if ( is_day(pre_tick_time) and
        (is_night(tick.last_time) or not_a_day(pre_tick_time, tick.last_time))
    ):
        return day_highest, day_lowest

    if tick.last_time == open_time:
        return last_price, last_price

    if pre_tick[tick_key_highest] < day_highest:
        high = day_highest
    else:
        high = max(open_price, last_price)

    if pre_tick[tick_key_lowest] > day_lowest:
        low = day_lowest
    else:
        low = min(open_price, last_price)
    return high, low


def update_k_hl(exchange, pre_tick, tick, k):
    k_key_high = exchange.kline_key_high
    k_key_low  = exchange.kline_key_low
    last_price = tick[tick_key_last]
    day_highest = tick[tick_key_highest]
    if day_highest > pre_tick[tick_key_highest]:
        k[k_key_high] = day_highest
    elif last_price > k[k_key_high]:
        k[k_key_high] = last_price

    day_lowest = tick[tick_key_lowest]
    if day_lowest < pre_tick[tick_key_lowest]:
        k[k_key_low] = day_lowest
    elif last_price < k[k_key_low]:
        k[k_key_low] = last_price


def init_k(exchange, interval, pre_tick, tick, open_price):
    tick_volume = tick[tick_key_volume]
    open_interest = tick[tick_key_oi]

    open_time = kl.get_open_time(interval, tick.last_time)
    close_time = open_time + kl.get_interval_timedelta(interval)
    high, low = init_k_hl(pre_tick, tick, open_time, open_price)
    k = {
        #"open_time": open_time,
        exchange.kline_key_open_time: exchange.get_data_ts_from_time(open_time),
        exchange.kline_key_open:  open_price,
        exchange.kline_key_high:  high,
        exchange.kline_key_low:   low,
        exchange.kline_key_close: open_price,
        exchange.kline_key_volume: 0,
        exchange.kline_key_oi: open_interest
    }
    return close_time, k


def to_kline(exchange, interval, tick_df, need_book=False):
    kls = []
    start_cost_time = datetime.now()
    tick = tick_df.iloc[0]
    close_time, k = init_k(exchange, interval, None, tick, tick[tick_key_last])
    pre_tick = tick
    pre_volume = 0
    for i, tick in tick_df[1:].iterrows():
        tick_time = tick.last_time
        last_price = tick[tick_key_last]
        tick_volume = tick[tick_key_volume]
        open_interest = tick[tick_key_oi]
        if tick_time <= close_time:
            update_k_hl(exchange, pre_tick, tick, k)

            k[exchange.kline_key_volume] = tick_volume - pre_volume
            k[exchange.kline_key_close] = last_price
            #k[k_key_close_time] = tick_time
            k[exchange.kline_key_oi] = open_interest

            if need_book:
                k[exchange.book_key_bid]      = tick[exchange.book_key_bid]
                k[exchange.book_key_bid_size] = tick[exchange.book_key_bid_size]
                k[exchange.book_key_ask]      = tick[exchange.book_key_ask]
                k[exchange.book_key_ask_size] = tick[exchange.book_key_ask_size]

        if tick_time >= close_time:
            kls.append(k)

            open_price = last_price
            if tick_time == close_time:
                pre_volume = tick_volume
            else:
                pre_tick_time = pre_tick.last_time
                if tick_time - pre_tick_time < timedelta(minutes=9):
                    open_price = pre_tick[tick_key_last]
                pre_volume = pre_tick[tick_key_volume]
                if tick_volume < pre_volume:
                    pre_volume = 0
            close_time, k = init_k(exchange, interval, pre_tick, tick, open_price)

            sys.stdout.flush()
            sys.stdout.write(
                "{}  progress: {:%},  cost: {},  tick: {}\r".format(
                    " "*10,
                    (i+1)/len(tick_df),
                    datetime.now() - start_cost_time,
                    tick_time,
                )
            )

        pre_tick = tick

    kls.append(k)
    sys.stdout.write('\n')
    return kls 


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('-source', required=True, choices=get_exchange_names(), help='market data source')
    #parser.add_argument('-symbol', required=True, help='symbol: btc_usdt')
    parser.add_argument('-interval', required=True, help='kline types: 1m, 5m, 1h, 1d')
    parser.add_argument('-files', required=True, nargs='*', help='')
    parser.add_argument('--book', action="store_true", help='book info')
    args = parser.parse_args()

    exchange = create_exchange(args.source)
    if not exchange:
        print("market data source error!")
        exit(1)

    for tick_file_name in args.files:
        print('read file: ', tick_file_name)
        cost_start = datetime.now()
        tick_df = pd.read_csv(tick_file_name)
        print('  cost: %s'%(datetime.now()-cost_start))
        tick_df['last_time'] = tick_df[exchange.tick_key_close_time].apply(exchange.get_time_from_data_ts)
        print(tick_df)
        
        index = tick_file_name.find('.csv')
        kline_file_name = tick_file_name[:index] + '_' + args.interval + tick_file_name[index:]
        print(kline_file_name)

        kls = to_kline(exchange, args.interval, tick_df, args.book)
        kls_df = pd.DataFrame(kls)
        kls_df.to_csv(kline_file_name, encoding='utf-8', index=False)

