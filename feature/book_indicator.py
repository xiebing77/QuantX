import talib
from . import *

def calc_book_indicators(quoter, config, df, calc_all, key_bid, key_bid_size, key_ask, key_ask_size):
    key_xs = []

    name = 'size.imb'
    if calc_all or name in config:
        key_x = '%s' % (name)
        bid_size = df[key_bid_size]
        bid_price = df[key_bid]
        ask_size = df[key_ask_size]
        ask_price = df[key_ask]

        size_diff = (bid_size - ask_size) / (bid_size + ask_size)
        price_diff = (ask_price - bid_price) / (bid_price + ask_price)
        df[key_x] = size_diff / price_diff
        key_xs.append(key_x)

    name = 'wpr.ema'
    if calc_all or name in config:
        N = 16
        key_x = '{}_{}'.format(name, N)
        wpr = WPR(df[key_bid], df[key_bid_size], df[key_ask], df[key_ask_size])
        df[key_x] = 1 - EMA(wpr, N)/wpr
        key_xs.append(key_x)

    name = 'WPR'
    if calc_all or name in config:
        key_x = f'{name}'
        wpr = WPR(df[key_bid], df[key_bid_size], df[key_ask], df[key_ask_size])
        df[key_x] = wpr
        key_xs.append(key_x)

    name = 'WPR_robust'
    if calc_all or name in config:
        key_x = f'{name}'
        wpr = WPR_robust(df[key_bid], df[key_bid_size], df[key_ask], df[key_ask_size])
        df[key_x] = wpr
        key_xs.append(key_x)

    name = 'spread'
    if calc_all or name in config:
        key_x = f'{name}'
        df[key_x] = df[key_ask] - df[key_bid]
        key_xs.append(key_x)

    name = 'spread_radio'
    if calc_all or name in config:
        key_x = f'{name}'
        wpr = WPR(df[key_bid], df[key_bid_size], df[key_ask], df[key_ask_size])
        df[key_x] = (df[key_ask] - df[key_bid]) / wpr
        key_xs.append(key_x)

    name = 'size.r'
    if calc_all or name in config:
        key_x = f'{name}'
        df[key_x] = df[key_ask_size] / df[key_bid_size]
        key_xs.append(key_x)

    name = 'depth_imbalance'
    if calc_all or name in config:
        key_x = f'{name}'
        df[key_x] = (df[key_bid_size] - df[key_ask_size]) / (df[key_bid_size] + df[key_ask_size])
        key_xs.append(key_x)

    return key_xs
