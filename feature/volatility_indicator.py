import talib

def calc_volatility_indicators(quoter, config, df, calc_all,
        key_open, key_high, key_low, key_close, key_volume, key_oi, prefix=''):
    key_xs = []

    name = 'ATR'
    if key_high and (calc_all or name in config):
        if name in config and 'period' in config[name]:
            tp = config[name]['period']
        else:
            tp = 14
        key_x = f'{prefix}{name}_{tp}'
        df[key_x] = talib.ATR(df[key_high], df[key_low], df[key_close], timeperiod=tp)
        key_xs.append(key_x)

    name = 'NATR'
    if key_high and (calc_all or name in config):
        if name in config and 'period' in config[name]:
            tp = config[name]['period']
        else:
            tp = 14
        key_x = f'{prefix}{name}_{tp}'
        df[key_x] = talib.NATR(df[key_high], df[key_low], df[key_close], timeperiod=tp)
        key_xs.append(key_x)

    name = 'TRANGE'
    if key_high and (calc_all or name in config):
        key_x = f'{prefix}{name}'
        df[key_x] = talib.TRANGE(df[key_high], df[key_low], df[key_close])
        key_xs.append(key_x)

    return key_xs
