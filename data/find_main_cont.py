import sys
import os
import argparse
from datetime import datetime
import pandas as pd

key_time = 'datetime_str'
vs  = []
ois  = []
vois = []


def load_days_df(symbol):
    return pd.read_csv(f'{symbol}_1d.csv')


def append_to_ss(ss, code, multiplier, k_t):
    if (not ss) or (ss and code > ss[-1][0]):
        ss.append([code, multiplier, f'{k_t.split(" ")[0]}T15'])


def check_switch(multiplier, symbol_prev, symbol, df, suffix_last):
    key_v_prev  = f'volume'
    key_v       = f'volume{suffix_last}'
    key_oi_prev = f'close_oi'
    key_oi      = f'close_oi{suffix_last}'

    print(symbol)
    e_name, _ = symbol.split('.')
    if e_name == 'CZCE':
        code_len = 3
    else:
        code_len = 4
    code = int(symbol[-code_len:])
    for idx, k in df.iterrows():
        k_t = k[key_time]
        v_is_over  = k[key_v_prev]  < k[key_v]
        oi_is_over = k[key_oi_prev] < k[key_oi]

        if v_is_over:
            print('  v: ' + f'{k_t},  prev: {k[key_v_prev]:12}, {k[key_oi_prev]:12};  cur:{k[key_v]:12}, {k[key_oi]:12}')
            append_to_ss(vs, code, multiplier, k_t)

        if oi_is_over:
            print(' oi: ' + f'{k_t},  prev: {k[key_v_prev]:12}, {k[key_oi_prev]:12};  cur:{k[key_v]:12}, {k[key_oi]:12}')
            append_to_ss(ois, code, multiplier, k_t)

        if (v_is_over and oi_is_over):
            print(f'voi: {k_t}')
            print()
            append_to_ss(vois, code, multiplier, k_t)
            break

def print_ss(ss):
    import json
    print(json.dumps(ss))
    #for s in ss:
    #    print(s)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='switch main contracte')
    parser.add_argument('-product', required=True, help='egg: SHFE.rb')
    parser.add_argument('-codes', nargs='*', help='egg: 1605')
    parser.add_argument('--window', type=int, default=56, help='')
    parser.add_argument('--broker', help='')
    args = parser.parse_args()

    if args.codes:
        codes = args.codes
    else:
        from data import get_main_codes
        codes = get_main_codes(args.product)
    print(codes)

    from data import get_multiplier
    multiplier = get_multiplier(args.product)

    pd.set_option('display.max_rows', None)
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', 1000)

    suffix_last = '_last'
    symbol_prev = None
    for code in codes:
        symbol = args.product + code
        df = load_days_df(symbol)

        if symbol_prev:
            join_df = pd.merge(df_prev[-args.window:], df, how='left',
                    left_on=key_time, right_on=key_time, suffixes=('', suffix_last) )

            check_switch(multiplier, symbol_prev, symbol, join_df, suffix_last)
        
        symbol_prev = symbol
        df_prev = df

    print('vs:')
    print_ss(vs)

    print('ois:')
    print_ss(ois)

    print('vois:')
    print_ss(vois)
