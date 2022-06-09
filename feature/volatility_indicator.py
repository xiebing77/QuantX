import talib

def calc_volatility_indicators(quoter, config, kdf, calc_all=False):
    key_xs = []
    key_open = quoter.kline_key_open
    key_close = quoter.kline_key_close
    key_high = quoter.kline_key_high
    key_low = quoter.kline_key_low

    name = 'ATR'
    if calc_all or name in config:
        if name in config and 'period' in config[name]:
            tp = config[name]['period']
        else:
            tp = 14
        key_x = '%s_%s' % (name, tp)
        kdf[key_x] = talib.ATR(kdf[key_high], kdf[key_low], kdf[key_close], timeperiod=tp)
        key_xs.append(key_x)

    name = 'NATR'
    if calc_all or name in config:
        if name in config and 'period' in config[name]:
            tp = config[name]['period']
        else:
            tp = 14
        key_x = '%s_%s' % (name, tp)
        kdf[key_x] = talib.NATR(kdf[key_high], kdf[key_low], kdf[key_close], timeperiod=tp)
        key_xs.append(key_x)

    name = 'TRANGE'
    if calc_all or name in config:
        key_x = '%s' % (name)
        kdf[key_x] = talib.TRANGE(kdf[key_high], kdf[key_low], kdf[key_close])
        key_xs.append(key_x)

    return key_xs
