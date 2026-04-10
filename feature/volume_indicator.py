import talib
from . import *

def calc_volume_indicators(quoter, config, df, calc_all,
        key_open, key_high, key_low, key_close, key_volume, key_oi, prefix=''):
    key_xs = []

    name = 'AD'
    if key_high and (calc_all or name in config):
        key_x = f'{prefix}{name}'
        df[key_x] = talib.AD(df[key_high], df[key_low], df[key_close], df[key_volume])
        key_xs.append(key_x)

    name = 'ADER'
    if key_high and (calc_all or name in config):
        key_x = f'{prefix}{name}'
        AD = talib.AD(df[key_high], df[key_low], df[key_close], df[key_volume])
        df[key_x] = AD / EMA(AD, 3) - 1
        key_xs.append(key_x)

    name = 'ADOSC'
    if key_high and (calc_all or name in config):
        if name in config and 'fastperiod' in config[name]:
            fp = config[name]['fastperiod']
            sp = config[name]['slowperiod']
        else:
            fp = 3
            sp = 10
        key_x = f'{prefix}{name}_{fp}_{sp}'
        df[key_x] = talib.ADOSC(df[key_high], df[key_low], df[key_close], df[key_volume],
                               fastperiod=fp, slowperiod=sp)
        key_xs.append(key_x)

    name = 'OBV'
    if key_high and (calc_all or name in config):
        key_x = f'{prefix}{name}'
        df[key_x] = talib.OBV(df[key_close], df[key_volume])
        key_xs.append(key_x)

    name = 'OBVER'
    if key_high and (calc_all or name in config):
        key_x = f'{prefix}{name}'
        OBV = talib.OBV(df[key_close], df[key_volume])
        df[key_x] = OBV / EMA(OBV, 4) - 1
        key_xs.append(key_x)

    name = 'EMV'
    if key_high and (calc_all or name in config):
        key_x = f'{prefix}{name}'
        emv = EMV(df[key_high], df[key_low], df[key_volume])
        df[key_x] = emv
        key_xs.append(key_x)

    name = 'WVAD'
    if key_high and (calc_all or name in config):
        key_x = f'{prefix}{name}'
        wvad = WVAD(df[key_open], df[key_high], df[key_low], df[key_close], df[key_volume])
        df[key_x] = wvad
        key_xs.append(key_x)

    name = 'WVADR'
    if key_high and (calc_all or name in config):
        key_x = f'{prefix}{name}'
        wvadr = WVADR(df[key_open], df[key_high], df[key_low], df[key_close], df[key_volume])
        df[key_x] = wvadr
        key_xs.append(key_x)

    return key_xs
