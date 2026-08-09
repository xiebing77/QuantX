import talib
from . import *


def calc_momentum_indicators(quoter, config, df, calc_all,
        key_open, key_high, key_low, key_close, key_volume, key_oi, prefix='', trial=None):
    key_xs = []

    name = 'ADX'
    tp, key_x = get_feature_1p(name, config, prefix, calc_all, trial, 14)
    if key_x:
        df[key_x] = talib.ADX(df[key_high], df[key_low], df[key_close], timeperiod=tp)
        key_xs.append(key_x)

    name = 'DI_diff'
    tp, key_x = get_feature_1p(name, config, prefix, calc_all, trial, 14)
    if key_x:
        df[key_x] = DI_diff(df[key_high], df[key_low], df[key_close], period=tp)
        key_xs.append(key_x)

    name = 'ADXR'
    tp, key_x = get_feature_1p(name, config, prefix, calc_all, trial, 14)
    if key_x:
        df[key_x] = talib.ADXR(df[key_high], df[key_low], df[key_close], timeperiod=tp)
        key_xs.append(key_x)

    name = 'APO'
    fp, sp, key_x = get_feature_2p(name, config, prefix, calc_all, trial, 12, 26)
    if key_x:
        df[key_x] = talib.APO(df[key_close], fastperiod=fp, slowperiod=sp, matype=0)
        key_xs.append(key_x)

    name = 'AROONOSC'
    tp, key_x = get_feature_1p(name, config, prefix, calc_all, trial, 14)
    if key_x:
        df[key_x] = talib.AROONOSC(df[key_high], df[key_low], timeperiod=tp)
        key_xs.append(key_x)

    name = 'BOP'
    key_x = get_feature_key(name, config, prefix, calc_all, trial)
    if key_high and key_x:
        key_x = f'{prefix}{name}'
        df[key_x] = talib.BOP(df[key_open], df[key_high], df[key_low], df[key_close])
        key_xs.append(key_x)

    name = 'CCI'
    tp, key_x = get_feature_1p(name, config, prefix, calc_all, trial, 14)
    if key_x:
        df[key_x] = talib.CCI(df[key_high], df[key_low], df[key_close], timeperiod=tp)
        key_xs.append(key_x)

    name = 'CMO'
    tp, key_x = get_feature_1p(name, config, prefix, calc_all, trial, 14)
    if key_x:
        df[key_x] = talib.CMO(df[key_close], timeperiod=tp)
        key_xs.append(key_x)

    name = 'DX'
    tp, key_x = get_feature_1p(name, config, prefix, calc_all, trial, 14)
    if key_x:
        df[key_x] = talib.DX(df[key_high], df[key_low], df[key_close], timeperiod=tp)
        key_xs.append(key_x)
    '''
    name = 'MACD'
    if calc_all or name in config:
        fastperiod = 12
        slowperiod = 26
        signalperiod = 9
        key_x = f'{prefix}{name}_{tp}'
        macd, macdsignal, macdhist = talib.MACD(df[key_close],
            fastperiod=fastperiod, slowperiod=slowperiod, signalperiod=signalperiod)
        df[key_x] = macdhist
        key_xs.append(key_x)

    name = 'MACDEXT'
    if calc_all or name in config:
        fastperiod = 12
        slowperiod = 26
        signalperiod = 9
        key_x = f'{prefix}{name}_{tp}'
        macd, macdsignal, macdhist = talib.MACDEXT(df[key_close],
            fastperiod=fastperiod, fastmatype=0, slowperiod=slowperiod, slowmatype=0,
            signalperiod=signalperiod, signalmatype=0)
        df[key_x] = macdhist
        key_xs.append(key_x)

    name = 'MACDFIX'
    if calc_all or name in config:
        signalperiod = 9
        key_x = f'{prefix}{name}_{tp}'
        macd, macdsignal, macdhist = talib.MACDFIX(df[key_close], signalperiod=signalperiod)
        df[key_x] = macdhist
        key_xs.append(key_x)
    '''
    name = 'MFI'
    tp, key_x = get_feature_1p(name, config, prefix, calc_all, trial, 14)
    if key_x:
        df[key_x] = MFI(df[key_high], df[key_low], df[key_close], df[key_volume], tp)
        key_xs.append(key_x)

    name = 'MFI_intraday'
    tp, key_x = get_feature_1p(name, config, prefix, calc_all, trial, 14)
    if key_x:
        df[key_x] = MFI_intraday(df[key_high], df[key_low], df[key_close], df[key_volume], tp)
        key_xs.append(key_x)

    name = 'MINUS_DI'
    tp, key_x = get_feature_1p(name, config, prefix, calc_all, trial, 14)
    if key_x:
        df[key_x] = talib.MINUS_DI(df[key_high], df[key_low], df[key_close], timeperiod=tp)
        key_xs.append(key_x)

    name = 'MINUS_DM'
    tp, key_x = get_feature_1p(name, config, prefix, calc_all, trial, 14)
    if key_x:
        df[key_x] = talib.MINUS_DM(df[key_high], df[key_low], timeperiod=tp)
        key_xs.append(key_x)

    name = 'MOM'
    tp, key_x = get_feature_1p(name, config, prefix, calc_all, trial, 10)
    if key_x:
        df[key_x] = talib.MOM(df[key_close], timeperiod=tp)
        key_xs.append(key_x)

    name = 'PLUS_DI'
    tp, key_x = get_feature_1p(name, config, prefix, calc_all, trial, 14)
    if key_x:
        df[key_x] = talib.PLUS_DI(df[key_high], df[key_low], df[key_close], timeperiod=tp)
        key_xs.append(key_x)

    name = 'PLUS_DM'
    tp, key_x = get_feature_1p(name, config, prefix, calc_all, trial, 14)
    if key_x:
        df[key_x] = talib.PLUS_DM(df[key_high], df[key_low], timeperiod=tp)
        key_xs.append(key_x)

    name = 'PPO'
    fp, sp, key_x = get_feature_2p(name, config, prefix, calc_all, trial, 12, 26)
    if key_x:
        df[key_x] = talib.PPO(df[key_close], fastperiod=fp, slowperiod=sp, matype=0)
        key_xs.append(key_x)

    name = 'ROC'
    tp, key_x = get_feature_1p(name, config, prefix, calc_all, trial, 10)
    if key_x:
        df[key_x] = talib.ROC(df[key_close], timeperiod=tp)
        key_xs.append(key_x)

    name = 'ROCP'
    tp, key_x = get_feature_1p(name, config, prefix, calc_all, trial, 10)
    if key_x:
        df[key_x] = talib.ROCP(df[key_close], timeperiod=tp)
        key_xs.append(key_x)

    name = 'ROCR'
    tp, key_x = get_feature_1p(name, config, prefix, calc_all, trial, 10)
    if key_x:
        df[key_x] = talib.ROCR(df[key_close], timeperiod=tp)
        key_xs.append(key_x)

    name = 'ROCR100'
    tp, key_x = get_feature_1p(name, config, prefix, calc_all, trial, 10)
    if key_x:
        df[key_x] = talib.ROCR100(df[key_close], timeperiod=tp)
        key_xs.append(key_x)

    name = 'RSI'
    tp, key_x = get_feature_1p(name, config, prefix, calc_all, trial, 14)
    if key_x:
        df[key_x] = talib.RSI(df[key_close], timeperiod=tp)
        key_xs.append(key_x)

    name = 'STOCH'
    key_x = get_feature_key(name, config, prefix, calc_all, trial)
    if key_x:
        if trial:
            f_cfg = config[name]
            fastk_period = trial.suggest_categorical(f'{key_x}_fastk_period', f_cfg['fastk_period'])
            slowk_period = trial.suggest_categorical(f'{key_x}_slowk_period', f_cfg['slowk_period'])
            slowk_matype = trial.suggest_categorical(f'{key_x}_slowk_matype', f_cfg['slowk_matype'])

            # 约束2：D线不能太快（否则K线和D线几乎重合
            # slowd只能选 >= 2
            valid_slowd = [v for v in f_cfg['slowd_period'] if v >= 2]
            slowd_period = trial.suggest_categorical(f'{key_x}_slowd_period', valid_slowd)
            slowd_matype = trial.suggest_categorical(f'{key_x}_slowd_matype', f_cfg['slowd_matype'])

            # 约束检查：不符合则剪枝
            # 约束1：K线原周期 >= 平滑周期
            # slowk只能选 <= fastk的值
            import optuna
            if fastk_period < slowk_period:
                raise optuna.TrialPruned("fastk_period < slowk_period")
            # 约束3：如果原周期很短（<5），必须用SMA平滑
            # EMA在极短周期下不稳定
            if fastk_period < 5 and slowk_matype != 0:
                raise optuna.TrialPruned("short period requires SMA")

            # 记录参数（便于事后分析）
            trial.set_user_attr(f'{key_x}_params', {
                'fastk_period': fastk_period,
                'slowk_period': slowk_period,
                'slowk_matype': slowk_matype,
                'slowd_period': slowd_period,
                'slowd_matype': slowd_matype
            })
        else:
            defaults = {'fastk_period': 5, 'slowk_period': 3,
                'slowk_matype': 0, 'slowd_period': 3, 'slowd_matype': 0}
            f_cfg = config.get(name) if name in config else {}
            fastk_period = f_cfg.get('fastk_period', defaults['fastk_period'])
            slowk_period = f_cfg.get('slowk_period', defaults['slowk_period'])
            slowk_matype = f_cfg.get('slowk_matype', defaults['slowk_matype'])
            slowd_period = f_cfg.get('slowd_period', defaults['slowd_period'])
            slowd_matype = f_cfg.get('slowd_matype', defaults['slowd_matype'])

        slowk, slowd = talib.STOCH(df[key_high], df[key_low], df[key_close],
            fastk_period=fastk_period,
            slowk_period=slowk_period, slowk_matype=slowk_matype,
            slowd_period=slowd_period, slowd_matype=slowd_matype)
        key_x = f'{key_x}_{fastk_period}_{slowk_period}_{slowk_matype}_{slowd_period}_{slowd_matype}'
        df[key_x] = slowk - slowd
        key_xs.append(key_x)

    '''
    name = 'STOCH-k'
    if key_high and (calc_all or name in config):
        key_x = f'{prefix}{name}'
        slowk, slowd = talib.STOCH(df[key_high], df[key_low], df[key_close],
            fastk_period=5, slowk_period=3, slowk_matype=0, slowd_period=3, slowd_matype=0)
        df[key_x] = slowk
        key_xs.append(key_x)

    name = 'STOCH-d'
    if key_high and (calc_all or name in config):
        key_x = f'{prefix}{name}'
        slowk, slowd = talib.STOCH(df[key_high], df[key_low], df[key_close],
            fastk_period=5, slowk_period=3, slowk_matype=0, slowd_period=3, slowd_matype=0)
        df[key_x] = slowd
        key_xs.append(key_x)
    '''
    name = 'STOCHF'
    key_x = get_feature_key(name, config, prefix, calc_all, trial)
    if key_x:
        if trial:
            f_cfg = config[name]
            fastk_period = trial.suggest_categorical(f'{key_x}_fastk_period', f_cfg['fastk_period'])

            # 约束：d线周期 >= 2，避免K/D线几乎重合
            valid_fastd = [v for v in f_cfg['fastd_period'] if v >= 2]
            fastd_period = trial.suggest_categorical(f'{key_x}_fastd_period', valid_fastd)
            fastd_matype = trial.suggest_categorical(f'{key_x}_fastd_matype', f_cfg['fastd_matype'])

            trial.set_user_attr(f'{key_x}_params', {
                'fastk_period': fastk_period,
                'fastd_period': fastd_period,
                'fastd_matype': fastd_matype
            })
        else:
            defaults = {'fastk_period': 5, 'fastd_period': 3, 'fastd_matype': 0}
            f_cfg = config.get(name, {}) if name in config else {}
            fastk_period = f_cfg.get('fastk_period', defaults['fastk_period'])
            fastd_period = f_cfg.get('fastd_period', defaults['fastd_period'])
            fastd_matype = f_cfg.get('fastd_matype', defaults['fastd_matype'])

        fastk, fastd = talib.STOCHF(
            df[key_high], df[key_low], df[key_close],
            fastk_period=fastk_period,
            fastd_period=fastd_period,
            fastd_matype=fastd_matype)
        key_x = f'{key_x}_{fastk_period}_{fastd_period}_{fastd_matype}'
        df[key_x] = fastk - fastd
        key_xs.append(key_x)
    '''
    name = 'STOCHF-k'
    if key_high and (calc_all or name in config):
        key_x = f'{prefix}{name}'
        fastk, fastd = talib.STOCHF(df[key_high], df[key_low], df[key_close],
            fastk_period=5, fastd_period=3, fastd_matype=0)
        df[key_x] = fastk
        key_xs.append(key_x)

    name = 'STOCHF-d'
    if key_high and (calc_all or name in config):
        key_x = f'{prefix}{name}'
        fastk, fastd = talib.STOCHF(df[key_high], df[key_low], df[key_close],
            fastk_period=5, fastd_period=3, fastd_matype=0)
        df[key_x] = fastd
        key_xs.append(key_x)
    '''
    name = 'STOCHRSI'
    key_x = get_feature_key(name, config, prefix, calc_all, trial)
    if key_x:
        if trial:
            f_cfg = config[name]
            timeperiod   = trial.suggest_categorical(f'{key_x}_timeperiod',   f_cfg['timeperiod'])
            fastk_period = trial.suggest_categorical(f'{key_x}_fastk_period', f_cfg['fastk_period'])

            # 约束：d线周期 >= 2
            valid_fastd = [v for v in f_cfg['fastd_period'] if v >= 2]
            fastd_period = trial.suggest_categorical(f'{key_x}_fastd_period', valid_fastd)
            fastd_matype = trial.suggest_categorical(f'{key_x}_fastd_matype', f_cfg['fastd_matype'])

            trial.set_user_attr(f'{key_x}_params', {
                'timeperiod': timeperiod,
                'fastk_period': fastk_period,
                'fastd_period': fastd_period,
                'fastd_matype': fastd_matype
            })
        else:
            defaults = {'timeperiod': 14, 'fastk_period': 5, 'fastd_period': 3, 'fastd_matype': 0}
            f_cfg = config.get(name, {}) if name in config else {}
            timeperiod = f_cfg.get('timeperiod', defaults['timeperiod'])
            fastk_period = f_cfg.get('fastk_period', defaults['fastk_period'])
            fastd_period = f_cfg.get('fastd_period', defaults['fastd_period'])
            fastd_matype = f_cfg.get('fastd_matype', defaults['fastd_matype'])

        fastk, fastd = talib.STOCHRSI(
            df[key_close],
            timeperiod=timeperiod,
            fastk_period=fastk_period,
            fastd_period=fastd_period,
            fastd_matype=fastd_matype)
        key_x = f'{key_x}_{timeperiod}_{fastk_period}_{fastd_period}_{fastd_matype}'
        df[key_x] = fastk - fastd
        key_xs.append(key_x)
    '''
    name = 'STOCHRSI-k'
    if calc_all or name in config:
        if name in config and 'period' in config[name]:
            tp = config[name]['period']
        else:
            tp = 14
        key_x = f'{prefix}{name}_{tp}'
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
        key_x = f'{prefix}{name}_{tp}'
        fastk, fastd = talib.STOCHRSI(df[key_close],
            timeperiod=tp, fastk_period=5, fastd_period=3, fastd_matype=0)
        df[key_x] = fastd
        key_xs.append(key_x)
    '''
    name = 'TRIX'
    tp, key_x = get_feature_1p(name, config, prefix, calc_all, trial, 30)
    if key_x:
        df[key_x] = talib.TRIX(df[key_close], timeperiod=tp)
        key_xs.append(key_x)

    name = 'ULTOSC'
    key_x = get_feature_key(name, config, prefix, calc_all, trial)
    if key_x:
        if trial:
            f_cfg = config[name]
            base = trial.suggest_categorical(f'{key_x}_base', f_cfg['base_period'])
            # 固定比例，不需要动态 choices，也不需要剪枝
            tp1 = base
            tp2 = base * 2
            tp3 = base * 4
            trial.set_user_attr(f'{key_x}_params', {'base': base})
        else:
            defaults = {'timeperiod1': 7, 'timeperiod2': 14, 'timeperiod3': 28}
            f_cfg = config.get(name, {}) if name in config else {}
            tp1 = f_cfg.get('timeperiod1', defaults['timeperiod1'])
            tp2 = f_cfg.get('timeperiod2', defaults['timeperiod2'])
            tp3 = f_cfg.get('timeperiod3', defaults['timeperiod3'])

        key_x = f'{key_x}_{tp1}_{tp2}_{tp3}'
        df[key_x] = talib.ULTOSC(
            df[key_high], df[key_low], df[key_close],
            timeperiod1=tp1, timeperiod2=tp2, timeperiod3=tp3)
        key_xs.append(key_x)

    name = 'WILLR'
    tp, key_x = get_feature_1p(name, config, prefix, calc_all, trial, 14)
    if key_x:
        df[key_x] = talib.WILLR(df[key_high], df[key_low], df[key_close], timeperiod=tp)
        key_xs.append(key_x)

    return key_xs
