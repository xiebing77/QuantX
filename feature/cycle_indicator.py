import talib

def calc_cycle_indicators(quoter, is_tick, config, df, calc_all=False):
    key_xs = []

    if is_tick:
        key_close = quoter.tick_key_close
    else:
        key_close = quoter.kline_key_close

    name = 'HT_DCPERIOD'
    if calc_all or name in config:
        key_x = '%s' % (name)
        df[key_x] = talib.HT_DCPERIOD(df[key_close])
        key_xs.append(key_x)

    name = 'HT_DCPHASE'
    if calc_all or name in config:
        key_x = '%s' % (name)
        df[key_x] = talib.HT_DCPHASE(df[key_close])
        key_xs.append(key_x)

    name = 'HT_PHASOR'
    if calc_all or name in config:
        key_x = '%s' % (name)
        inphase, quadrature = talib.HT_PHASOR(df[key_close])
        df[key_x] = inphase
        key_xs.append(key_x)

    name = 'HT_SINE'
    if calc_all or name in config:
        key_x = '%s' % (name)
        sine, leadsine = talib.HT_SINE(df[key_close])
        df[key_x] = sine
        key_xs.append(key_x)

    name = 'HT_TRENDMODE'
    if calc_all or name in config:
        key_x = '%s' % (name)
        df[key_x] = talib.HT_TRENDMODE(df[key_close])
        key_xs.append(key_x)
    return key_xs

