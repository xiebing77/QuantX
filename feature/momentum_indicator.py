import talib

def calc_momentum_indicators(quoter, config, kdf, calc_all=False):
    key_xs = []
    key_open = quoter.kline_key_open
    key_close = quoter.kline_key_close
    key_high = quoter.kline_key_high
    key_low = quoter.kline_key_low
    key_volume = quoter.kline_key_volume

    name = 'ADX'
    if calc_all or name in config:
        if name in config and 'period' in config[name]:
            tp = config[name]['period']
        else:
            tp = 14
        key_x = '%s_%s' % (name, tp)
        kdf[key_x] = talib.ADX(kdf[key_high], kdf[key_low], kdf[key_close], timeperiod=tp)
        key_xs.append(key_x)

    name = 'ADXR'
    if calc_all or name in config:
        if name in config and 'period' in config[name]:
            tp = config[name]['period']
        else:
            tp = 14
        key_x = '%s_%s' % (name, tp)
        kdf[key_x] = talib.ADXR(kdf[key_high], kdf[key_low], kdf[key_close], timeperiod=tp)
        key_xs.append(key_x)

    name = 'APO'
    if calc_all or name in config:
        key_x = '%s' % (name)
        fp = 12
        sp = 26
        key_x = '%s_%s_%s' % (name, fp, sp)
        kdf[key_x] = talib.APO(kdf[key_close], fastperiod=fp, slowperiod=sp, matype=0)
        key_xs.append(key_x)

    name = 'AROONOSC'
    if calc_all or name in config:
        if name in config and 'period' in config[name]:
            tp = config[name]['period']
        else:
            tp = 14
        key_x = '%s_%s' % (name, tp)
        kdf[key_x] = talib.AROONOSC(kdf[key_high], kdf[key_low], timeperiod=tp)
        key_xs.append(key_x)

    name = 'BOP'
    if calc_all or name in config:
        key_x = '%s' % (name)
        kdf[key_x] = talib.BOP(kdf[key_open], kdf[key_high], kdf[key_low], kdf[key_close])
        key_xs.append(key_x)

    name = 'CCI'
    if calc_all or name in config:
        if name in config and 'period' in config[name]:
            tp = config[name]['period']
        else:
            tp = 14
        key_x = '%s_%s' % (name, tp)
        kdf[key_x] = talib.CCI(kdf[key_high], kdf[key_low], kdf[key_close], timeperiod=tp)
        key_xs.append(key_x)

    name = 'CMO'
    if calc_all or name in config:
        if name in config and 'period' in config[name]:
            tp = config[name]['period']
        else:
            tp = 14
        key_x = '%s_%s' % (name, tp)
        kdf[key_x] = talib.CMO(kdf[key_close], timeperiod=tp)
        key_xs.append(key_x)

    name = 'DX'
    if calc_all or name in config:
        if name in config and 'period' in config[name]:
            tp = config[name]['period']
        else:
            tp = 14
        key_x = '%s_%s' % (name, tp)
        kdf[key_x] = talib.DX(kdf[key_high], kdf[key_low], kdf[key_close], timeperiod=tp)
        key_xs.append(key_x)

    name = 'MACD'
    if calc_all or name in config:
        fastperiod = 12
        slowperiod = 26
        signalperiod = 9
        key_x = '%s_%s' % (name, tp)
        macd, macdsignal, macdhist = talib.MACD(kdf[key_close],
            fastperiod=fastperiod, slowperiod=slowperiod, signalperiod=signalperiod)
        kdf[key_x] = macdhist
        key_xs.append(key_x)

    name = 'MACDEXT'
    if calc_all or name in config:
        fastperiod = 12
        slowperiod = 26
        signalperiod = 9
        key_x = '%s_%s' % (name, tp)
        macd, macdsignal, macdhist = talib.MACDEXT(kdf[key_close],
            fastperiod=fastperiod, fastmatype=0, slowperiod=slowperiod, slowmatype=0,
            signalperiod=signalperiod, signalmatype=0)
        kdf[key_x] = macdhist
        key_xs.append(key_x)

    name = 'MACDFIX'
    if calc_all or name in config:
        signalperiod = 9
        key_x = '%s_%s' % (name, tp)
        macd, macdsignal, macdhist = talib.MACDFIX(kdf[key_close], signalperiod=signalperiod)
        kdf[key_x] = macdhist
        key_xs.append(key_x)

    name = 'MFI'
    if calc_all or name in config:
        key_x = '%s' % (name)
        kdf[key_x] = talib.MFI(kdf[key_open], kdf[key_high], kdf[key_low], kdf[key_volume])
        key_xs.append(key_x)

    name = 'MINUS_DI'
    if calc_all or name in config:
        if name in config and 'period' in config[name]:
            tp = config[name]['period']
        else:
            tp = 14
        key_x = '%s_%s' % (name, tp)
        kdf[key_x] = talib.MINUS_DI(kdf[key_high], kdf[key_low], kdf[key_close], timeperiod=tp)
        key_xs.append(key_x)

    name = 'MINUS_DM'
    if calc_all or name in config:
        if name in config and 'period' in config[name]:
            tp = config[name]['period']
        else:
            tp = 14
        key_x = '%s_%s' % (name, tp)
        kdf[key_x] = talib.MINUS_DM(kdf[key_high], kdf[key_low], timeperiod=tp)
        key_xs.append(key_x)

    name = 'MOM'
    if calc_all or name in config:
        if name in config and 'period' in config[name]:
            tp = config[name]['period']
        else:
            tp = 10
        key_x = '%s_%s' % (name, tp)
        kdf[key_x] = talib.MOM(kdf[key_close], timeperiod=tp)
        key_xs.append(key_x)

    name = 'PLUS_DI'
    if calc_all or name in config:
        if name in config and 'period' in config[name]:
            tp = config[name]['period']
        else:
            tp = 14
        key_x = '%s_%s' % (name, tp)
        kdf[key_x] = talib.PLUS_DI(kdf[key_high], kdf[key_low], kdf[key_close], timeperiod=tp)
        key_xs.append(key_x)

    name = 'PLUS_DM'
    if calc_all or name in config:
        if name in config and 'period' in config[name]:
            tp = config[name]['period']
        else:
            tp = 14
        key_x = '%s_%s' % (name, tp)
        kdf[key_x] = talib.PLUS_DM(kdf[key_high], kdf[key_low], timeperiod=tp)

    name = 'PPO'
    if calc_all or name in config:
        key_x = '%s' % (name)
        fp = 12
        sp = 26
        key_x = '%s_%s_%s' % (name, fp, sp)
        kdf[key_x] = talib.PPO(kdf[key_close], fastperiod=fp, slowperiod=sp, matype=0)
        key_xs.append(key_x)

    name = 'ROC'
    if calc_all or name in config:
        if name in config and 'period' in config[name]:
            tp = config[name]['period']
        else:
            tp = 10
        key_x = '%s_%s' % (name, tp)
        kdf[key_x] = talib.ROC(kdf[key_close], timeperiod=tp)
        key_xs.append(key_x)

    name = 'ROCP'
    if calc_all or name in config:
        if name in config and 'period' in config[name]:
            tp = config[name]['period']
        else:
            tp = 10
        key_x = '%s_%s' % (name, tp)
        kdf[key_x] = talib.ROCP(kdf[key_close], timeperiod=tp)
        key_xs.append(key_x)

    name = 'ROCR'
    if calc_all or name in config:
        if name in config and 'period' in config[name]:
            tp = config[name]['period']
        else:
            tp = 10
        key_x = '%s_%s' % (name, tp)
        kdf[key_x] = talib.ROCR(kdf[key_close], timeperiod=tp)
        key_xs.append(key_x)

    name = 'ROCR100'
    if calc_all or name in config:
        if name in config and 'period' in config[name]:
            tp = config[name]['period']
        else:
            tp = 10
        key_x = '%s_%s' % (name, tp)
        kdf[key_x] = talib.ROCR100(kdf[key_close], timeperiod=tp)
        key_xs.append(key_x)

    name = 'RSI'
    if calc_all or name in config:
        if name in config and 'period' in config[name]:
            tp = config[name]['period']
        else:
            tp = 14
        key_x = '%s_%s' % (name, tp)
        kdf[key_x] = talib.RSI(kdf[key_close], timeperiod=tp)
        key_xs.append(key_x)

    name = 'STOCH'
    if calc_all or name in config:
        key_x = '%s_%s' % (name, tp)
        slowk, slowd = talib.STOCH(kdf[key_high], kdf[key_low], kdf[key_close],
            fastk_period=5, slowk_period=3, slowk_matype=0, slowd_period=3, slowd_matype=0)
        kdf[key_x] = slowk - slowd
        key_xs.append(key_x)

    name = 'STOCHF'
    if calc_all or name in config:
        key_x = '%s_%s' % (name, tp)
        fastk, fastd = talib.STOCHF(kdf[key_high], kdf[key_low], kdf[key_close],
            fastk_period=5, fastd_period=3, fastd_matype=0)
        kdf[key_x] = fastk - fastd
        key_xs.append(key_x)

    name = 'STOCHRSI'
    if calc_all or name in config:
        if name in config and 'period' in config[name]:
            tp = config[name]['period']
        else:
            tp = 14
        key_x = '%s_%s' % (name, tp)
        fastk, fastd = talib.STOCHRSI(kdf[key_close],
            timeperiod=tp, fastk_period=5, fastd_period=3, fastd_matype=0)
        kdf[key_x] = fastk - fastd
        key_xs.append(key_x)

    name = 'TRIX'
    if calc_all or name in config:
        if name in config and 'period' in config[name]:
            tp = config[name]['period']
        else:
            tp = 30
        key_x = '%s_%s' % (name, tp)
        kdf[key_x] = talib.TRIX(kdf[key_close], timeperiod=tp)
        key_xs.append(key_x)

    name = 'ULTOSC'
    if calc_all or name in config:
        key_x = '%s' % (name)
        tp1 = 7
        tp2 = 14
        tp3 =28
        key_x = '%s_%s_%s_%s' % (name, tp1, tp2, tp3)
        kdf[key_x] = talib.ULTOSC(kdf[key_high], kdf[key_low], kdf[key_close],
            timeperiod1=tp1, timeperiod2=tp2, timeperiod3=tp3)
        key_xs.append(key_x)

    name = 'WILLR'
    if calc_all or name in config:
        if name in config and 'period' in config[name]:
            tp = config[name]['period']
        else:
            tp = 14
        key_x = '%s_%s' % (name, tp)
        kdf[key_x] = talib.WILLR(kdf[key_high], kdf[key_low], kdf[key_close], timeperiod=tp)
        key_xs.append(key_x)

    return key_xs
