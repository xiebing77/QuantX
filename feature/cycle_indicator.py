import talib

def calc_cycle_indicators(quoter, config, kdf, calc_all=False):
    key_xs = []
    key_close = quoter.kline_key_close

    name = 'HT_DCPERIOD'
    if calc_all or name in config:
        key_x = '%s' % (name)
        kdf[key_x] = talib.HT_DCPERIOD(kdf[key_close])
        key_xs.append(key_x)

    name = 'HT_DCPHASE'
    if calc_all or name in config:
        key_x = '%s' % (name)
        kdf[key_x] = talib.HT_DCPHASE(kdf[key_close])
        key_xs.append(key_x)

    name = 'HT_PHASOR'
    if calc_all or name in config:
        key_x = '%s' % (name)
        inphase, quadrature = talib.HT_PHASOR(kdf[key_close])
        kdf[key_x] = inphase
        key_xs.append(key_x)

    name = 'HT_SINE'
    if calc_all or name in config:
        key_x = '%s' % (name)
        sine, leadsine = talib.HT_SINE(kdf[key_close])
        kdf[key_x] = sine
        key_xs.append(key_x)

    name = 'HT_TRENDMODE'
    if calc_all or name in config:
        key_x = '%s' % (name)
        kdf[key_x] = talib.HT_TRENDMODE(kdf[key_close])
        key_xs.append(key_x)
    return key_xs

