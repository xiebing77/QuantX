import talib

def calc_cycle_indicators(quoter, config, df, calc_all, key_price, prefix=''):
    key_xs = []

    name = 'HT_DCPERIOD'
    if calc_all or name in config:
        key_x = f'{prefix}{name}'
        df[key_x] = talib.HT_DCPERIOD(df[key_price])
        key_xs.append(key_x)

    name = 'HT_DCPHASE'
    if calc_all or name in config:
        key_x = f'{prefix}{name}'
        df[key_x] = talib.HT_DCPHASE(df[key_price])
        key_xs.append(key_x)

    name = 'HT_PHASOR'
    if calc_all or name in config:
        key_x = f'{prefix}{name}'
        inphase, quadrature = talib.HT_PHASOR(df[key_price])
        df[key_x] = inphase
        key_xs.append(key_x)

    name = 'HT_SINE'
    if calc_all or name in config:
        key_x = f'{prefix}{name}'
        sine, leadsine = talib.HT_SINE(df[key_price])
        df[key_x] = sine
        key_xs.append(key_x)

    name = 'HT_TRENDMODE'
    if calc_all or name in config:
        key_x = f'{prefix}{name}'
        df[key_x] = talib.HT_TRENDMODE(df[key_price])
        key_xs.append(key_x)
    return key_xs

