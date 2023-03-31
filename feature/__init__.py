import numpy as np
import pandas as pd

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

def BIAS(s, N):
    return s / MA(s, N) - 1

def nmBIAS(s, N, M):
    return MA(s, N) / MA(s, M) - 1

def PB(close, N):
    k = 2
    diff = k * RSTD(close, N)
    down = MA(close, N) - diff
    return (close - down) / (2 * diff)

def BW(close, N):
    return RSTD(close, N) / MA(close, N)

def CLV(high, low, close):
    return (2*close - high - low) / (high - low)

def CV(high, low, N=10):
    hlema = EMA(high - low, N)
    return hlema.diff(N) / hlema.shift(N)

def DBCD(close, N=5, M=16, T=17):
    bias = BIAS(close, N)
    dif = bias.diff(M)
    return EMA(dif, T)

def RSV(high, low, close, N):
    highest = HIGHEST(high, N)
    lowest = LOWEST(low, N)
    return (close - lowest) / (highest - lowest) * 100

def KDJ(high, low, close, N=9):
    rsv = RSV(high, low, close, N)
    k = rsv.ewm(com=2, adjust=False).mean()  # pd.ewma(rsv,com=2)
    d = k.ewm(com=2, adjust=False).mean() # pd.ewma(klines['kdj_k'],com=2)，注意需要加adjust=False才能和np_kdj的结果相同，要不有些许差别
    j = 3.0 * k - 2.0 * d
    return k, d, j

def CMF(high, low, close, volume, N=21):
    clv = CLV(high, low, close)
    va = clv * volume
    return RSUM(va, N) / RSUM(volume, N)

def CR(high, low, close, N=20):
    typ = (high + low + close) / 3
    pre_typ = typ.shift()
    hp = (high - pre_typ).apply(lambda x: max(x, 0))
    pl = (pre_typ - low).apply(lambda x: max(x, 0))
    return RSUM(hp, N) / RSUM(pl, N)

def CR2(high, low, close, N=20):
    return CR(HIGHEST(high, N), LOWEST(low, N), close, N)

def MassIndex(high, low, close, N=9):
    emahl = EMA(high - low, N)
    emaratio = emahl / EMA(emahl, N)
    return emaratio#RSUM(emaratio, 25)

def MassIndex2(high, low, close, N=9):
    return MassIndex(HIGHEST(high, N), LOWEST(low, N), close, N)

def ElderRayIndex(high, low, close, N=13):
    close_ema = EMA(close, N)
    BullPower = high - close_ema
    BearPower = low - close_ema
    return (BullPower - BearPower) / close

def ElderRayIndex2(high, low, close, N=13):
    return ElderRayIndex(HIGHEST(high, N), LOWEST(low, N), close, N)

def max_df(a, b):
    df = pd.DataFrame()
    df['a'] = a
    df['b'] = b
    s = df.apply(np.max, axis=1)
    return s

def min_df(a, b):
    df = pd.DataFrame()
    df['a'] = a
    df['b'] = b
    s = df.apply(np.min, axis=1)
    return s

def UOS(high, low, close, M=7, N=14, O=28):
    prev_close = close.shift()
    th = max_df(high, prev_close)
    tl = min_df(low, prev_close)
    tr = th - tl
    xr = close - tl
    XRM = RSUM(xr, M) / RSUM(tr, M)
    XRN = RSUM(xr, N) / RSUM(tr, N)
    XRO = RSUM(xr, O) / RSUM(tr, O)
    UOS = 100 * (XRM*N*O + XRN*M*O + XRO*M*N) / (M*N + M*O+ N*O)
    return UOS

def UOS2(high, low, close, M=7, N=14, O=28):
    return UOS(HIGHEST(high, N), LOWEST(low, N), close, M, N, O)

def si_r(x):
    m = max(x.a, x.b, x.c)
    if m == x.a:
        return x.a + x.b/2 + x.d/4
    elif m == x.b:
        return x.a/2 + x.b + x.d/4
    elif m == x.c:
        return x.c + x.d/4

def SI(open, high, low, close, N):
    prev_close = close.shift()
    prev_open = open.shift()
    prev_low = low.shift()
    E = close.diff()
    A = E.abs()
    B = (low - prev_close).abs()
    C = (high - prev_low).abs()
    D = (prev_close - prev_open).abs()
    F = close - open
    G = prev_close - prev_open
    X = E + F/2 + G
    #K = max(A, B)
    df = pd.DataFrame()
    df['a'] = A
    df['b'] = B
    K = df.apply(np.max, axis=1)

    df['c'] = C
    df['d'] = D
    R = df.apply(si_r, axis=1)
    '''
    max_v = max(A, B, C)
    if max_v == A:
        R = A + B/2 + D/4
    elif max_v == B:
        R = A/2 + B + D/4
    else:
        R = C + D/4
    '''
    SI = 16 * X / R * K

    df['k'] = K
    df['r'] = R
    df['si'] = SI
    #print(df)

    return SI

def ASIR(open, high, low, close, N=20):
    si = SI(open, high, low, close, N)
    asi = RSUM(si, N)
    asir = asi / EMA(close, N)
    return asir

def ASIR2(open, high, low, close, N=20):
    return ASIR(open, HIGHEST(high, N), LOWEST(low, N), close)

def UI(close, N):
    closest = close.rolling(N).max()
    Ri = (close - closest) / closest
    return Ri

def Hurst(close, N):
    n = N
    x = log(close) - log(close.shift())
    mean = x.rolling(n).mean()
    std = x.rolling(n).std()
    z = (close - mean).rolling(n).sum()
    r = z.rolling(N).max() - z.rolling(N).min()
    y = log(r/std)

def EMV(high, low, volume):
    mid = (high + low) / 2
    prev_mid = mid.shift()
    return (mid - prev_mid) / (high - low)

def WVAD(open, high, low, close, volume):
    return volume * ((close - open)/(high - low))

def OIV(volume, oi):
    diff_oi = oi - oi.shift()
    return diff_oi / volume

def VOI(volume, oi):
    return volume / oi.shift()

def WPR(bid, bid_size, ask, ask_size):
    return (bid*ask_size + ask*bid_size) / (bid_size+ask_size)
