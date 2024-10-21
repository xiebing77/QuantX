import talib
from . import *

def calc_overlap_indicators(quoter, is_tick, config, kdf, calc_all=False):
    key_xs = []
    key_open = quoter.kline_key_open
    key_close = quoter.kline_key_close
    key_high = quoter.kline_key_high
    key_low = quoter.kline_key_low

    name = 'BBANDS'
    if calc_all or name in config:
        if name in config and 'period' in config[name]:
            tp = config[name]['period']
        else:
            tp = 20
        key_x = '%s_%s' % (name, tp)
        upperband, middleband, lowerband = talib.BBANDS(kdf[key_close], timeperiod=tp)
        kdf[key_x] = (upperband - lowerband) / middleband
        #m = MA(kdf[key_close], tp)
        #kdf[key_x] = 4 * m.std() / m
        key_xs.append(key_x)

    '''
    name = 'DEMA'
    if calc_all or name in config:
        tp = config[name]['period']
        key_x = '%s_%s' % (name, tp)
        kdf[key_x] = talib.DEMA(kdf[key_close], timeperiod=tp)
        key_xs.append(key_x)

    name = 'EMA'
    if calc_all or name in config:
        tp = config[name]['period']
        key_x = '%s_%s' % (name, tp)
        kdf[key_x] = talib.EMA(kdf[key_close], timeperiod=tp)
        key_xs.append(key_x)

    name = 'MA'
    if calc_all or name in config:
        tp = config[name]['period']
        key_x = '%s_%s' % (name, tp)
        kdf[key_x] = talib.MA(kdf[key_close], timeperiod=tp)
        key_xs.append(key_x)

    name = 'KAMA'
    if calc_all or name in config:
        tp = config[name]['period']
        key_x = '%s_%s' % (name, tp)
        kdf[key_x] = talib.KAMA(kdf[key_close], timeperiod=tp)
        key_xs.append(key_x)

    name = 'MAMA'
    if calc_all or name in config:
        tp = config[name]['period']
        fl = 0
        sl = 0
        key_x = '%s_%s_%s' % (name, fl, sl)
        kdf[key_x] = talib.MAMA(kdf[key_close], fastlimit=fl, slowlimit=sl)
        key_xs.append(key_x)

    name = 'HT_TRENDLINE'
    if calc_all or name in config:
        key_x = '%s' % (name)
        kdf[key_x] = talib.HT_TRENDLINE(kdf[key_close])
        key_xs.append(key_x)

    name = 'MIDPOINT'
    if calc_all or name in config:
        tp = config[name]['period']
        key_x = '%s_%s' % (name, tp)
        kdf[key_x] = talib.MIDPOINT(kdf[key_close], timeperiod=tp)
        key_xs.append(key_x)

    name = 'MIDPRICE'
    if calc_all or name in config:
        tp = config[name]['period']
        key_x = '%s_%s' % (name, tp)
        kdf[key_x] = talib.MIDPRICE(kdf[key_high], kdf[key_low], timeperiod=tp)
        key_xs.append(key_x)

    name = 'SAR'
    if calc_all or name in config:
        key_x = '%s' % (name)
        kdf[key_x] = talib.SAR(kdf[key_high], kdf[key_low], acceleration=0, maximum=0)
        key_xs.append(key_x)

    name = 'SAREXT'
    if calc_all or name in config:
        key_x = '%s' % (name)
        kdf[key_x] = talib.SAREXT(kdf[key_high], kdf[key_low],
            startvalue=0, offsetonreverse=0,
            accelerationinitlong=0, accelerationlong=0, accelerationmaxlong=0,
            accelerationinitshort=0, accelerationshort=0, accelerationmaxshort=0)
        key_xs.append(key_x)


    name = 'SMA'
    if calc_all or name in config:
        tp = config[name]['period']
        key_x = '%s_%s' % (name, tp)
        kdf[key_x] = talib.SMA(kdf[key_close], timeperiod=tp)
        key_xs.append(key_x)

    name = 'T3'
    if calc_all or name in config:
        tp = config[name]['period']
        key_x = '%s_%s' % (name, tp)
        kdf[key_x] = talib.T3(kdf[key_close], timeperiod=tp)
        key_xs.append(key_x)

    name = 'TEMA'
    if calc_all or name in config:
        tp = config[name]['period']
        key_x = '%s_%s' % (name, tp)
        kdf[key_x] = talib.TEMA(kdf[key_close], timeperiod=tp)
        key_xs.append(key_x)

    name = 'TRIMA'
    if calc_all or name in config:
        tp = config[name]['period']
        key_x = '%s_%s' % (name, tp)
        kdf[key_x] = talib.TRIMA(kdf[key_close], timeperiod=tp)
        key_xs.append(key_x)

    name = 'WMA'
    if calc_all or name in config:
        tp = config[name]['period']
        key_x = '%s_%s' % (name, tp)
        kdf[key_x] = talib.WMA(kdf[key_close], timeperiod=tp)
        key_xs.append(key_x)

    name = 'TSF'
    if calc_all or name in config:
        if name in config and 'period' in config[name]:
            tp = config[name]['period']
        else:
            tp = 14
        key_x = '%s_%s' % (name, tp)
        kdf[key_x] = talib.TSF(kdf[key_close], timeperiod=tp)
        key_xs.append(key_x)
    '''

    return key_xs

