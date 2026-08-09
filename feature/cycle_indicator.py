import talib
from . import *

def calc_cycle_indicators(quoter, config, df, calc_all, key_price, prefix='', trial=None):
    key_xs = []

    name = 'HT_DCPERIOD'
    key_x = get_feature_key(name, config, prefix, calc_all, trial)
    if key_x:
        df[key_x] = talib.HT_DCPERIOD(df[key_price])
        key_xs.append(key_x)

    name = 'HT_DCPHASE'
    key_x = get_feature_key(name, config, prefix, calc_all, trial)
    if key_x:
        df[key_x] = talib.HT_DCPHASE(df[key_price])
        key_xs.append(key_x)

    name = 'HT_PHASOR'
    key_x = get_feature_key(name, config, prefix, calc_all, trial)
    if key_x:
        inphase, quadrature = talib.HT_PHASOR(df[key_price])
        df[key_x] = inphase
        key_xs.append(key_x)

    name = 'HT_SINE'
    key_x = get_feature_key(name, config, prefix, calc_all, trial)
    if key_x:
        sine, leadsine = talib.HT_SINE(df[key_price])
        df[key_x] = sine
        key_xs.append(key_x)

    name = 'HT_TRENDMODE'
    key_x = get_feature_key(name, config, prefix, calc_all, trial)
    if key_x:
        df[key_x] = talib.HT_TRENDMODE(df[key_price])
        key_xs.append(key_x)
    return key_xs

