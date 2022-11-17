import talib

def calc_volume_indicators(quoter, is_tick, config, df, calc_all=False):
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

    name = 'AD'
    if key_high and (calc_all or name in config):
        key_x = '%s' % (name)
        df[key_x] = talib.AD(df[key_high], df[key_low], df[key_close], df[key_volume])
        key_xs.append(key_x)

    name = 'ADOSC'
    if key_high and (calc_all or name in config):
        if name in config and 'fastperiod' in config[name]:
            fp = config[name]['fastperiod']
            sp = config[name]['slowperiod']
        else:
            fp = 3
            sp = 10
        key_x = '%s_%s_%s' % (name, fp, sp)
        df[key_x] = talib.ADOSC(df[key_high], df[key_low], df[key_close], df[key_volume],
                               fastperiod=fp, slowperiod=sp)
        key_xs.append(key_x)

    name = 'OBV'
    if key_high and (calc_all or name in config):
        key_x = '%s' % (name)
        df[key_x] = talib.OBV(df[key_close], df[key_volume])
        key_xs.append(key_x)

    return key_xs
