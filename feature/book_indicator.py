import talib
from . import *

def calc_book_indicators(quoter, config, df, calc_all, key_bid, key_bid_size, key_ask, key_ask_size, prefix='', trial=None):
    key_xs = []

    name = 'size.imb'
    key_x = get_feature_key(name, config, prefix, calc_all, trial)
    if key_x:
        bid_size = df[key_bid_size]
        bid_price = df[key_bid]
        ask_size = df[key_ask_size]
        ask_price = df[key_ask]

        size_diff = (bid_size - ask_size) / (bid_size + ask_size)
        price_diff = (ask_price - bid_price) / (bid_price + ask_price)
        df[key_x] = size_diff / price_diff
        key_xs.append(key_x)

    name = 'wpr.ema'
    n, key_x = get_feature_1p(name, config, prefix, calc_all, trial, 16)
    if key_x:
        wpr = WPR(df[key_bid], df[key_bid_size], df[key_ask], df[key_ask_size])
        df[key_x] = 1 - EMA(wpr, n)/wpr
        key_xs.append(key_x)

    name = 'WPR'
    key_x = get_feature_key(name, config, prefix, calc_all, trial)
    if key_x:
        wpr = WPR(df[key_bid], df[key_bid_size], df[key_ask], df[key_ask_size])
        df[key_x] = wpr
        key_xs.append(key_x)

    name = 'WPR_robust'
    key_x = get_feature_key(name, config, prefix, calc_all, trial)
    if key_x:
        wpr = WPR_robust(df[key_bid], df[key_bid_size], df[key_ask], df[key_ask_size])
        df[key_x] = wpr
        key_xs.append(key_x)

    name = 'spread'
    key_x = get_feature_key(name, config, prefix, calc_all, trial)
    if key_x:
        df[key_x] = df[key_ask] - df[key_bid]
        key_xs.append(key_x)

    name = 'spread_radio'
    key_x = get_feature_key(name, config, prefix, calc_all, trial)
    if key_x:
        wpr = WPR(df[key_bid], df[key_bid_size], df[key_ask], df[key_ask_size])
        df[key_x] = (df[key_ask] - df[key_bid]) / wpr
        key_xs.append(key_x)

    name = 'size.r'
    key_x = get_feature_key(name, config, prefix, calc_all, trial)
    if key_x:
        df[key_x] = df[key_ask_size] / df[key_bid_size]
        key_xs.append(key_x)

    name = 'depth_imbalance'
    key_x = get_feature_key(name, config, prefix, calc_all, trial)
    if key_x:
        df[key_x] = (df[key_bid_size] - df[key_ask_size]) / (df[key_bid_size] + df[key_ask_size])
        key_xs.append(key_x)

    return key_xs
