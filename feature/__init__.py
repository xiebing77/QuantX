import numpy as np
import pandas as pd


def get_feature_key(name, config, prefix, calc_all, trial):
    key_x = f'{prefix}{name}'
    if calc_all:
        return f'{prefix}{name}'

    if not trial:
        if not name in config:
            return ''
        return f'{prefix}{name}'

    if name in config:
        f_cfg = config[name]
    #elif ' '+name in config:
    #    f_cfg = config[' '+name]
    else:
        return ''

    use_switch = trial.suggest_categorical('use_'+key_x, [True, False])
    if not use_switch:
        return ''
    return f'{prefix}{name}'


def get_feature_1p0(name, config, prefix, calc_all, trial, tp):
    if calc_all:
        return tp, f'{prefix}{name}_{tp}'

    if not trial:
        if not name in config:
            return np.nan, ''
        if 'period' in config[name]:
            tp = config[name]['period']
        return tp, f'{prefix}{name}_{tp}'

    if name in config:
        f_cfg = config[name]
    elif ' '+name in config:
        f_cfg = config[' '+name]
    else:
        return np.nan, ''

    use_switch = trial.suggest_categorical('use_'+name, [True, False])
    if not use_switch:
        return np.nan, ''

    if not 'range' in f_cfg:
        return tp, f'{prefix}{name}_{tp}'
    r_cfg = f_cfg['range']
    tp = trial.suggest_int(name, r_cfg[0], r_cfg[1], step=r_cfg[2])
    return tp, f'{prefix}{name}'


def get_feature_1p(name, config, prefix, calc_all, trial, tp):
    key_x = f'{prefix}{name}'
    if calc_all:
        return tp, f'{prefix}{name}_{tp}'

    if not trial:
        if not name in config:
            return np.nan, ''
        if 'period' in config[name]:
            tp = config[name]['period']
        return tp, f'{prefix}{name}_{tp}'

    if name in config:
        f_cfg = config[name]
    #elif ' '+name in config:
    #    f_cfg = config[' '+name]
    else:
        return np.nan, ''
        f_cfg = None

    use_switch = trial.suggest_categorical('use_'+key_x, [True, False])
    if not use_switch:
        return np.nan, ''

    if f_cfg and 'range' in f_cfg:
        r_cfg = f_cfg['range']
        start = r_cfg[0]
        stop  = r_cfg[1]
        step  = r_cfg[2]
    else:
        start = tp
        stop  = tp * 4
        step  = tp

    tp = trial.suggest_int(key_x, start, stop, step=step)
    return tp, f'{prefix}{name}'


def get_feature_2p(name, config, prefix, calc_all, trial, fp, sp):
    key_x = f'{prefix}{name}'
    if calc_all:
        return fp, sp, f'{prefix}{name}_{fp}_{sp}'

    if not trial:
        if not name in config:
            return np.nan, np.nan, ''
        if 'periods' in config[name]:
            fp = config[name]['periods'][0]
            sp = config[name]['periods'][1]
        return fp, sp, f'{prefix}{name}_{fp}_{sp}'

    if name in config:
        f_cfg = config[name]
    #elif ' '+name in config:
    #    f_cfg = config[' '+name]
    else:
        return np.nan, np.nan, ''

    use_switch = trial.suggest_categorical('use_'+key_x, [True, False])
    if not use_switch:
        return np.nan, np.nan, ''

    if not  'fast_range' in f_cfg or not 'k_range' in f_cfg:
        return fp, sp, f'{prefix}{name}_{fp}_{sp}'

    fr_cfg = f_cfg['fast_range']
    start = fr_cfg[0]
    stop  = fr_cfg[1]
    step  = fr_cfg[2]
    fp = trial.suggest_int(key_x+'_fast', start, stop, step=step)

    kr_cfg = f_cfg['k_range']
    start = kr_cfg[0]
    stop  = kr_cfg[1]
    step  = kr_cfg[2]
    k = trial.suggest_float(key_x+'_k', start, stop, step=step)

    trial.set_user_attr(f'{key_x}_params', {
        'fp': fp,
        'k': k
    })

    sp = int(fp * k)
    return fp, sp, f'{prefix}{name}'


def HIGHEST(high, N):
    return high.rolling(N).max()

def LOWEST(low, N):
    return low.rolling(N).min()

def RSUM(s, N):
    return s.rolling(N).sum()

def RSTD(s, N):
    return s.rolling(N).std()

def MA(s, N):
    return s.rolling(N).mean()

def EMA(s, N):
    return s.ewm(span=N, adjust=False).mean()

def ema_volume(vol_series, span):
    # 无量时不更新 防止 0 值将 EMA 拖向 0
    alpha = 2 / (span + 1)
    ema = np.nan
    result = []
    for vol in vol_series:
        if pd.notna(vol) and vol > 0:
            if np.isnan(ema):
                ema = vol
            else:
                ema = ema * (1 - alpha) + vol * alpha
        result.append(ema)
    return pd.Series(result, index=vol_series.index)


#下面BIAS只能用于量价（零即缺失的数据），不能用于持仓等，因为可能为0
def BIAS(s, N):
    b = s / MA(s, N) - 1
    return b

def BIAS_E(s, N):
    b = s / ema_volume(s, N) - 1
    return b

def nmBIAS(s, N, M):
    ma_n = MA(s, N)
    ma_m = MA(s, M)
    b = ma_n / ma_m - 1
    b[(ma_m == 0) | pd.isna(ma_m)] = np.nan
    return b

def nmBIAS_E(s, N, M):
    b = ema_volume(s, N) / ema_volume(s, M) - 1
    return b

'''
def ma_volume_smart(volume_series, span, skip_threshold=5):
    """
    智能成交量 MA：
    - 连续无量 < skip_threshold：正常更新，0值纳入
    - 连续无量 >= skip_threshold：触发冻结，只出不进
    """
    alpha = 2 / (span + 1)
    vs = []
    zero_streak = 0
    result = []

    for vol in volume_series:
        if vol > 0:
            # 有真实成交：无论之前是否冻结，现在强行解冻并更新
            vs.append(vol)
            if len(vs) > span:
                vs.pop(0)
            zero_streak = 0
        else:
            # vol == 0
            zero_streak += 1
            if zero_streak < skip_threshold:
                # 偶尔断档：正常纳入 0，让 MA 衰减
                vs.append(vol)
                if len(vs) > span:
                    vs.pop(0)
        result.append(np.mean(vs))

    return pd.Series(result, index=volume_series.index)

def ema_volume_smart(volume_series, span, skip_threshold=5):
    """
    智能成交量 EMA：
    - 连续无量 < skip_threshold：正常更新，0值纳入
    - 连续无量 >= skip_threshold：触发冻结，只出不进
    """
    alpha = 2 / (span + 1)
    ema = np.nan
    zero_streak = 0
    result = []

    for vol in volume_series:
        if vol > 0:
            # 有真实成交：无论之前是否冻结，现在强行解冻并更新
            if np.isnan(ema):
                ema = vol
            else:
                ema = ema * (1 - alpha) + vol * alpha
            zero_streak = 0
        else:
            # vol == 0
            zero_streak += 1
            if zero_streak < skip_threshold and not np.isnan(ema):
                # 偶尔断档：正常纳入 0，让 EMA 衰减
                ema = ema * (1 - alpha) + 0 * alpha
            # 如果 zero_streak >= skip_threshold 或 ema 还是 NaN:
            # 则什么都不做，ema 维持原值（冻结）
        result.append(ema)

    return pd.Series(result, index=volume_series.index)
'''

def ema_volume(volume_series, span):
    """
    成交量专用 EMA：只在成交量 > 0 时更新，无量期间保持不变。
    初始状态为 NaN，直到第一根有成交量的 K 线出现才开始计算。
    """
    alpha = 2 / (span + 1)
    ema = np.nan
    result = []

    for vol in volume_series:
        if vol > 0:
            if np.isnan(ema):
                ema = vol  # 初始化
            else:
                ema = ema * (1 - alpha) + vol * alpha
        # 若 vol == 0，ema 维持原值（包括维持 NaN）
        result.append(ema)

    return pd.Series(result, index=volume_series.index)


def PB(close, N):
    k = 2
    ma = MA(close, N)
    std = RSTD(close, N)
    diff = k * std
    down = ma - diff

    # 分母：2 * diff = 4 * std，当 std == 0 或 NaN 时整根 K 线无效
    denom = 2 * diff
    invalid = (std == 0) | pd.isna(std)

    pb = (close - down) / denom
    pb[invalid] = np.nan
    return pb


def BW(close, N):
    return RSTD(close, N) / MA(close, N) - 1


def CLV(high, low, close):
    spread = high - low
    clv = (2*close - high - low) / spread
    clv[spread == 0] = 0  # 一字板时，价格重心在极端位，CLV 给 0 是合理的
    return clv


def CV(high, low, N=10):
    hlema = EMA(high - low, N)
    prev = hlema.shift(N)
    cv = hlema.diff(N) / prev
    cv[prev == 0] = np.nan # 防止除0
    return cv


def DBCD(close, N=5, M=16, T=17):
    bias = BIAS(close, N)
    dif = bias.diff(M)
    return EMA(dif, T)


def RSV(high, low, close, N):
    highest = HIGHEST(high, N)
    lowest = LOWEST(low, N)
    denom = highest - lowest

    # 无效条件：分母为 0，或窗口内无有效波动（如缺数据导致 NaN）
    invalid = (denom == 0) | pd.isna(denom)

    rsv = (close - lowest) / denom * 100
    rsv[invalid] = np.nan
    return rsv

def KDJ(high, low, close, N=9):
    rsv = RSV(high, low, close, N)
    k = rsv.ewm(com=2, adjust=False).mean()  # pd.ewma(rsv,com=2)
    d = k.ewm(com=2, adjust=False).mean() # pd.ewma(klines['kdj_k'],com=2)，注意需要加adjust=False才能和np_kdj的结果相同，要不有些许差别
    j = 3.0 * k - 2.0 * d
    return k, d, j


def CR(high, low, close, N=20):
    typ = (high + low + close) / 3
    pre_typ = typ.shift()

    # 向量化计算，避免 apply
    hp = (high - pre_typ).clip(lower=0)   # 上攻能量
    pl = (pre_typ - low).clip(lower=0)    # 下杀能量

    # 滚动求和，要求窗口内至少有 N 根有效 K 线（可根据需要调整）
    hp_sum = hp.rolling(window=N, min_periods=N).sum()
    pl_sum = pl.rolling(window=N, min_periods=N).sum()

    # 分母为 0 或 NaN 时，整根 K 线无效
    invalid = (pl_sum == 0) | pd.isna(pl_sum)

    cr = hp_sum / pl_sum
    cr[invalid] = np.nan
    return cr


def MassIndex_ratio(high, low, N=9):
    """
    计算 Mass Index 的中间比值 emaratio，已处理分母为零和预热期。
    """
    spread = high - low
    emahl = spread.ewm(span=N, adjust=False).mean()
    ema_emahl = emahl.ewm(span=N, adjust=False).mean()

    # 分母为 0 或 NaN → 输出 NaN
    invalid = (ema_emahl == 0) | pd.isna(ema_emahl)
    emaratio = emahl / ema_emahl
    emaratio[invalid] = np.nan
    return emaratio


def MassIndex(high, low, N=9, sum_period=25):
    emaratio = MassIndex_ratio(high, low, N)   # 前面已除零保护
    mass = emaratio.rolling(window=sum_period, min_periods=sum_period).sum()
    return mass

def MassIndex_intraday(high, low, N=9, sum_period=25):
    """
    日内/高频版 Mass Index，不足窗口时按有效根数比例折算到标准窗口。
    """
    emaratio = MassIndex_ratio(high, low, N)

    # 滚动求和，允许窗口内只有 1 根有效即可出值
    sum_val = emaratio.rolling(window=sum_period, min_periods=1).sum()
    valid_n = emaratio.notna().rolling(window=sum_period, min_periods=1).sum()

    # 折算：平均每根有效值 × 标准窗口长度
    mass = (sum_val / valid_n.replace(0, np.nan)) * sum_period
    return mass


def ElderRayIndex(high, low, close, N=13):
    """
    多空力量差归一化，停板期间输出 NaN。
    """
    close_ema = close.ewm(span=N, adjust=False).mean()
    bull = high - close_ema
    bear = low - close_ema

    eri = (bull - bear) / close   # 等价于 (high - low) / close

    # 停板条件：价差为 0（一字板）→ 市场停滞，指标无效
    invalid = (high == low) | pd.isna(close)
    eri[invalid] = np.nan
    return eri


def ElderPowerRatio(high, low, close, N=13):
    """
    多空力量对比指标（方向性）。
    正值表示多方力量主导，负值表示空方力量主导，0 表示均衡。
    一字板期间输出 NaN，因为无法计算有效均线偏离。
    """
    close_ema = close.ewm(span=N, adjust=False).mean()
    bull = high - close_ema      # 多方力量（正向）
    bear = close_ema - low       # 空方力量（取正，方便比较）

    # 防止分母为 0（一字板时 bull 和 bear 可能都为 0）
    total = bull + bear
    invalid = (total == 0) | pd.isna(close_ema)

    # 多空力量归一化差值：+1 表示纯多头，-1 表示纯空头
    power = (bull - bear) / total
    power[invalid] = np.nan
    return power


def BarAmplitude(high, low, close):
    return (high - low) / close


def UOS(high, low, close, M=7, N=14, O=28):
    prev_close = close.shift()
    # 向量化替代 apply
    th = np.maximum(high, prev_close)
    tl = np.minimum(low, prev_close)
    tr = th - tl
    xr = close - tl

    # 滚动求和，要求窗口满才有效（min_periods 等于窗口长度）
    xr_M = xr.rolling(window=M, min_periods=M).sum()
    tr_M = tr.rolling(window=M, min_periods=M).sum()
    xr_N = xr.rolling(window=N, min_periods=N).sum()
    tr_N = tr.rolling(window=N, min_periods=N).sum()
    xr_O = xr.rolling(window=O, min_periods=O).sum()
    tr_O = tr.rolling(window=O, min_periods=O).sum()

    # 分母为 0 或 NaN 时，比值无效
    XRM = xr_M / tr_M
    XRM[(tr_M == 0) | pd.isna(tr_M)] = np.nan
    XRN = xr_N / tr_N
    XRN[(tr_N == 0) | pd.isna(tr_N)] = np.nan
    XRO = xr_O / tr_O
    XRO[(tr_O == 0) | pd.isna(tr_O)] = np.nan

    # 加权合成，任一单周期为 NaN 则结果 NaN
    numerator = XRM * N * O + XRN * M * O + XRO * M * N
    denominator = M * N + M * O + N * O
    UOS = 100 * numerator / denominator
    return UOS


def UOS_intraday(high, low, close, M=7, N=14, O=28):
    """
    日内高频版 UOS（终极摆动指标）。
    - 允许窗口内不足标准长度时出值（min_periods=1）
    - 分母为 0（停板导致真实波幅为 0）该周期比值置 NaN
    - 任一周期比值为 NaN 则最终 UOS 为 NaN，信号层可自动屏蔽
    """
    prev_close = close.shift()
    # 真实高点、真实低点
    th = np.maximum(high, prev_close)
    tl = np.minimum(low, prev_close)
    tr = th - tl
    xr = close - tl

    # 分子分母滚动求和，最少 1 根有效即出值
    xr_M = xr.rolling(window=M, min_periods=1).sum()
    tr_M = tr.rolling(window=M, min_periods=1).sum()
    xr_N = xr.rolling(window=N, min_periods=1).sum()
    tr_N = tr.rolling(window=N, min_periods=1).sum()
    xr_O = xr.rolling(window=O, min_periods=1).sum()
    tr_O = tr.rolling(window=O, min_periods=1).sum()

    # 比值：分母为 0 → 比值无意义，置 NaN
    XRM = xr_M / tr_M
    XRM[(tr_M == 0) | pd.isna(tr_M)] = np.nan
    XRN = xr_N / tr_N
    XRN[(tr_N == 0) | pd.isna(tr_N)] = np.nan
    XRO = xr_O / tr_O
    XRO[(tr_O == 0) | pd.isna(tr_O)] = np.nan

    # 加权合成（固定权重）
    numerator = XRM * N * O + XRN * M * O + XRO * M * N
    denominator = M * N + M * O + N * O
    UOS = 100 * numerator / denominator
    return UOS


def SI(open, high, low, close):
    """
    计算单根K线的摆动值 SI（Wilder's Swing Index）。
    若分母为0或市场处于一字停板状态，返回 NaN。
    全向量化实现，无逐行循环。
    """
    prev_close = close.shift()
    prev_open = open.shift()
    prev_low = low.shift()

    # 价格变化分量
    E = close.diff()                          # 收盘价净变化
    A = E.abs()                               # 净变化绝对值
    B = (low - prev_close).abs()              # 最低价与昨收的距离
    C = (high - prev_low).abs()               # 最高价与昨低的距离
    D = (prev_close - prev_open).abs()        # 昨振幅
    F = close - open                          # 今振幅
    G = prev_close - prev_open                # 昨振幅

    X = E + F / 2 + G
    K = np.maximum(A, B)                      # 等价于 max(A, B)

    # 向量化计算 R（根据 A, B, C 的最大值分支）
    cond_A = (A >= B) & (A >= C)
    cond_B = (B > A) & (B >= C)
    cond_C = ~cond_A & ~cond_B

    R = pd.Series(np.nan, index=close.index)
    R[cond_A] = A[cond_A] + B[cond_A]/2 + D[cond_A]/4
    R[cond_B] = A[cond_B]/2 + B[cond_B] + D[cond_B]/4
    R[cond_C] = C[cond_C] + D[cond_C]/4

    # 无效条件：分母 R 为 0，或行情完全停滞（K=0且X=0，即一字板）
    invalid = (R == 0) | ((K == 0) & (X == 0)) | R.isna()
    SI_val = 16 * X / R * K
    SI_val[invalid] = np.nan
    return SI_val


def ASIR(open, high, low, close, N=20):
    si = SI(open, high, low, close)
    # 稳健版：窗口满 N 根有效 K 线才出值
    asi = si.rolling(window=N, min_periods=N).sum()
    ema = close.ewm(span=N, adjust=False).mean()
    asir = asi / ema
    return asir


def ASIR_intraday(open, high, low, close, N=20):
    """
    日内高频版 ASIR：累积摆动与 EMA 的比率。
    允许窗口内不足 N 根有效 K 线时按比例折算，从而开板后立即产生信号。
    """
    si = SI(open, high, low, close)

    # 滚动求和与有效计数（最少1根有效即出值）
    si_sum = si.rolling(window=N, min_periods=1).sum()
    valid_n = si.notna().rolling(window=N, min_periods=1).sum()

    # 折算到标准 N 根水平：平均每根 × N
    asi = (si_sum / valid_n.replace(0, np.nan)) * N

    # 价格 EMA（标准 ewm，无特殊处理）
    ema = close.ewm(span=N, adjust=False).mean()

    asir = asi / ema
    return asir


def UI(close, N):
    closest = close.rolling(N).max()
    Ri = (close - closest) / closest
    return Ri

# Hurst本身依赖窗口内的统计分布，过早出值没有意义，故没有高频版
def Hurst(close, N):
    def rs_calc(window):
        log_p = np.log(window)
        if len(window) < N:
            return np.nan
        mean_log = log_p.mean()
        cum_dev = (log_p - mean_log).cumsum()
        R = cum_dev.max() - cum_dev.min()
        S = np.diff(log_p).std() if len(log_p) > 1 else 0
        if S == 0 or np.isnan(S):
            return np.nan
        return np.log(R / S)
    return close.rolling(window=N, min_periods=N).apply(rs_calc, raw=True)


def MFI(high, low, close, volume, N=14):
    """
    MFI 稳健版：窗口满 N 根有效 K 线才出值。
    一字无量期分母=0 → 输出 NaN。
    完全抛弃 talib.MFI，自实现，便于控制内部无效状态。
    """
    # 1. 典型价（价格已连续填充，无缺失）
    tp = (high + low + close) / 3.0

    # 2. 原始资金流
    rmf = tp * volume

    # 3. 无效条件：volume 无效（NaN 或 ≤0）或 tp 无波动 → 该根 rmf 不参与累加
    invalid = (volume <= 0) | pd.isna(volume) | pd.isna(tp)
    rmf_valid = rmf.mask(invalid, np.nan)

    # 4. 有效 rmf 的正负分流
    pos_rmf = rmf_valid.where(tp.diff() > 0, 0.0)
    neg_rmf = rmf_valid.where(tp.diff() < 0, 0.0)

    # 5. 滚动 N 期累加，要求窗口满 N 根有效 K 线才出值
    pos_sum = pos_rmf.rolling(window=N, min_periods=N).sum()
    neg_sum = neg_rmf.rolling(window=N, min_periods=N).sum()

    # 6. 分母为 0 → 输出 NaN
    mf_ratio = pos_sum / neg_sum
    mf_ratio[neg_sum == 0] = np.nan

    mfi = 100.0 - 100.0 / (1.0 + mf_ratio)
    mfi[pd.isna(mf_ratio)] = np.nan
    return mfi


def MFI_intraday(high, low, close, volume, N=14):
    """
    MFI 高频版：开板后立即出值，不足 N 根时按有效根数折算。
    一字无量期分母=0 → 输出 NaN。
    """
    tp = (high + low + close) / 3.0
    rmf = tp * volume

    invalid = (volume <= 0) | pd.isna(volume) | pd.isna(tp)
    rmf_valid = rmf.mask(invalid, np.nan)

    pos_rmf = rmf_valid.where(tp.diff() > 0, 0.0)
    neg_rmf = rmf_valid.where(tp.diff() < 0, 0.0)

    # 有效 K 线计数
    valid_mask = rmf_valid.notna()
    valid_n = valid_mask.rolling(window=N, min_periods=1).sum()

    # 折算到 N 根标准窗口
    pos_sum_raw = pos_rmf.rolling(window=N, min_periods=1).sum()
    neg_sum_raw = neg_rmf.rolling(window=N, min_periods=1).sum()

    pos_sum = (pos_sum_raw / valid_n.replace(0, np.nan)) * N
    neg_sum = (neg_sum_raw / valid_n.replace(0, np.nan)) * N

    mf_ratio = pos_sum / neg_sum
    mf_ratio[neg_sum == 0] = np.nan

    mfi = 100.0 - 100.0 / (1.0 + mf_ratio)
    mfi[pd.isna(mf_ratio)] = np.nan
    return mfi


def CMF(high, low, close, volume, N=21):
    spread = high - low
    clv = ((close - low) - (high - close)) / spread

    # 统一的无效条件：spread无效 或 volume无效 → 整根K线不参与计算
    invalid = (spread == 0) | (volume <= 0) | pd.isna(volume)
    clv[invalid] = np.nan
    va = clv * volume

    vol_clean = volume.copy()
    vol_clean[invalid] = np.nan

    va_sum = va.rolling(window=N, min_periods=N).sum()
    vol_sum = vol_clean.rolling(window=N, min_periods=N).sum()
    return va_sum / vol_sum


def CMF_intraday(high, low, close, volume, N=21):
    spread = high - low
    clv = ((close - low) - (high - close)) / spread

    # 统一的无效条件：spread无效 或 volume无效 → 整根K线不参与计算
    invalid = (spread == 0) | (volume <= 0) | pd.isna(volume)
    clv[invalid] = np.nan
    va = clv * volume  # 无效时自动为NaN

    # vol_clean 也必须使用完全相同的 invalid 条件
    vol_clean = volume.copy()
    vol_clean[invalid] = np.nan

    va_sum = va.rolling(window=N, min_periods=1).sum()
    vol_sum = vol_clean.rolling(window=N, min_periods=1).sum()

    return va_sum / vol_sum


def EMV(high, low, volume, N=14):
    # 稳健版（适合中低频），必须等攒满 N 根有效 K 线
    mid = (high + low) / 2
    spread = high - low

    # 原始 em
    em = volume * (mid.diff() / spread)

    # 无效条件：价差为0，或成交量无效（0/NaN）
    invalid_mask = (spread == 0) | (volume <= 0) | pd.isna(volume)
    em[invalid_mask] = np.nan

    # 滚动求和，自动跳过 NaN，min_periods 设为 N，不足 N 根则出 NaN
    emv = em.rolling(window=N, min_periods=N).sum()
    return emv


def EMV_intraday(high, low, volume, N=14):
    # 平滑启动版（适合日内高频），不足 N 根时按比例折算
    mid = (high + low) / 2
    spread = high - low

    em = volume * (mid.diff() / spread)

    # 同样的无效条件
    invalid_mask = (spread == 0) | (volume <= 0) | pd.isna(volume)
    em[invalid_mask] = np.nan

    # 有效 K 线求和与计数
    emv_sum = em.rolling(window=N, min_periods=1).sum()
    valid_count = em.notna().rolling(window=N, min_periods=1).sum()

    # 折算，分母为 0 时保持 NaN
    emv = (emv_sum / valid_count.replace(0, np.nan)) * N
    return emv


def WVAD(open, high, low, close, volume, N=12):
    spread = high - low
    vad = volume * ((close - open) / spread)

    # 无效条件：价差为0，或成交量无效
    invalid = (spread == 0) | (volume <= 0) | pd.isna(volume)
    vad[invalid] = np.nan

    # 必须凑满 N 根有效 K 线
    wvad = vad.rolling(window=N, min_periods=N).sum()
    return wvad


def WVAD_intraday(open, high, low, close, volume, N=12):
    spread = high - low
    vad = volume * ((close - open) / spread)

    invalid = (spread == 0) | (volume <= 0) | pd.isna(volume)
    vad[invalid] = np.nan

    vad_sum = vad.rolling(window=N, min_periods=1).sum()
    valid_count = vad.notna().rolling(window=N, min_periods=1).sum()

    wvad = (vad_sum / valid_count.replace(0, np.nan)) * N
    return wvad


def WVADR(open, high, low, close, volume, N=12, M=24):
    spread = high - low
    vad = volume * ((close - open) / spread)

    # 无效条件：价差为0，或成交量无效
    invalid = (spread == 0) | (volume <= 0) | pd.isna(volume)
    vad[invalid] = np.nan

    # 必须凑满 N 根有效 K 线
    wvadn = vad.rolling(window=N, min_periods=N).sum()
    wvadm = vad.rolling(window=M, min_periods=M).sum()
    return wvadn / wvadm - 1


def WVADR_intraday(open, high, low, close, volume, N=12, M=24):
    spread = high - low
    vad = volume * ((close - open) / spread)
    invalid = (spread == 0) | (volume <= 0) | pd.isna(volume)
    vad[invalid] = np.nan

    avg_n = vad.rolling(N, min_periods=1).mean()  # mean 自动跳过 NaN
    avg_m = vad.rolling(M, min_periods=1).mean()
    return avg_n / avg_m - 1


def OI_diff_ratio(oi, N=20):
    oi_diff = oi.diff()
    base = oi_diff.abs().rolling(window=N, min_periods=N).mean()
    oidr = oi_diff / base
    # 分母为 0 或 NaN 时，输出 NaN
    oidr[(base == 0) | pd.isna(base)] = np.nan
    return oidr


def OI_diff_ratio_intraday(oi, span=20):
    oi_diff = oi.diff()
    base = ema_volume(oi_diff.abs(), span)   # 跳过 NaN，无量时冻结
    oidr = oi_diff / base
    oidr[base == 0] = np.nan
    return oidr


def OI_diff_ratio_atr(oi, high, low, N=20):
    oi_diff = oi.diff()
    atr = (high - low).rolling(N, min_periods=N).mean()  # 价格已连续填充
    oidr = oi_diff / atr
    oidr[atr == 0] = np.nan
    return oidr


def OI_diff_percentile(oi, N=252):
    oi_diff = oi.diff().abs()
    rank = oi_diff.rolling(N, min_periods=N).rank(pct=True)
    return rank


def OIV(volume, oi):
    oi_diff = oi.diff()
    # 无效条件：成交量无效（0、NaN），或持仓量变化无法计算
    invalid = (volume <= 0) | pd.isna(volume) | pd.isna(oi_diff)
    oiv = oi_diff / volume
    oiv[invalid] = np.nan
    return oiv


def VOI(volume, oi):
    # 无效条件：成交量无效 或 前一持仓量无效/为零
    prev_oi = oi.shift()
    invalid = (volume <= 0) | pd.isna(volume) | pd.isna(prev_oi) | (prev_oi == 0)
    voi = volume / prev_oi
    voi[invalid] = np.nan
    return voi


def WPR(bid, bid_size, ask, ask_size):
    # 分母无效（无买盘或无卖盘，或挂单量为0）→ 输出 NaN
    denom = bid_size + ask_size
    invalid = (denom == 0) | pd.isna(bid) | pd.isna(ask) | (bid_size <= 0) | (ask_size <= 0)

    wpr = (bid * ask_size + ask * bid_size) / denom
    wpr[invalid] = np.nan
    return wpr


def WPR_robust(bid, bid_size, ask, ask_size):
    # 正常情况下双侧有效
    valid = (bid_size > 0) & (ask_size > 0) & pd.notna(bid) & pd.notna(ask)

    # 基于有效边计算
    wpr = pd.Series(np.nan, index=bid.index)
    wpr[valid] = (bid*ask_size + ask*bid_size) / (bid_size + ask_size)

    # 如果只有买单（涨停），以买价作为参考
    only_bid = (bid_size > 0) & ((ask_size == 0) | pd.isna(ask))
    wpr[only_bid] = bid

    # 如果只有卖单（跌停），以卖价作为参考
    only_ask = (ask_size > 0) & ((bid_size == 0) | pd.isna(bid))
    wpr[only_ask] = ask

    return wpr


import pandas as pd
import numpy as np
# 市场环境因素
# ==================== 基础工具 ====================
def true_range(high, low, close_prev):
    """
    真实波幅 TR
    三项最大值: (high-low), |high-昨收|, |low-昨收|
    涵盖日内振幅和隔夜跳空，是波动率计算的基础。
    """
    return pd.concat([
        high - low,
        (high - close_prev).abs(),
        (low - close_prev).abs()
    ], axis=1).max(axis=1)


def rolling_percentile(series, window=250, min_periods=None):
    """
    滚动分位数 (0~1)
    表示当前值在过去 window 天中处于多高的位置。
    1.0 → 当前值比历史上所有值都高（最高水位）
    0.0 → 当前值比历史上所有值都低（最低水位）
    """
    if min_periods is None:
        min_periods = window
    return series.rolling(window, min_periods=min_periods).apply(
        lambda x: (x[-1] > x[:-1]).mean() if len(x) >= min_periods else np.nan,
        raw=True
    )

def expanding_percentile(series, min_periods=42):
    """
    累积历史分位数 (0~1)
    从序列开头开始累积，至少 min_periods 个值后才开始计算。
    """
    return series.expanding(min_periods).apply(
        lambda x: (x[-1] > x[:-1]).mean(),
        raw=True
    )


# ==================== ATR 家族 ====================
def ATR(high, low, close, period=14):
    """
    平均真实波幅 ATR (Wilder平滑版)
    与ADX平滑方式一致，使用alpha=1/period的EMA
    """
    prev_close = close.shift(1)
    tr = true_range(high, low, prev_close)
    # 使用与ADX一致的Wilder平滑，而非简单移动平均
    return tr.ewm(alpha=1/period, min_periods=period, adjust=False).mean()


def ATR_pct(high, low, close, period=14):
    """相对波幅 = ATR / 收盘价，消除价格量级影响。"""
    return ATR(high, low, close, period) / close


def ATR_percentile(high, low, close, period=14, percentile_window=250):
    """
    ATR 的分位数水位
    percentile_window 代表回头多少根K线（在日线上常用250=一年，小时线可用500≈两月）。
    """
    return rolling_percentile(ATR(high, low, close, period), percentile_window)


# ==================== ADX 家族（与时间轴无关） ====================
def DI_plus(high, low, close, period=14):
    """
    +DI 上升方向线
    +DM = 当前最高 - 前最高（如果向上且大于向下动向），平滑后除以 ATR。
    值越大，多头主动推升力量越强。
    """
    prev_close = close.shift(1)
    atr = ATR(high, low, close, period)
    up = high - high.shift(1)
    down = low.shift(1) - low
    plus_dm = pd.Series(np.where((up > down) & (up > 0), up, 0), index=close.index)
    return 100 * (plus_dm.ewm(alpha=1/period, min_periods=period).mean() / atr)


def DI_minus(high, low, close, period=14):
    """
    -DI 下降方向线
    -DM = 前低 - 当前低（如果向下且大于向上动向），平滑后除以 ATR。
    值越大，空头主动打压力量越强。
    """
    prev_close = close.shift(1)
    atr = ATR(high, low, close, period)
    up = high - high.shift(1)
    down = low.shift(1) - low
    minus_dm = pd.Series(np.where((down > up) & (down > 0), down, 0), index=close.index)
    return 100 * (minus_dm.ewm(alpha=1/period, min_periods=period).mean() / atr)


def ADX(high, low, close, period=14):
    """
    平均趋向指数 ADX
    先计算 DX = |+DI - -DI| / (+DI + -DI) * 100，再平滑。
    衡量趋势强度，不指示方向。<20 震荡，>25 趋势启动，>30 强趋势。
    """
    plus = DI_plus(high, low, close, period)
    minus = DI_minus(high, low, close, period)
    dx = (abs(plus - minus) / (plus + minus + 1e-9)) * 100
    return dx.ewm(alpha=1/period, min_periods=period).mean()


def DI_diff(high, low, close, period=14):
    """+DI 与 -DI 差值，正值偏多，负值偏空。"""
    return DI_plus(high, low, close, period) - DI_minus(high, low, close, period)


# ==================== 多周期位置（窗口代表K线根数） ====================
def Position(close, high, low, window=20):
    """
    相对区间位置 = (收盘-最低)/(最高-最低)，0~1之间。
    0 处于窗口最低点，1 处于窗口最高点。
    """
    highest = high.rolling(window).max()
    lowest  = low.rolling(window).min()
    return (close - lowest) / (highest - lowest + 1e-9)


def Position_historical(close, high, low):
    """上市以来历史极值位置，expanding max/min，无需窗口参数。"""
    hist_high = high.expanding().max()
    hist_low  = low.expanding().min()
    return (close - hist_low) / (hist_high - hist_low + 1e-9)


# ==================== 布林带 ====================
def BB_position(close, window=20, num_std=2):
    """
    布林带位置：价格在下轨=0，上轨=1。
    利用正态分布概念衡量价格相对波动范围的极端程度。
    """
    ma = close.rolling(window).mean()
    std = close.rolling(window).std()
    upper = ma + num_std * std
    lower = ma - num_std * std
    return (close - lower) / (upper - lower + 1e-9)


def BB_width_pct(close, window=20, num_std=2):
    """
    布林带宽度/% = (上轨-下轨)/中轨，度量波动率扩张/收缩。
    高值→盘整突破前兆，低值→死水。
    """
    ma = close.rolling(window).mean()
    std = close.rolling(window).std()
    upper = ma + num_std * std
    lower = ma - num_std * std
    return (upper - lower) / ma


# ==================== 趋势强度与年龄 ====================
def MA_slope(close, ma_period=50, slope_lookback=20):
    """
    均线斜率：MA 在 slope_lookback 天内的相对变化率。
    正值向上，负值向下，绝对值大小反映趋势力度。
    """
    ma = close.rolling(ma_period).mean()
    return (ma - ma.shift(slope_lookback)) / (ma.shift(slope_lookback) + 1e-9)


def Trend_age(close, ma_period=50, slope_lookback=20):
    """
    趋势年龄：MA 斜率保持同向的连续K线根数。
    数越大，趋势越“老”，反转概率可能增加。
    """
    slope = MA_slope(close, ma_period, slope_lookback)
    sign = np.sign(slope)
    return sign.groupby((sign != sign.shift(1)).cumsum()).cumcount() + 1


# ==================== 持仓量特征 ====================
def OI_change_pct(open_interest, window=5):
    """持仓量变化率，增仓表明资金主动，趋势可能持续。"""
    return open_interest.pct_change(window)


def Price_OI_corr(open_interest, close, window=5, corr_window=20):
    """
    价格与持仓量的滚动相关。
    正相关 → 价量配合，趋势健康；负相关或背离 → 警惕反转。
    """
    oi_c = open_interest.pct_change(window)
    price_c = close.pct_change(window)
    return price_c.rolling(corr_window).corr(oi_c)


# ==================== 日线封装 ====================

# ==================== 动态趋势强度特征（日线版） ====================

def ADX_percentile_daily(high, low, close, period=14, lookback=500, min_periods=250):
    """ADX 滚动分位数，lookback 窗口内排名"""
    adx_series = ADX(high, low, close, period=period)
    return rolling_percentile(adx_series, window=lookback, min_periods=min_periods)


def ADX_percentile_historical_daily(high, low, close, period=14, min_periods=42):
    """ADX 在全历史中的累积分位数（主力合约内部）"""
    adx_series = ADX(high, low, close, period=period)
    return expanding_percentile(adx_series, min_periods=min_periods)


def ADX_accel_daily(high, low, close, period=14, diff_window=5, smooth=3):
    """
    ADX 动量（加速度）
    先计算 diff_window 天的变化，再用 smooth 天均值平滑。
    正值 → 趋势增强；负值 → 趋势衰竭。
    """
    adx_series = ADX(high, low, close, period=period)
    raw_diff = adx_series.diff(diff_window)
    return raw_diff.rolling(smooth).mean()


def ADX_accel2_daily(high, low, close, period=14, diff_window=5, smooth=3):
    """
    ADX 加速度的加速度（二阶）
    逻辑：
      1. 计算一阶加速度 accel = ADX_accel_daily(...)
      2. 对 accel 再求 diff_window 天的差分
      3. 做 smooth 天平滑
    返回：二阶加速度序列
    """
    accel = ADX_accel_daily(high, low, close, period=period, 
                           diff_window=diff_window, smooth=smooth)
    raw_diff2 = accel.diff(diff_window)
    return raw_diff2.rolling(smooth).mean()


def ADX_accel_percentile_daily(high, low, close, period=14, diff_window=5, lookback=500):
    """
    ADX 加速度的滚动分位数 (0~1)
    值接近 1 → 趋势强度正在以历史少有的速度增强。
    """
    accel = ADX_accel_daily(high, low, close, period, diff_window)
    return rolling_percentile(accel, window=lookback)


def DI_diff_zscore_daily(high, low, close, period=14, lookback=500):
    """
    DI_diff 的滚动标准化值 (Z-score)
    用过去 lookback 天的均值和标准差对当前值做突变判断。
    正值且很大 → 多头极端；负值且绝对值很大 → 空头极端。
    """
    di_diff_series = DI_diff(high, low, close, period=period)
    mean = di_diff_series.rolling(lookback).mean()
    std = di_diff_series.rolling(lookback).std()
    # 避免早期除零
    return (di_diff_series - mean) / (std + 1e-9)


def DI_diff_percentile_daily(high, low, close, period=14, lookback=500, min_periods=250):
    """+DI 与 -DI 差值的滚动分位数"""
    di = DI_diff(high, low, close, period=period)
    return rolling_percentile(di, window=lookback, min_periods=min_periods)


def DI_diff_accel_daily(high, low, close, period=14, diff_window=5, smooth=3):
    """
    DI_diff 动量（加速度）
    先计算 diff_window 天的变化，再用 smooth 天均值平滑。
    正值 → 趋势增强；负值 → 趋势衰竭。
    """
    dd_series = DI_diff(high, low, close, period=period)
    raw_diff = dd_series.diff(diff_window)
    return raw_diff.rolling(smooth).mean()


def Position_monthly_daily(close, high, low):
    """月线区间位置：20个交易日"""
    return Position(close, high, low, window=20)

def Position_quarterly_daily(close, high, low):
    """季度区间位置：60个交易日"""
    return Position(close, high, low, window=60)

def Position_yearly_daily(close, high, low):
    """年度区间位置：250个交易日"""
    return Position(close, high, low, window=250)

def ATR_percentile_daily(high, low, close):
    """日线ATR分位数：回头看250天（一年）"""
    return ATR_percentile(high, low, close, period=14, percentile_window=250)

def BB_position_daily(close):
    """日线布林带位置，默认20日"""
    return BB_position(close, window=20)

def BB_width_pct_daily(close):
    """日线布林带宽度，默认20日"""
    return BB_width_pct(close, window=20)

def MA_slope_daily(close):
    """日线均线斜率：50日均线，回看20天"""
    return MA_slope(close, ma_period=50, slope_lookback=20)

def Trend_age_daily(close):
    """日线趋势年龄：50日均线斜率，回看20天"""
    return Trend_age(close, ma_period=50, slope_lookback=20)

def OI_change_pct_daily(open_interest):
    """日线持仓量变化：窗口5天"""
    return OI_change_pct(open_interest, window=5)

def Price_OI_corr_daily(open_interest, close):
    """日线价量相关性：窗口5天变化，20天滚动相关"""
    return Price_OI_corr(open_interest, close, window=5, corr_window=20)


# ==================== 小时线封装 ====================
def Position_intraday_hourly(close, high, low):
    """日内区间位置：6小时（约1个交易日）"""
    return Position(close, high, low, window=6)

def Position_weekly_hourly(close, high, low):
    """周度区间位置：30小时（约5个交易日）"""
    return Position(close, high, low, window=30)

def Position_monthly_hourly(close, high, low):
    """月度区间位置：120小时（约20个交易日）"""
    return Position(close, high, low, window=120)

def ATR_percentile_hourly(high, low, close):
    """小时线ATR分位数：回头看500小时（约2个月）"""
    return ATR_percentile(high, low, close, period=14, percentile_window=500)

def BB_position_hourly(close):
    """小时线布林带位置：24小时（约4天）"""
    return BB_position(close, window=24)

def BB_width_pct_hourly(close):
    """小时线布林带宽度：24小时"""
    return BB_width_pct(close, window=24)

def MA_slope_hourly(close):
    """小时线均线斜率：24小时均线，回看12小时"""
    return MA_slope(close, ma_period=24, slope_lookback=12)

def Trend_age_hourly(close):
    """小时线趋势年龄：24小时均线，回看12小时"""
    return Trend_age(close, ma_period=24, slope_lookback=12)

def OI_change_pct_hourly(open_interest):
    """小时线持仓量变化：窗口6小时"""
    return OI_change_pct(open_interest, window=6)

def Price_OI_corr_hourly(open_interest, close):
    """小时线价量相关性：窗口6小时变化，24小时滚动相关"""
    return Price_OI_corr(open_interest, close, window=6, corr_window=24)
