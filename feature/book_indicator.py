import talib
from . import *

def calc_book_indicators(quoter, config, df, calc_all, key_bid, key_bid_size, key_ask, key_ask_size):
    key_xs = []

    name = 'size.imb'
    if calc_all or name in config:
        key_x = '%s' % (name)
        df[key_x] = (df[key_bid_size]-df[key_ask_size])/(df[key_bid_size]+df[key_ask_size])/df[key_ask]-(df[key_bid])/(df[key_bid]+df[key_ask])*2
        key_xs.append(key_x)

    name = 'wpr.ema'
    if calc_all or name in config:
        N = 16
        key_x = '{}_{}'.format(name, N)
        wpr = WPR(df[key_bid], df[key_bid_size], df[key_ask], df[key_ask_size])
        df[key_x] = 1 - EMA(wpr, N)/wpr
        key_xs.append(key_x)

    return key_xs
