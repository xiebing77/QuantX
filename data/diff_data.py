
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
    parser.add_argument('-symbols', required=True, help='symbol: btc_usdt')
    parser.add_argument('-interval', required=True, help='kline types: 1m,4h,1d')
    args = parser.parse_args()

    exchange = create_exchange(args.source)
    if not exchange:
        print("market data source error!")
        exit(1)

    db = get_mongodb(args.source)

    symbols = args.symbols.split(',')
    collection_a = kl.get_kline_collection(symbols[0], args.interval)
    collection_b = kl.get_kline_collection(symbols[1], args.interval)

    kls_a = db.find(collection_a, {})
    kls_b = db.find(collection_b, {})
    print('count old: {},  new: {}'.format(len(kls_a), len(kls_b)))
    open_time_key = exchange.kline_key_open_time
    open_key   = exchange.kline_key_open
    close_key  = exchange.kline_key_close
    high_key   = exchange.kline_key_high
    low_key    = exchange.kline_key_low
    volume_key = exchange.kline_key_volume

    i_a = 0
    i_b = 0
    fmt_k = '{}  o: {},  h: {},  l: {},  c: {},  v: {}'
    while i_a < len(kls_a) and i_b < len(kls_b):
        k_a = kls_a[i_a]
        k_b = kls_b[i_b]
        if k_a[open_time_key] == k_b[open_time_key]:
            if (k_a[open_key]  != k_b[open_key] or
                k_a[close_key] != k_b[close_key] or
                k_a[high_key]  != k_b[high_key] or
                k_a[low_key]   != k_b[low_key] or
                k_a[volume_key] != k_b[volume_key]):
                print('{}:'.format(exchange.get_time_from_data_ts(k_a[open_time_key])))
                print(fmt_k.format(' '*20+'old', k_a[open_key], k_a[high_key], k_a[low_key], k_a[close_key], k_a[volume_key]))
                print(fmt_k.format(' '*20+'new', k_b[open_key], k_b[high_key], k_b[low_key], k_b[close_key], k_b[volume_key]))
            i_a += 1
            i_b += 1
            continue

        #print('index a: {},  b: {}'.format(i_a, i_b))
        if k_a[open_time_key] > k_b[open_time_key]:
            o_p = k_b[open_key]
            h_p = k_b[high_key]
            l_p = k_b[low_key]
            c_p = k_b[close_key]
            t = exchange.get_time_from_data_ts(k_b[open_time_key])
            info = fmt_k.format('', o_p, h_p, l_p, c_p, k_b[volume_key])
            print('old lack {},    new{}'.format(t, info))
            i_b += 1
        else:
            o_p = k_a[open_key]
            h_p = k_a[high_key]
            l_p = k_a[low_key]
            c_p = k_a[close_key]
            if k_a[volume_key] != 0 or not (o_p == c_p and h_p == l_p and o_p == h_p):
                t = exchange.get_time_from_data_ts(k_a[open_time_key])
                info = fmt_k.format('', o_p, h_p, l_p, c_p, k_a[volume_key])
                print('new lack {},    old{}'.format(t, info))
            i_a += 1        

