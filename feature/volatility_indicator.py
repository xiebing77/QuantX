import talib

def calc_volatility_indicators(quoter, is_tick, config, df, calc_all=False):
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

    name = 'ATR'
    if key_high and (calc_all or name in config):
        if name in config and 'period' in config[name]:
            tp = config[name]['period']
        else:
            tp = 14
        key_x = '%s_%s' % (name, tp)
        df[key_x] = talib.ATR(df[key_high], df[key_low], df[key_close], timeperiod=tp)
        key_xs.append(key_x)

    name = 'NATR'
    if key_high and (calc_all or name in config):
        if name in config and 'period' in config[name]:
            tp = config[name]['period']
        else:
            tp = 14
        key_x = '%s_%s' % (name, tp)
        df[key_x] = talib.NATR(df[key_high], df[key_low], df[key_close], timeperiod=tp)
        key_xs.append(key_x)

    name = 'TRANGE'
    if key_high and (calc_all or name in config):
        key_x = '%s' % (name)
        df[key_x] = talib.TRANGE(df[key_high], df[key_low], df[key_close])
        key_xs.append(key_x)

    return key_xs
