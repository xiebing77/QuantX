import talib
from . import *


def ATR_C(high, low, close, tp=14):
    atr = talib.ATR(high, low, close, timeperiod=tp)
    return atr / close * 10000


def calc_volatility_indicators(quoter, config, df, calc_all,
        key_open, key_high, key_low, key_close, key_volume, key_oi, prefix='', trial=None):
    key_xs = []

    name = 'ATR'
    tp, key_x = get_feature_1p(name, config, prefix, calc_all, trial, 14)
    if key_high and key_x:
        df[key_x] = talib.ATR(df[key_high], df[key_low], df[key_close], timeperiod=tp)
        key_xs.append(key_x)

    name = 'ATR_C'
    tp, key_x = get_feature_1p(name, config, prefix, calc_all, trial, 14)
    if key_high and key_x:
        df[key_x] = ATR_C(df[key_high], df[key_low], df[key_close], tp)
        key_xs.append(key_x)

    name = 'vol_accel'
    n, key_x = get_feature_1p(name, config, prefix, calc_all, trial, 5)
    if key_high and key_x:
        atr_c = ATR_C(df[key_high], df[key_low], df[key_close], n)
        df[key_x] = atr_c - atr_c.shift(n)
        key_xs.append(key_x)

    name = 'ATR_M'
    fp, sp, key_x = get_feature_2p(name, config, prefix, calc_all, trial, 20, 60)
    if key_high and key_x:
        atr = talib.ATR(df[key_high], df[key_low], df[key_close], timeperiod=fp)
        df[key_x] = atr / atr.rolling(sp).mean() -1
        key_xs.append(key_x)

    name = 'NATR'
    tp, key_x = get_feature_1p(name, config, prefix, calc_all, trial, 14)
    if key_high and key_x:
        df[key_x] = talib.NATR(df[key_high], df[key_low], df[key_close], timeperiod=tp)
        key_xs.append(key_x)

    name = 'TRANGE'
    key_x = get_feature_key(name, config, prefix, calc_all, trial)
    if key_high and key_x:
        df[key_x] = talib.TRANGE(df[key_high], df[key_low], df[key_close])
        key_xs.append(key_x)

    return key_xs
