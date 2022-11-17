import talib
from . import *

def calc_other_indicators(quoter, is_tick, config, df, calc_all=False):
    key_xs = []

    if is_tick:
        key_high = None
        key_close = quoter.tick_key_close
        key_volume = quoter.tick_key_volume
    else:
        key_open = quoter.kline_key_open
        key_close = quoter.kline_key_close
        key_high = quoter.kline_key_high
        key_low = quoter.kline_key_low
        key_volume = quoter.kline_key_volume
        key_oi = quoter.kline_key_oi

    name = 'CLV'
    if key_high and (calc_all or name in config):
        key_x = '%s' % (name)
        df[key_x] = CLV(df[key_high], df[key_low], df[key_close])
        key_xs.append(key_x)

    name = 'CV'
    if key_high and (calc_all or name in config):
        key_x = '%s' % (name)
        period = 10
        df[key_x] = CV(df[key_high], df[key_low], period)
        key_xs.append(key_x)

    name = 'DBCD'
    if key_high and (calc_all or name in config):
        key_x = '%s' % (name)
        df[key_x] = DBCD(df[key_close])
        key_xs.append(key_x)

    name = 'PB'
    if key_high and (calc_all or name in config):
        scs = [{"n": 20}]
        if name in config and config[name]:
            scs = config[name]
            if type(scs) != list:
                scs = [scs]
        for sc in scs:
            period = sc['n']
            key_x = '%s_%s' % (name, period)
            df[key_x] = PB(df[key_close], period)
            key_xs.append(key_x)

    name = 'BW'
    if key_high and (calc_all or name in config):
        scs = [{"n": 20}]
        if name in config and config[name]:
            scs = config[name]
            if type(scs) != list:
                scs = [scs]
        for sc in scs:
            period = sc['n']
            key_x = '%s_%s' % (name, period)
            df[key_x] = BW(df[key_close], period)
            key_xs.append(key_x)

    name = 'KDJ'
    if key_high and (calc_all or name in config):
        key_x = '%s' % (name)
        period = 9
        k, d, j = KDJ(df[key_high], df[key_low], df[key_close], period)
        df[key_x] = j
        key_xs.append(key_x)

    name = 'CMF'
    if key_high and (calc_all or name in config):
        n = 21
        key_x = '%s_%s' % (name, n)
        df[key_x] = CMF(df[key_high], df[key_low], df[key_close], df[key_volume], n)
        key_xs.append(key_x)

    name = 'CR'
    if key_high and (calc_all or name in config):
        n = 20
        key_x = '%s_%s' % (name, n)
        df[key_x] = CR(df[key_high], df[key_low], df[key_close], n)
        key_xs.append(key_x)

    name = 'MassIndex'
    if key_high and (calc_all or name in config):
        n = 9
        key_x = '%s_%s' % (name, n)
        df[key_x] = MassIndex(df[key_high], df[key_low], df[key_close], n)
        key_xs.append(key_x)

    name = 'ElderRayIndex'
    if key_high and (calc_all or name in config):
        n = 13
        key_x = '%s_%s' % (name, n)
        df[key_x] = ElderRayIndex(df[key_high], df[key_low], df[key_close], n)
        key_xs.append(key_x)

    name = 'UOS'
    if key_high and (calc_all or name in config):
        key_x = '%s' % (name)
        df[key_x] = UOS(df[key_high], df[key_low], df[key_close])
        key_xs.append(key_x)

    name = 'ASIR'
    if key_high and (calc_all or name in config):
        n = 20
        key_x = '%s_%s' % (name, n)
        df[key_x] = ASIR(df[key_open], df[key_high], df[key_low], df[key_close], n)
        key_xs.append(key_x)

    name = 'UI'
    if key_high and (calc_all or name in config):
        n = 10
        key_x = '%s_%s' % (name, n)
        df[key_x] = UI(df[key_close], n)
        key_xs.append(key_x)

    name = 'nBIAS'
    if calc_all or name in config:
        ary = []
        if name in config:
            scs = config[name]
            if type(scs) != list:
                scs = [scs]
            if not scs:
                scs = [{"n": 13}]

        for sc in scs:
            t = sc['t']
            n = sc['n']
            key_x = '%s_%s_%s' % (name, t, n)
            if t == 'c':
                s = df[key_close]
            elif t == 'v':
                s = df[key_volume]
            elif t == 'oi':
                s = df[key_oi]
            else:
                s = df[key_close]
            df[key_x] = BIAS(s, n)
            key_xs.append(key_x)

    name = 'n-mBIAS'
    if calc_all or name in config:
        ary = []
        if name in config:
            scs = config[name]
            if type(scs) != list:
                scs = [scs]
            if not scs:
                scs = [{"n": 13, "m": 39}]

        for sc in scs:
            t = sc['t']
            n = sc['n']
            m = sc['m']
            key_x = '%s_%s_%s_%s' % (name, t, n, m)
            if t == 'c':
                s = df[key_close]
            elif t == 'v':
                s = df[key_volume]
            elif t == 'oi':
                s = df[key_oi]
            else:
                s = df[key_close]
            df[key_x] = nmBIAS(s, n, m)
            key_xs.append(key_x)
    return key_xs
