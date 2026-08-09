import talib
from . import *

def calc_volume_indicators(quoter, config, df, calc_all,
        key_open, key_high, key_low, key_close, key_volume, key_oi, prefix='', trial=None):
    key_xs = []

    name = 'AD'
    key_x = get_feature_key(name, config, prefix, calc_all, trial)
    if key_high and key_x:
        df[key_x] = talib.AD(df[key_high], df[key_low], df[key_close], df[key_volume])
        key_xs.append(key_x)

    name = 'ADER'
    n, key_x = get_feature_1p(name, config, prefix, calc_all, trial, 3)
    if key_high and key_x:
        AD = talib.AD(df[key_high], df[key_low], df[key_close], df[key_volume])
        df[key_x] = AD / EMA(AD, n) - 1
        key_xs.append(key_x)

    name = 'ADOSC'
    fp, sp, key_x = get_feature_2p(name, config, prefix, calc_all, trial, 3, 10)
    if key_high and key_x:
        df[key_x] = talib.ADOSC(df[key_high], df[key_low], df[key_close], df[key_volume],
                               fastperiod=fp, slowperiod=sp)
        key_xs.append(key_x)

    name = 'OBV'
    key_x = get_feature_key(name, config, prefix, calc_all, trial)
    if key_high and key_x:
        df[key_x] = talib.OBV(df[key_close], df[key_volume])
        key_xs.append(key_x)

    name = 'OBVER'
    n, key_x = get_feature_1p(name, config, prefix, calc_all, trial, 4)
    if key_high and key_x:
        OBV = talib.OBV(df[key_close], df[key_volume])
        df[key_x] = OBV / EMA(OBV, n) - 1
        key_xs.append(key_x)

    name = 'EMV'
    n, key_x = get_feature_1p(name, config, prefix, calc_all, trial, 14)
    if key_high and key_x:
        emv = EMV(df[key_high], df[key_low], df[key_volume], n)
        df[key_x] = emv
        key_xs.append(key_x)

    name = 'EMV_intraday'
    n, key_x = get_feature_1p(name, config, prefix, calc_all, trial, 14)
    if key_high and key_x:
        emv = EMV_intraday(df[key_high], df[key_low], df[key_volume], n)
        df[key_x] = emv
        key_xs.append(key_x)

    name = 'WVAD'
    n, key_x = get_feature_1p(name, config, prefix, calc_all, trial, 12)
    if key_high and key_x:
        wvad = WVAD(df[key_open], df[key_high], df[key_low], df[key_close], df[key_volume], 12)
        df[key_x] = wvad
        key_xs.append(key_x)

    name = 'WVAD_intraday'
    n, key_x = get_feature_1p(name, config, prefix, calc_all, trial, 12)
    if key_high and key_x:
        wvad = WVAD_intraday(df[key_open], df[key_high], df[key_low], df[key_close], df[key_volume], n)
        df[key_x] = wvad
        key_xs.append(key_x)

    name = 'WVADR'
    n, m, key_x = get_feature_2p(name, config, prefix, calc_all, trial, 12, 24)
    if key_high and key_x:
        wvadr = WVADR(df[key_open], df[key_high], df[key_low], df[key_close], df[key_volume], n, m)
        df[key_x] = wvadr
        key_xs.append(key_x)

    name = 'WVADR_intraday'
    n, m, key_x = get_feature_2p(name, config, prefix, calc_all, trial, 12, 24)
    if key_high and key_x:
        wvadr = WVADR_intraday(df[key_open], df[key_high], df[key_low], df[key_close], df[key_volume], n, m)
        df[key_x] = wvadr
        key_xs.append(key_x)

    name = 'VOLR'
    n, key_x = get_feature_1p(name, config, prefix, calc_all, trial, 20)
    if key_high and key_x:
        volr = df[key_volume] / df[key_volume].rolling(n).mean()
        df[key_x] = volr
        key_xs.append(key_x)

    return key_xs
