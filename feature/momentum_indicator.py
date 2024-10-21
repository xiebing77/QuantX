import talib

def calc_momentum_indicators(quoter, is_tick, config, df, calc_all=False):
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

    name = 'ADX'
    if key_high and (calc_all or name in config):
        if name in config and 'period' in config[name]:
            tp = config[name]['period']
        else:
            tp = 14
        key_x = '%s_%s' % (name, tp)
        df[key_x] = talib.ADX(df[key_high], df[key_low], df[key_close], timeperiod=tp)
        key_xs.append(key_x)

    name = 'ADXR'
    if key_high and (calc_all or name in config):
        if name in config and 'period' in config[name]:
            tp = config[name]['period']
        else:
            tp = 14
        key_x = '%s_%s' % (name, tp)
        df[key_x] = talib.ADXR(df[key_high], df[key_low], df[key_close], timeperiod=tp)
        key_xs.append(key_x)

    name = 'APO'
    if calc_all or name in config:
        key_x = '%s' % (name)
        fp = 12
        sp = 26
        key_x = '%s_%s_%s' % (name, fp, sp)
        df[key_x] = talib.APO(df[key_close], fastperiod=fp, slowperiod=sp, matype=0)
        key_xs.append(key_x)

    name = 'AROONOSC'
    if key_high and (calc_all or name in config):
        if name in config and 'period' in config[name]:
            tp = config[name]['period']
        else:
            tp = 14
        key_x = '%s_%s' % (name, tp)
        df[key_x] = talib.AROONOSC(df[key_high], df[key_low], timeperiod=tp)
        key_xs.append(key_x)

    name = 'BOP'
    if key_high and (calc_all or name in config):
        key_x = '%s' % (name)
        df[key_x] = talib.BOP(df[key_open], df[key_high], df[key_low], df[key_close])
        key_xs.append(key_x)

    name = 'CCI'
    if key_high and (calc_all or name in config):
        if name in config and 'period' in config[name]:
            tp = config[name]['period']
        else:
            tp = 14
        key_x = '%s_%s' % (name, tp)
        df[key_x] = talib.CCI(df[key_high], df[key_low], df[key_close], timeperiod=tp)
        key_xs.append(key_x)

    name = 'CMO'
    if calc_all or name in config:
        if name in config and 'period' in config[name]:
            tp = config[name]['period']
        else:
            tp = 14
        key_x = '%s_%s' % (name, tp)
        df[key_x] = talib.CMO(df[key_close], timeperiod=tp)
        key_xs.append(key_x)

    name = 'DX'
    if key_high and (calc_all or name in config):
        if name in config and 'period' in config[name]:
            tp = config[name]['period']
        else:
            tp = 14
        key_x = '%s_%s' % (name, tp)
        df[key_x] = talib.DX(df[key_high], df[key_low], df[key_close], timeperiod=tp)
        key_xs.append(key_x)

    name = 'MACD'
    if calc_all or name in config:
        fastperiod = 12
        slowperiod = 26
        signalperiod = 9
        key_x = '%s_%s' % (name, tp)
        macd, macdsignal, macdhist = talib.MACD(df[key_close],
            fastperiod=fastperiod, slowperiod=slowperiod, signalperiod=signalperiod)
        df[key_x] = macdhist
        key_xs.append(key_x)

    name = 'MACDEXT'
    if calc_all or name in config:
        fastperiod = 12
        slowperiod = 26
        signalperiod = 9
        key_x = '%s_%s' % (name, tp)
        macd, macdsignal, macdhist = talib.MACDEXT(df[key_close],
            fastperiod=fastperiod, fastmatype=0, slowperiod=slowperiod, slowmatype=0,
            signalperiod=signalperiod, signalmatype=0)
        df[key_x] = macdhist
        key_xs.append(key_x)

    name = 'MACDFIX'
    if calc_all or name in config:
        signalperiod = 9
        key_x = '%s_%s' % (name, tp)
        macd, macdsignal, macdhist = talib.MACDFIX(df[key_close], signalperiod=signalperiod)
        df[key_x] = macdhist
        key_xs.append(key_x)

    name = 'MFI'
    if key_high and (calc_all or name in config):
        key_x = '%s' % (name)
        df[key_x] = talib.MFI(df[key_open], df[key_high], df[key_low], df[key_volume])
        key_xs.append(key_x)

    name = 'MINUS_DI'
    if key_high and (calc_all or name in config):
        if name in config and 'period' in config[name]:
            tp = config[name]['period']
        else:
            tp = 14
        key_x = '%s_%s' % (name, tp)
        df[key_x] = talib.MINUS_DI(df[key_high], df[key_low], df[key_close], timeperiod=tp)
        key_xs.append(key_x)

    name = 'MINUS_DM'
    if key_high and (calc_all or name in config):
        if name in config and 'period' in config[name]:
            tp = config[name]['period']
        else:
            tp = 14
        key_x = '%s_%s' % (name, tp)
        df[key_x] = talib.MINUS_DM(df[key_high], df[key_low], timeperiod=tp)
        key_xs.append(key_x)

    name = 'MOM'
    if calc_all or name in config:
        if name in config and 'period' in config[name]:
            tp = config[name]['period']
        else:
            tp = 10
        key_x = '%s_%s' % (name, tp)
        df[key_x] = talib.MOM(df[key_close], timeperiod=tp)
        key_xs.append(key_x)

    name = 'PLUS_DI'
    if key_high and (calc_all or name in config):
        if name in config and 'period' in config[name]:
            tp = config[name]['period']
        else:
            tp = 14
        key_x = '%s_%s' % (name, tp)
        df[key_x] = talib.PLUS_DI(df[key_high], df[key_low], df[key_close], timeperiod=tp)
        key_xs.append(key_x)

    name = 'PLUS_DM'
    if key_high and (calc_all or name in config):
        if name in config and 'period' in config[name]:
            tp = config[name]['period']
        else:
            tp = 14
        key_x = '%s_%s' % (name, tp)
        df[key_x] = talib.PLUS_DM(df[key_high], df[key_low], timeperiod=tp)
        key_xs.append(key_x)

    name = 'PPO'
    if calc_all or name in config:
        key_x = '%s' % (name)
        fp = 12
        sp = 26
        key_x = '%s_%s_%s' % (name, fp, sp)
        df[key_x] = talib.PPO(df[key_close], fastperiod=fp, slowperiod=sp, matype=0)
        key_xs.append(key_x)

    name = 'ROC'
    if calc_all or name in config:
        if name in config and 'period' in config[name]:
            tp = config[name]['period']
        else:
            tp = 10
        key_x = '%s_%s' % (name, tp)
        df[key_x] = talib.ROC(df[key_close], timeperiod=tp)
        key_xs.append(key_x)

    name = 'ROCP'
    if calc_all or name in config:
        if name in config and 'period' in config[name]:
            tp = config[name]['period']
        else:
            tp = 10
        key_x = '%s_%s' % (name, tp)
        df[key_x] = talib.ROCP(df[key_close], timeperiod=tp)
        key_xs.append(key_x)

    name = 'ROCR'
    if calc_all or name in config:
        if name in config and 'period' in config[name]:
            tp = config[name]['period']
        else:
            tp = 10
        key_x = '%s_%s' % (name, tp)
        df[key_x] = talib.ROCR(df[key_close], timeperiod=tp)
        key_xs.append(key_x)

    name = 'ROCR100'
    if calc_all or name in config:
        if name in config and 'period' in config[name]:
            tp = config[name]['period']
        else:
            tp = 10
        key_x = '%s_%s' % (name, tp)
        df[key_x] = talib.ROCR100(df[key_close], timeperiod=tp)
        key_xs.append(key_x)

    name = 'RSI'
    if calc_all or name in config:
        if name in config and 'period' in config[name]:
            tp = config[name]['period']
        else:
            tp = 14
        key_x = '%s_%s' % (name, tp)
        df[key_x] = talib.RSI(df[key_close], timeperiod=tp)
        key_xs.append(key_x)

    name = 'STOCH'
    if key_high and (calc_all or name in config):
        key_x = '%s' % (name)
        slowk, slowd = talib.STOCH(df[key_high], df[key_low], df[key_close],
            fastk_period=5, slowk_period=3, slowk_matype=0, slowd_period=3, slowd_matype=0)
        df[key_x] = slowk - slowd
        key_xs.append(key_x)

    name = 'STOCH-k'
    if key_high and (calc_all or name in config):
        key_x = '%s' % (name)
        slowk, slowd = talib.STOCH(df[key_high], df[key_low], df[key_close],
            fastk_period=5, slowk_period=3, slowk_matype=0, slowd_period=3, slowd_matype=0)
        df[key_x] = slowk
        key_xs.append(key_x)

    name = 'STOCH-d'
    if key_high and (calc_all or name in config):
        key_x = '%s' % (name)
        slowk, slowd = talib.STOCH(df[key_high], df[key_low], df[key_close],
            fastk_period=5, slowk_period=3, slowk_matype=0, slowd_period=3, slowd_matype=0)
        df[key_x] = slowd
        key_xs.append(key_x)

    name = 'STOCHF'
    if key_high and (calc_all or name in config):
        key_x = '%s' % (name)
        fastk, fastd = talib.STOCHF(df[key_high], df[key_low], df[key_close],
            fastk_period=5, fastd_period=3, fastd_matype=0)
        df[key_x] = fastk - fastd
        key_xs.append(key_x)

    name = 'STOCHF-k'
    if key_high and (calc_all or name in config):
        key_x = '%s' % (name)
        fastk, fastd = talib.STOCHF(df[key_high], df[key_low], df[key_close],
            fastk_period=5, fastd_period=3, fastd_matype=0)
        df[key_x] = fastk
        key_xs.append(key_x)

    name = 'STOCHF-d'
    if key_high and (calc_all or name in config):
        key_x = '%s' % (name)
        fastk, fastd = talib.STOCHF(df[key_high], df[key_low], df[key_close],
            fastk_period=5, fastd_period=3, fastd_matype=0)
        df[key_x] = fastd
        key_xs.append(key_x)

    name = 'STOCHRSI'
    if calc_all or name in config:
        if name in config and 'period' in config[name]:
            tp = config[name]['period']
        else:
            tp = 14
        key_x = '%s_%s' % (name, tp)
        fastk, fastd = talib.STOCHRSI(df[key_close],
            timeperiod=tp, fastk_period=5, fastd_period=3, fastd_matype=0)
        df[key_x] = fastk - fastd
        key_xs.append(key_x)

    name = 'STOCHRSI-k'
    if calc_all or name in config:
        if name in config and 'period' in config[name]:
            tp = config[name]['period']
        else:
            tp = 14
        key_x = '%s_%s' % (name, tp)
        fastk, fastd = talib.STOCHRSI(df[key_close],
            timeperiod=tp, fastk_period=5, fastd_period=3, fastd_matype=0)
        df[key_x] = fastk
        key_xs.append(key_x)

    name = 'STOCHRSI-d'
    if calc_all or name in config:
        if name in config and 'period' in config[name]:
            tp = config[name]['period']
        else:
            tp = 14
        key_x = '%s_%s' % (name, tp)
        fastk, fastd = talib.STOCHRSI(df[key_close],
            timeperiod=tp, fastk_period=5, fastd_period=3, fastd_matype=0)
        df[key_x] = fastd
        key_xs.append(key_x)

    name = 'TRIX'
    if calc_all or name in config:
        if name in config and 'period' in config[name]:
            tp = config[name]['period']
        else:
            tp = 30
        key_x = '%s_%s' % (name, tp)
        df[key_x] = talib.TRIX(df[key_close], timeperiod=tp)
        key_xs.append(key_x)

    name = 'ULTOSC'
    if key_high and (calc_all or name in config):
        key_x = '%s' % (name)
        tp1 = 7
        tp2 = 14
        tp3 =28
        key_x = '%s_%s_%s_%s' % (name, tp1, tp2, tp3)
        df[key_x] = talib.ULTOSC(df[key_high], df[key_low], df[key_close],
            timeperiod1=tp1, timeperiod2=tp2, timeperiod3=tp3)
        key_xs.append(key_x)

    name = 'WILLR'
    if key_high and (calc_all or name in config):
        if name in config and 'period' in config[name]:
            tp = config[name]['period']
        else:
            tp = 14
        key_x = '%s_%s' % (name, tp)
        df[key_x] = talib.WILLR(df[key_high], df[key_low], df[key_close], timeperiod=tp)
        key_xs.append(key_x)

    return key_xs
