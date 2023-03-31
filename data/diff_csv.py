
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


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('-source', required=True, choices=get_exchange_names(), help='market data source')
    parser.add_argument('-files', required=True, nargs=2, help='')
    args = parser.parse_args()

    exchange = create_exchange(args.source)
    if not exchange:
        print("market data source error!")
        exit(1)

    df_a = pd.read_csv(args.files[0])
    df_b = pd.read_csv(args.files[1])
    
    print('count old: {},  new: {}'.format(len(df_a), len(df_b)))
    k_key_open_time = exchange.kline_key_open_time
    open_key   = exchange.kline_key_open
    close_key  = exchange.kline_key_close
    high_key   = exchange.kline_key_high
    low_key    = exchange.kline_key_low
    volume_key = exchange.kline_key_volume
    oi_key     = exchange.kline_key_oi

    max_i_b = len(df_b) - 1
    i_a = 0
    i_b = 0
    fmt_k = '{}  o: {},  h: {},  l: {},  c: {},  v: {}'
    while i_a < len(df_a) and i_b <= max_i_b:
        k_a = df_a.iloc[i_a]
        k_b = df_b.iloc[i_b]
        open_time_a = exchange.get_time_from_data_ts(k_a[k_key_open_time])
        open_time_b = exchange.get_time_from_data_ts(k_b[k_key_open_time])

        sys.stdout.flush()
        sys.stdout.write("{}  {:.2%}\r".format(open_time_b, i_b/max_i_b))

        if open_time_a == open_time_b:
            if (k_a[open_key]  != k_b[open_key] or
                k_a[close_key] != k_b[close_key] or
                k_a[high_key]  != k_b[high_key] or
                k_a[low_key]   != k_b[low_key] or
                k_a[volume_key] != k_b[volume_key] or
                k_a[oi_key]    != k_b[oi_key]):
                print('{}:'.format(open_time_a), end='')
                print(fmt_k.format(' '*2 +'old',
                    k_a[open_key], k_a[high_key], k_a[low_key], k_a[close_key],
                    k_a[volume_key], k_a[oi_key]))
                print(fmt_k.format(' '*22+'new',
                    k_b[open_key], k_b[high_key], k_b[low_key], k_b[close_key],
                    k_b[volume_key], k_b[oi_key]))
            i_a += 1
            i_b += 1
            continue

        #print('index a: {},  b: {}'.format(i_a, i_b))
        if open_time_a > open_time_b:
            o_p = k_b[open_key]
            h_p = k_b[high_key]
            l_p = k_b[low_key]
            c_p = k_b[close_key]
            info = fmt_k.format('', o_p, h_p, l_p, c_p, k_b[volume_key])
            print('old lack {},    new{}'.format(open_time_b, info))
            i_b += 1
        else:
            o_p = k_a[open_key]
            h_p = k_a[high_key]
            l_p = k_a[low_key]
            c_p = k_a[close_key]
            if k_a[volume_key] != 0 or not (o_p == c_p and h_p == l_p and o_p == h_p):
                info = fmt_k.format('', o_p, h_p, l_p, c_p, k_a[volume_key])
                print('new lack {},    old{}'.format(open_time_a, info))
            i_a += 1        

    sys.stdout.write('\n')

