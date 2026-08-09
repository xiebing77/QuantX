import talib
from . import *

def calc_other_indicators(quoter, config, df, calc_all,
        key_open, key_high, key_low, key_close, key_volume, key_oi, prefix='', trial=None):
    key_xs = []

    name = 'ret'
    key_x = get_feature_key(name, config, prefix, calc_all, trial)
    if key_x:
        if trial:
            f_cfg = config[name]
            shift = trial.suggest_categorical(f'{key_x}_shift', f_cfg['shift'])
        else:
            shift = config.get(name, {}).get('shift', 1) if name in config else 1

        key_x = f'{key_x}_{shift}'
        df[key_x] = (df[key_close] / df[key_close].shift(shift) - 1) * 10000
        key_xs.append(key_x)

    name = 'ma-slope'
    key_x = get_feature_key(name, config, prefix, calc_all, trial)
    if key_high and key_x:
        if trial:
            f_cfg = config[name]
            window = trial.suggest_categorical(f'{key_x}_window', f_cfg['window'])
            shift = trial.suggest_categorical(f'{key_x}_shift',  f_cfg['shift'])

            trial.set_user_attr(f'{key_x}_params', {
                'window': window,
                'shift': shift
            })
        else:
            defaults = {'window': 20, 'shift': 3}
            f_cfg = config.get(name, {}) if name in config else {}
            window = f_cfg.get('window', defaults['window'])
            shift = f_cfg.get('shift', defaults['shift'])

        key_x = f'{key_x}_{window}_{shift}'
        ma = df[key_close].rolling(window).mean()
        pre_ma = ma.shift(shift)
        df[key_x] = (ma - pre_ma) / pre_ma / shift * 10000
        key_xs.append(key_x)

    name = 'CLV'
    key_x = get_feature_key(name, config, prefix, calc_all, trial)
    if key_high and key_x:
        df[key_x] = CLV(df[key_high], df[key_low], df[key_close])
        key_xs.append(key_x)

    name = 'CV'
    n, key_x = get_feature_1p(name, config, prefix, calc_all, trial, 10)
    if key_x:
        df[key_x] = CV(df[key_high], df[key_low], n)
        key_xs.append(key_x)

    name = 'DBCD'
    key_x = get_feature_key(name, config, prefix, calc_all, trial)
    if key_high and key_x:
        df[key_x] = DBCD(df[key_close])
        key_xs.append(key_x)

    name = 'PB'
    n, key_x = get_feature_1p(name, config, prefix, calc_all, trial, 20)
    if key_x:
        df[key_x] = PB(df[key_close], n)
        key_xs.append(key_x)

    name = 'BW'
    n, key_x = get_feature_1p(name, config, prefix, calc_all, trial, 20)
    if key_x:
        df[key_x] = BW(df[key_close], n)
        key_xs.append(key_x)

    name = 'KDJ'
    n, key_x = get_feature_1p(name, config, prefix, calc_all, trial, 9)
    if key_x:
        k, d, j = KDJ(df[key_high], df[key_low], df[key_close], n)
        df[key_x] = j
        key_xs.append(key_x)

    name = 'CMF'
    n, key_x = get_feature_1p(name, config, prefix, calc_all, trial, 21)
    if key_x:
        df[key_x] = CMF(df[key_high], df[key_low], df[key_close], df[key_volume], n)
        key_xs.append(key_x)

    name = 'CMF_intraday'
    n, key_x = get_feature_1p(name, config, prefix, calc_all, trial, 21)
    if key_x:
        df[key_x] = CMF_intraday(df[key_high], df[key_low], df[key_close], df[key_volume], n)
        key_xs.append(key_x)

    name = 'CR'
    n, key_x = get_feature_1p(name, config, prefix, calc_all, trial, 20)
    if key_x:
        df[key_x] = CR(df[key_high], df[key_low], df[key_close], n)
        key_xs.append(key_x)

    name = 'MassIndex'
    n, key_x = get_feature_1p(name, config, prefix, calc_all, trial, 9)
    if key_x:
        df[key_x] = MassIndex(df[key_high], df[key_low], n)
        key_xs.append(key_x)

    name = 'MassIndex_intraday'
    n, key_x = get_feature_1p(name, config, prefix, calc_all, trial, 9)
    if key_x:
        df[key_x] = MassIndex_intraday(df[key_high], df[key_low], n)
        key_xs.append(key_x)

    name = 'ElderPowerRatio'
    n, key_x = get_feature_1p(name, config, prefix, calc_all, trial, 13)
    if key_x:
        df[key_x] = ElderPowerRatio(df[key_high], df[key_low], df[key_close], n)
        key_xs.append(key_x)

    name = 'BarAmplitude'
    key_x = get_feature_key(name, config, prefix, calc_all, trial)
    if key_x:
        df[key_x] = BarAmplitude(df[key_high], df[key_low], df[key_close])
        key_xs.append(key_x)

    name = 'UOS'
    key_x = get_feature_key(name, config, prefix, calc_all, trial)
    if key_high and key_x:
        df[key_x] = UOS(df[key_high], df[key_low], df[key_close], M=7, N=14, O=28)
        key_xs.append(key_x)

    name = 'UOS_intraday'
    key_x = get_feature_key(name, config, prefix, calc_all, trial)
    if key_high and key_x:
        df[key_x] = UOS_intraday(df[key_high], df[key_low], df[key_close], M=7, N=14, O=28)
        key_xs.append(key_x)

    name = 'ASIR'
    n, key_x = get_feature_1p(name, config, prefix, calc_all, trial, 20)
    if key_x:
        df[key_x] = ASIR(df[key_open], df[key_high], df[key_low], df[key_close], n)
        key_xs.append(key_x)

    name = 'ASIR_intraday'
    n, key_x = get_feature_1p(name, config, prefix, calc_all, trial, 20)
    if key_x:
        df[key_x] = ASIR_intraday(df[key_open], df[key_high], df[key_low], df[key_close], n)
        key_xs.append(key_x)

    name = 'UI'
    n, key_x = get_feature_1p(name, config, prefix, calc_all, trial, 10)
    if key_x:
        df[key_x] = UI(df[key_close], n)
        key_xs.append(key_x)

    name = 'Hurst'
    n, key_x = get_feature_1p(name, config, prefix, calc_all, trial, 10)
    if key_x:
        df[key_x] = Hurst(df[key_close], n)
        key_xs.append(key_x)

    name = 'BIAS_C'
    n, key_x = get_feature_1p(name, config, prefix, calc_all, trial, 13)
    if key_x:
        df[key_x] = BIAS(df[key_close], n)
        key_xs.append(key_x)

    name = 'BIAS_V'
    n, key_x = get_feature_1p(name, config, prefix, calc_all, trial, 13)
    if key_x:
        df[key_x] = BIAS(df[key_volume], n)
        key_xs.append(key_x)

    name = 'BIAS_E_C'
    n, key_x = get_feature_1p(name, config, prefix, calc_all, trial, 13)
    if key_x:
        df[key_x] = BIAS_E(df[key_close], n)
        key_xs.append(key_x)

    name = 'BIAS_E_V'
    n, key_x = get_feature_1p(name, config, prefix, calc_all, trial, 13)
    if key_x:
        df[key_x] = BIAS_E(df[key_volume], n)
        key_xs.append(key_x)

    name = 'nmBIAS_C'
    n, m, key_x = get_feature_2p(name, config, prefix, calc_all, trial, 10, 30)
    if key_x:
        df[key_x] = nmBIAS(df[key_close], n, m)
        key_xs.append(key_x)

    name = 'nmBIAS_V'
    n, m, key_x = get_feature_2p(name, config, prefix, calc_all, trial, 10, 30)
    if key_x:
        df[key_x] = nmBIAS(df[key_volume], n, m)
        key_xs.append(key_x)

    name = 'nmBIAS_E_C'
    n, m, key_x = get_feature_2p(name, config, prefix, calc_all, trial, 10, 30)
    if key_x:
        df[key_x] = nmBIAS_E(df[key_close], n, m)
        key_xs.append(key_x)

    name = 'nmBIAS_E_V'
    n, m, key_x = get_feature_2p(name, config, prefix, calc_all, trial, 10, 30)
    if key_x:
        df[key_x] = nmBIAS_E(df[key_volume], n, m)
        key_xs.append(key_x)

    name = 'OI_diff_ratio'
    n, key_x = get_feature_1p(name, config, prefix, calc_all, trial, 20)
    if key_x:
        df[key_x] = OI_diff_ratio(df[key_oi], n)
        key_xs.append(key_x)

    name = 'OI_diff_ratio_intraday'
    n, key_x = get_feature_1p(name, config, prefix, calc_all, trial, 20)
    if key_x:
        df[key_x] = OI_diff_ratio_intraday(df[key_oi], n)
        key_xs.append(key_x)

    name = 'OI_diff_ratio_atr'
    n, key_x = get_feature_1p(name, config, prefix, calc_all, trial, 20)
    if key_x:
        df[key_x] = OI_diff_ratio_atr(df[key_oi], df[key_high], df[key_low], n)
        key_xs.append(key_x)

    name = 'OIV'
    key_x = get_feature_key(name, config, prefix, calc_all, trial)
    if key_high and key_x:
        df[key_x] = OIV(df[key_volume], df[key_oi])
        key_xs.append(key_x)

    name = 'VOI'
    key_x = get_feature_key(name, config, prefix, calc_all, trial)
    if key_high and key_x:
        df[key_x] = VOI(df[key_volume], df[key_oi])
        key_xs.append(key_x)

    name = 'MA-EMA'
    tp, key_x = get_feature_1p(name, config, prefix, calc_all, trial, 16)
    if key_x:
        a = talib.MA(df[key_close], timeperiod=tp)
        b = talib.EMA(df[key_close], timeperiod=tp)
        df[key_x] = a / b - 1
        key_xs.append(key_x)

    '''
    name = 'EMA-DEMA'
    tp, key_x = get_feature_1p(name, config, prefix, calc_all, trial, 16)
    if key_x:
        a = talib.EMA(df[key_close], timeperiod=tp)
        b = talib.DEMA(df[key_close], timeperiod=tp)
        df[key_x] = a / b - 1
        key_xs.append(key_x)
    '''

    name = 'KAMA-EMA'
    tp, key_x = get_feature_1p(name, config, prefix, calc_all, trial, 16)
    if key_x:
        a = talib.KAMA(df[key_close], timeperiod=tp)
        b = talib.EMA(df[key_close], timeperiod=tp)
        df[key_x] = a / b - 1
        key_xs.append(key_x)
    '''
    name = 'MAMA-EMA'
    if calc_all or name in config:
        if name in config and 'period' in config[name]:
            tp = config[name]['period']
        else:
            fl = 0
            sl = 0
        key_x = '%s_%s_%s' % (name, fl, sl)
        a = talib.MAMA(df[key_close], fastlimit=fl, slowlimit=sl)
        b = talib.EMA(df[key_close], timeperiod=tp)
        df[key_x] = a / b - 1
        key_xs.append(key_x)
    '''
    name = 'WMA-EMA'
    tp, key_x = get_feature_1p(name, config, prefix, calc_all, trial, 16)
    if key_x:
        a = talib.WMA(df[key_close], timeperiod=tp)
        b = talib.EMA(df[key_close], timeperiod=tp)
        df[key_x] = a / b - 1
        key_xs.append(key_x)
    '''
    name = 'SAR-MIDPRICE'
    tp, key_x = get_feature_1p(name, config, prefix, calc_all, trial, 16)
    if key_x:
        a = talib.SAR(df[key_high], df[key_low], acceleration=0, maximum=0)
        b = talib.MIDPRICE(df[key_high], df[key_low], timeperiod=tp)
        df[key_x] = a / b - 1
        key_xs.append(key_x)
    '''

    return key_xs

