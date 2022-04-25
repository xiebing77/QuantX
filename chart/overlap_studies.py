#!/usr/bin/python3
import talib

plot_colors = ['y', 'r', 'b', 'm', 'k']

def add_argument_overlap_studies(parser):
    # Overlap Studies
    group = parser.add_argument_group('Overlap Studies')

    group.add_argument('--ABANDS', type=int, nargs='*', help='ATR Bands')
    group.add_argument('--BANDS', type=float, nargs='?', const=0.1, help=' Bands')

    # talib
    group = parser.add_argument_group('Overlap Studies (TaLib)')
    group.add_argument('--BBANDS', action="store_true", help='Bollinger Bands')
    group.add_argument('--DEMA', type=int, nargs='?', const=30, help='Double Exponential Moving Average')
    group.add_argument('--EMA', type=int, nargs='*', help='Exponential Moving Average')
    group.add_argument('--HT_TRENDLINE', action="store_true", help='Hilbert Transform - Instantaneous Trendline')
    group.add_argument('--KAMA', type=int, nargs='*', help='Kaufman Adaptive Moving Average')
    group.add_argument('--MA', type=int, nargs='*', help='Moving average')
    group.add_argument('--MAMA', action="store_true", help='MESA Adaptive Moving Average')
    group.add_argument('--MIDPOINT', type=int, nargs='?', const=14, help='MidPoint over period')
    group.add_argument('--MIDPRICE', type=int, nargs='?', const=14, help='Midpoint Price over period')
    group.add_argument('--SAR', action="store_true", help='Parabolic SAR')
    group.add_argument('--SAREXT', action="store_true", help='Parabolic SAR - Extended')
    group.add_argument('--SMA', type=int, nargs='?', const=30, help='Simple Moving Average')
    group.add_argument('--T3', type=int, nargs='?', const=5, help='Triple Exponential Moving Average')
    group.add_argument('--TEMA', type=int, nargs='?', const=30, help='Triple Exponential Moving Average')
    group.add_argument('--TRIMA', type=int, nargs='?', const=30, help='Triangular Moving Average')
    group.add_argument('--WMA', type=int, nargs='?', const=30, help='Weighted Moving Average')

    group.add_argument('--TSF', action="store_true", help='Time Series Forecast')

def handle_overlap_studies(args, kax, klines_df, close_times, display_count):
    all_name = ""
    if args.ABANDS: # ATR BANDS
        name = 'ABANDS'
        real = talib.ATR(klines_df["high"], klines_df["low"], klines_df["close"], timeperiod=14)
        emas = talib.EMA(klines_df["close"], timeperiod=26)
        kax.plot(close_times, emas[-display_count:], "b--", label=name)

        #cs = ['y', 'c', 'm', 'k']
        for idx, n in enumerate(args.ABANDS):
            """
            if idx >= len(cs):
                break
            c = cs[idx]
            """
            c = 'y'
            cl = c + '--'
            n = int(n)
            kax.plot(close_times, (emas+n*real)[-display_count:], cl, label=name+' upperband')
            kax.plot(close_times, (emas-n*real)[-display_count:], cl, label=name+' lowerband')

    if args.BANDS: # BANDS
        name = 'BANDS'
        emas = talib.EMA(klines_df["close"], timeperiod=26)
        kax.plot(close_times, emas[-display_count:], "b--", label=name)
        r= args.BANDS
        kax.plot(close_times, (1+r)*emas[-display_count:], 'y--', label=name+' upperband')
        kax.plot(close_times, (1-r)*emas[-display_count:], 'y--', label=name+' lowerband')

    # talib
    os_key = 'BBANDS'
    if args.BBANDS:
        upperband, middleband, lowerband = talib.BBANDS(klines_df["close"], timeperiod=5, nbdevup=2, nbdevdn=2, matype=0)
        kax.plot(close_times, upperband[-display_count:], "y", label=os_key+' upperband')
        kax.plot(close_times, middleband[-display_count:], "b", label=os_key+' middleband')
        kax.plot(close_times, lowerband[-display_count:], "y", label=os_key+' lowerband')

    os_key = 'DEMA'
    if args.DEMA:
        real = talib.DEMA(klines_df["close"], timeperiod=args.DEMA)
        kax.plot(close_times, real[-display_count:], "y", label=os_key)

    if args.EMA:
        name = 'EMA'
        all_name += "  %s%s" % (name, args.EMA)
        for idx, e_p in enumerate(args.EMA):
            if idx >= len(plot_colors):
                break
            e_p = int(e_p)
            emas = talib.EMA(klines_df["close"], timeperiod=e_p)
            kax.plot(close_times, emas[-display_count:], plot_colors[idx]+'--', label="%sEMA" % (e_p))

    if args.MA:
        name = 'MA'
        all_name += "  %s%s" % (name, args.MA)
        for idx, e_p in enumerate(args.MA):
            if idx >= len(plot_colors):
                break
            e_p = int(e_p)
            emas = talib.MA(klines_df["close"], timeperiod=e_p)
            kax.plot(close_times, emas[-display_count:], plot_colors[idx], label="%sMA" % (e_p))

    os_key = 'KAMA'
    if args.KAMA:
        all_name += "  %s%s" % (os_key, args.KAMA)
        for idx, e_p in enumerate(args.KAMA):
            if idx >= len(plot_colors):
                break
            e_p = int(e_p)
            real = talib.KAMA(klines_df["close"], timeperiod=e_p)
            kax.plot(close_times, real[-display_count:], plot_colors[idx]+'.', label="%s%s" % (e_p, os_key))

    os_key = 'MAMA'
    if args.MAMA:
        mama, fama = talib.MAMA(klines_df["close"], fastlimit=0, slowlimit=0)
        kax.plot(close_times, mama[-display_count:], "b", label=os_key)
        kax.plot(close_times, fama[-display_count:], "c", label=os_key)

    os_key = 'HT_TRENDLINE'
    if args.HT_TRENDLINE:
        real = talib.HT_TRENDLINE(klines_df["close"])
        kax.plot(close_times, real[-display_count:], "y", label=os_key)

    os_key = 'MIDPOINT'
    if args.MIDPOINT:
        real = talib.MIDPOINT(klines_df["close"], timeperiod=args.MIDPOINT)
        kax.plot(close_times, real[-display_count:], "y", label=os_key)

    os_key = 'MIDPRICE'
    if args.MIDPRICE:
        real = talib.MIDPRICE(klines_df["high"], klines_df["low"], timeperiod=args.MIDPRICE)
        kax.plot(close_times, real[-display_count:], "y", label=os_key)

    os_key = 'SAR'
    if args.SAR:
        real = talib.SAR(klines_df["high"], klines_df["low"], acceleration=0, maximum=0)
        kax.plot(close_times, real[-display_count:], "y", label=os_key)

    os_key = 'SAREXT'
    if args.SAREXT:
        real = talib.SAREXT(klines_df["high"], klines_df["low"],
            startvalue=0, offsetonreverse=0,
            accelerationinitlong=0, accelerationlong=0, accelerationmaxlong=0,
            accelerationinitshort=0, accelerationshort=0, accelerationmaxshort=0)
        kax.plot(close_times, real[-display_count:], "y", label=os_key)

    os_key = 'SMA'
    if args.SMA:
        real = talib.SMA(klines_df["close"], timeperiod=args.SMA)
        kax.plot(close_times, real[-display_count:], "y", label=os_key)

    os_key = 'T3'
    if args.T3:
        real = talib.T3(klines_df["close"], timeperiod=args.T3, vfactor=0)
        kax.plot(close_times, real[-display_count:], "y", label=os_key)

    os_key = 'TEMA'
    if args.TEMA:
        real = talib.TEMA(klines_df["close"], timeperiod=args.TEMA)
        kax.plot(close_times, real[-display_count:], "y", label=os_key)

    os_key = 'TRIMA'
    if args.TRIMA:
        real = talib.TRIMA(klines_df["close"], timeperiod=args.TRIMA)
        kax.plot(close_times, real[-display_count:], "y", label=os_key)

    os_key = 'WMA'
    if args.WMA:
        real = talib.WMA(klines_df["close"], timeperiod=args.WMA)
        kax.plot(close_times, real[-display_count:], "y", label=os_key)

    if args.TSF:
        name = 'TSF'
        real = talib.TSF(klines_df["close"], timeperiod=14)
        kax.plot(close_times, real[-display_count:], "y:", label=name)

    return all_name


def handle_overlap_studies2(args, apds, kdf):
    ss = []
    if args.ABANDS: # ATR BANDS
        name = 'ABANDS'
        tp_atr = 14
        tp_ema =  26
        real = talib.ATR(kdf["high"], kdf["low"], kdf["close"], timeperiod=tp_atr)
        emas = talib.EMA(kdf["close"], timeperiod=tp_ema)
        ss.append(('%s %s %s'%(name, tp_atr, tp_ema), emas, {'linestyle': 'dashdot', 'color': 'b'}))

        for n in args.ABANDS:
            ss.append(('%s upperband'%(name), emas+n*real, {'linestyle': 'dotted', 'color': 'y'}))
            ss.append(('%s lowerband'%(name), emas-n*real, {'linestyle': 'dotted', 'color': 'y'}))

    if args.BANDS: # BANDS
        name = 'BANDS'
        tp_ema = 26
        emas = talib.EMA(kdf["close"], timeperiod=tp_ema)
        ss.append(('%s %s'%(name, tp_ema), emas, {'linestyle': 'dashdot', 'color': 'b'}))
        r= args.BANDS
        ss.append(('%s upperband'%(name), (1+r)*emas, {'linestyle': 'dotted', 'color': 'y'}))
        ss.append(('%s lowerband'%(name), (1-r)*emas, {'linestyle': 'dotted', 'color': 'y'}))

    if args.BBANDS:
        name = 'BBANDS'
        tp = 5
        upperband, middleband, lowerband = talib.BBANDS(kdf["close"], timeperiod=tp, nbdevup=2, nbdevdn=2, matype=0)
        ss.append(('%s %s'%(name, tp), middleband, {'linestyle': 'dashdot', 'color': 'b'}))
        ss.append(('%s upperband'%(name), upperband, {'linestyle': 'dotted', 'color': 'y'}))
        ss.append(('%s lowerband'%(name), lowerband, {'linestyle': 'dotted', 'color': 'y'}))

    if args.DEMA:
        name = 'DEMA'
        tp = args.DEMA
        real = talib.DEMA(kdf["close"], timeperiod=tp)
        ss.append(('%s %s'%(name, tp), real, {}))

    if args.EMA:
        name = 'EMA'
        for tp in args.EMA:
            real = talib.EMA(kdf["close"], timeperiod=tp)
            ss.append(('%s %s'%(name, tp), real, {}))

    if args.MA:
        name = 'MA'
        for tp in args.MA:
            real = talib.MA(kdf["close"], timeperiod=tp)
            ss.append(('%s %s'%(name, tp), real, {}))

    if args.KAMA:
        name = 'KAMA'
        for tp in args.KAMA:
            real = talib.KAMA(kdf["close"], timeperiod=tp)
            ss.append(('%s %s'%(name, tp), real, {'linestyle': 'dotted'}))

    if args.MAMA:
        name = 'MAMA'
        mama, fama = talib.MAMA(kdf["close"], fastlimit=0, slowlimit=0)
        ss.append(('%s'%(name), mama, {'linestyle': 'dashed', 'color': 'b'}))
        ss.append(('%s'%(name), fama, {'linestyle': 'dashed', 'color': 'c'}))

    if args.HT_TRENDLINE:
        name = 'HT_TRENDLINE'
        real = talib.HT_TRENDLINE(kdf["close"])
        ss.append(('%s'%(name), real, {'color': 'y'}))

    if args.MIDPOINT:
        name = 'MIDPOINT'
        tp = args.MIDPOINT
        real = talib.MIDPOINT(kdf["close"], timeperiod=tp)
        ss.append(('%s %s'%(name, tp), real, {'color': 'y'}))

    if args.MIDPRICE:
        name = 'MIDPRICE'
        tp = args.MIDPRICE
        real = talib.MIDPRICE(kdf["high"], kdf["low"], timeperiod=tp)
        ss.append(('%s %s'%(name, tp), real, {'color': 'y'}))

    if args.SAR:
        name = 'SAR'
        real = talib.SAR(kdf["high"], kdf["low"], acceleration=0, maximum=0)
        ss.append(('%s'%(name), real, {'color': 'y'}))

    if args.SAREXT:
        name = 'SAREXT'
        real = talib.SAREXT(kdf["high"], kdf["low"],
            startvalue=0, offsetonreverse=0,
            accelerationinitlong=0, accelerationlong=0, accelerationmaxlong=0,
            accelerationinitshort=0, accelerationshort=0, accelerationmaxshort=0)
        ss.append(('%s'%(name), real, {'color': 'y'}))

    if args.SMA:
        name = 'SMA'
        tp = args.SMA
        real = talib.SMA(kdf["close"], timeperiod=tp)
        ss.append(('%s %s'%(name, tp), real, {'color': 'y'}))

    if args.T3:
        name = 'T3'
        tp = args.T3
        real = talib.T3(kdf["close"], timeperiod=tp, vfactor=0)
        ss.append(('%s %s'%(name, tp), real, {'color': 'y'}))

    if args.TEMA:
        name = 'TEMA'
        tp = args.TEMA
        real = talib.TEMA(kdf["close"], timeperiod=tp)
        ss.append(('%s %s'%(name, tp), real, {'color': 'y'}))

    if args.TRIMA:
        name = 'TRIMA'
        tp = args.TRIMA
        real = talib.TRIMA(kdf["close"], timeperiod=tp)
        ss.append(('%s %s'%(name, tp), real, {'color': 'y'}))

    if args.WMA:
        name = 'WMA'
        tp = args.WMA
        real = talib.WMA(kdf["close"], timeperiod=tp)
        ss.append(('%s %s'%(name, tp), real, {'color': 'y'}))

    if args.TSF:
        name = 'TSF'
        tp = 14
        real = talib.TSF(kdf["close"], timeperiod=tp)
        ss.append(('%s %s'%(name, tp), real, {'color': 'y'}))

    return ss

