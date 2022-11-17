
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

tick_prefix = 'KQ.m@SHFE.cu.'
tick_key_last   = tick_prefix + 'last_price'
tick_key_volume = tick_prefix + 'volume'
tick_key_oi     = tick_prefix + 'open_interest'

k_key_open_time  = 'open_time'
k_key_close_time = 'close_time'
k_key_open       = 'open'
k_key_high       = 'high'
k_key_low        = 'low'
k_key_close      = 'close'
k_key_volume     = 'volume'
k_key_oi         = 'open_interest'

k_columns=['open_time', 'open', 'high', 'low', 'close', 'volume', 'open_interest']

def init_k(tick_time, last_price, open_interest):
    open_minute = tick_time.minute - tick_time.minute%5
    open_time = tick_time.replace(minute=open_minute, second=0, microsecond=0)
    close_time = open_time + timedelta(minutes=5)
    k = {
        k_key_open_time: open_time,
        k_key_open:  last_price,
        k_key_high:  last_price,
        k_key_low:   last_price,
        k_key_close: last_price,
        k_key_volume: 0,
        k_key_oi: open_interest
    }
    #print('init tick time: {}; close_time: {}'.format(tick_time, close_time), end='')
    return close_time, k


def finish_k(csv_file, k):
    ks = []
    for key in k_columns:
        ks.append(k[key])
    csv_file.writerow(ks)
    '''
    print('    kline: {} ~ {}, v: {}, o: {}, h: {}, l: {}, c: {}, volume: {} {}'.format(
        k[k_key_open_time], k[k_key_close_time], k[k_key_volume],
        k[k_key_open], k[k_key_high], k[k_key_low], k[k_key_close],
        tick_volume, pre_volume))
    '''


def to_kline(tick_df, csv_file):
    kls = []
    k = None
    pre_volume = 0
    start_cost_time = datetime.now()
    for i, d in tick_df.iterrows():
        tick_time = datetime.fromtimestamp(int(d.datetime_nano) / 1000000000)
        last_price = d[tick_key_last]
        tick_volume = d[tick_key_volume]
        open_interest = d[tick_key_oi]
        if not k:
            close_time, k = init_k(tick_time, last_price, open_interest)
        else:
            if tick_time <= close_time:
                if last_price > k[k_key_high]:
                    k[k_key_high] = last_price
                if last_price < k[k_key_low]:
                    k[k_key_low] = last_price
                k[k_key_volume] = tick_volume - pre_volume
                k[k_key_close] = last_price
                k[k_key_close_time] = tick_time
                k[k_key_oi] = open_interest

            if tick_time >= close_time:
                kls.append(k)
                finish_k(csv_file, k)

                open_price = last_price
                if tick_time == close_time:
                    pre_volume = tick_volume
                else:
                    pre_d = tick_df.iloc[i-1]
                    pre_tick_time = datetime.fromtimestamp(int(pre_d.datetime_nano) / 1000000000)
                    if tick_time - pre_tick_time < timedelta(minutes=9):
                        open_price = pre_d[tick_key_last]
                    pre_volume = pre_d[tick_key_volume]
                    if tick_volume < pre_volume:
                        pre_volume = 0
                close_time, k = init_k(tick_time, open_price, open_interest)

        if pre_volume == tick_volume:
            sys.stdout.flush()
            sys.stdout.write(
                "{}  progress: {:%},  cost: {},  tick: {}\r".format(
                    " "*10,
                    (i+1)/len(tick_df),
                    datetime.now() - start_cost_time,
                    tick_time,
                )
            )

    sys.stdout.write('\n')
    kls.append(k)
    finish_k(csv_file, k)

    return kls 


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='')
    #parser.add_argument('-source', required=True, choices=get_exchange_names(), help='market data source')
    #parser.add_argument('-symbol', required=True, help='symbol: btc_usdt')
    #parser.add_argument('-interval', required=True, help='kline types: 1m,4h,1d')
    parser.add_argument('-files', required=True, help='')
    args = parser.parse_args()

    for tick_file_name in args.files.split(','):
        print('read file: ', tick_file_name)
        cost_start = datetime.now()
        tick_df = pd.read_csv(tick_file_name)
        print('  cost: %s'%(datetime.now()-cost_start))
        print(tick_df)
        
        index = tick_file_name.find('.csv')
        kline_file_name = tick_file_name[:index] + '_5m' + tick_file_name[index:]
        print(kline_file_name)

        openResult = open(kline_file_name, 'a+')
        csv_file = csv.writer(openResult)
        csv_file.writerow(k_columns)
        to_kline(tick_df, csv_file)
        openResult.close()


