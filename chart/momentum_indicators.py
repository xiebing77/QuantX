#!/usr/bin/python3

import pandas as pd
import talib

#import utils.indicator as ic

from .overlap_studies import plot_colors

def add_argument_momentum_indicators(parser):
    # Momentum Indicators
    group = parser.add_argument_group('Momentum Indicators')

    group.add_argument('--macd', action="store_true", help='Moving Average Convergence/Divergence')
    group.add_argument('--mr', action="store_true", help='MACD rate')
    group.add_argument('--kdj', action="store_true", help='kdj')

    # talib
    group = parser.add_argument_group('Momentum Indicators (TaLib)')
    group.add_argument('--ADX' , action="store_true", help='Average Directional Movement Index')
    group.add_argument('--ADXR', action="store_true", help='Average Directional Movement Index Rating')
    group.add_argument('--APO' , action="store_true", help='Absolute Price Oscillator')
    group.add_argument('--AROON', action="store_true", help='Aroon')
    group.add_argument('--AROONOSC', action="store_true", help='Aroon Oscillator')
    group.add_argument('--BOP', action="store_true", help='Balance Of Power')
    group.add_argument('--CCI', action="store_true", help='Commodity Channel Index')
    group.add_argument('--CMO', action="store_true", help='Chande Momentum Oscillator')
    group.add_argument('--DX', action="store_true", help='Directional Movement Index')
    group.add_argument('--MACD', action="store_true", help='Moving Average Convergence/Divergence')
    group.add_argument('--MACDEXT', action="store_true", help='MACD with controllable MA type')
    group.add_argument('--MACDFIX', action="store_true", help='Moving Average Convergence/Divergence Fix 12/26')
    group.add_argument('--MFI', action="store_true", help='Money Flow Index')
    group.add_argument('--MINUS_DI', action="store_true", help='Minus Directional Indicator')
    group.add_argument('--MINUS_DM', action="store_true", help='Minus Directional Movement')
    group.add_argument('--MOM', action="store_true", help='Momentum')
    group.add_argument('--PLUS_DI', action="store_true", help='Plus Directional Indicator')
    group.add_argument('--PLUS_DM', action="store_true", help='Plus Directional Movement')
    group.add_argument('--PPO', action="store_true", help='Percentage Price Oscillator')
    group.add_argument('--ROC', action="store_true", help='Rate of change : ((price/prevPrice)-1)*100')
    group.add_argument('--ROCP', action="store_true", help='Rate of change Percentage: (price-prevPrice)/prevPrice')
    group.add_argument('--ROCR', action="store_true", help='Rate of change ratio: (price/prevPrice)')
    group.add_argument('--ROCR100', action="store_true", help='Rate of change ratio 100 scale: (price/prevPrice)*100')
    group.add_argument('--RSI', type=int, nargs='*', help='Relative Strength Index')
    group.add_argument('--RSIRank', type=int, nargs='*', help='Relative Strength Index Rank')
    group.add_argument('--STOCH', action="store_true", help='Stochastic')
    group.add_argument('--STOCHF', action="store_true", help='Stochastic Fast')
    group.add_argument('--STOCHRSI', action="store_true", help='Stochastic Relative Strength Index')
    group.add_argument('--TRIX', type=int, nargs='*', help='1-day Rate-Of-Change (ROC) of a Triple Smooth EMA')
    group.add_argument('--ULTOSC', action="store_true", help='Ultimate Oscillator')
    group.add_argument('--WILLR', action="store_true", help="Williams' %%R")


def get_momentum_indicators_count(args):
    count = 0

    if args.macd: # macd
        count += 1
    if args.mr: # macd rate
        count += 1
    if args.kdj: # kdj
        count += 1

    if args.ADX: # 
        count += 1
    if args.ADXR: # 
        count += 1
    if args.APO: # 
        count += 1
    if args.AROON: # 
        count += 1
    if args.AROONOSC: # 
        count += 1
    if args.BOP: # 
        count += 1
    if args.CCI: # 
        count += 1
    if args.CMO: # 
        count += 1
    if args.DX: # 
        count += 1
    if args.MACD: # MACD
        count += 1
    if args.MACDEXT: # MACDEXT
        count += 1
    if args.MACDFIX: # MACDFIX
        count += 1
    if args.MFI: # 
        count += 1
    if args.MINUS_DI: # 
        count += 1
    if args.MINUS_DM: # 
        count += 1
    if args.MOM: # 
        count += 1
    if args.PLUS_DI: # 
        count += 1
    if args.PLUS_DM: # 
        count += 1
    if args.PPO: # 
        count += 1
    if args.ROC: # 
        count += 1
    if args.ROCP: # 
        count += 1
    if args.ROCR: # 
        count += 1
    if args.ROCR100: # 
        count += 1
    if args.RSI is not None: #
        count += 1
    if args.STOCH: # 
        count += 1
    if args.STOCHF: # 
        count += 1
    if args.STOCHRSI: # 
        count += 1
    if args.TRIX is not None: #
        count += 1
    if args.ULTOSC: # 
        count += 1
    if args.WILLR: # 
        count += 1

    return count


def handle_momentum_indicators(args, axes, i, klines_df, close_times, display_count):
    if args.macd: # macd
        name = 'macd'
        klines_df = ic.pd_macd(klines_df)
        difs = [round(a, 2) for a in klines_df["dif"]]
        deas = [round(a, 2) for a in klines_df["dea"]]
        macds = [round(a, 2) for a in klines_df["macd"]]
        i += 1
        axes[i].set_ylabel(name)
        axes[i].grid(True)
        axes[i].plot(close_times, difs[-display_count:], "y", label="dif")
        axes[i].plot(close_times, deas[-display_count:], "b", label="dea")
        axes[i].plot(close_times, macds[-display_count:], "r", drawstyle="steps", label="macd")

    if args.mr: # macd rate
        name = 'macd rate'
        klines_df = ic.pd_macd(klines_df)
        closes = klines_df["close"][-display_count:]
        closes = pd.to_numeric(closes)
        mrs = [round(a, 4) for a in (klines_df["macd"][-display_count:] / closes)]
        i += 1
        axes[i].set_ylabel(name)
        axes[i].grid(True)
        axes[i].plot(close_times, mrs, "r--", label="mr")

    if args.kdj: # kdj
        name = 'kdj'
        ks, ds, js = ic.pd_kdj(klines_df)
        i += 1
        axes[i].set_ylabel(name)
        axes[i].grid(True)
        axes[i].plot(close_times, ks[-display_count:], "y", label="k")
        axes[i].plot(close_times, ds[-display_count:], "b", label="d")
        axes[i].plot(close_times, js[-display_count:], "m", label="j")

    # talib
    if args.ADX: # ADX
        name = 'ADX'
        adxs = talib.ADX(klines_df["high"], klines_df["low"], klines_df["close"], timeperiod=14)
        i += 1
        axes[i].set_ylabel(name)
        axes[i].grid(True)
        axes[i].plot(close_times, adxs[-display_count:], "b", label=name)

    if args.ADXR: # ADXR
        name = 'ADXR'
        adxrs = talib.ADXR(klines_df["high"], klines_df["low"], klines_df["close"], timeperiod=14)
        i += 1
        axes[i].set_ylabel(name)
        axes[i].grid(True)
        axes[i].plot(close_times, adxrs[-display_count:], "r", label=name)

    if args.APO: # APO
        name = 'APO'
        real = talib.APO(klines_df["close"], fastperiod=12, slowperiod=26, matype=0)
        i += 1
        axes[i].set_ylabel(name)
        axes[i].grid(True)
        axes[i].plot(close_times, real[-display_count:], "y:", label=name)

    if args.AROON: # AROON
        name = 'AROON'
        aroondown, aroonup = talib.AROON(klines_df["high"], klines_df["low"], timeperiod=14)
        i += 1
        axes[i].set_ylabel(name)
        axes[i].grid(True)
        axes[i].plot(close_times, aroondown[-display_count:], "r:", label=name)
        axes[i].plot(close_times, aroonup[-display_count:], "g:", label=name)

    if args.AROONOSC: # AROONOSC
        name = 'AROONOSC'
        real = talib.AROONOSC(klines_df["high"], klines_df["low"], timeperiod=14)
        i += 1
        axes[i].set_ylabel(name)
        axes[i].grid(True)
        axes[i].plot(close_times, real[-display_count:], "y:", label=name)

    if args.BOP: # BOP
        name = 'BOP'
        real = talib.BOP(klines_df["open"], klines_df["high"], klines_df["low"], klines_df["close"])
        i += 1
        axes[i].set_ylabel(name)
        axes[i].grid(True)
        axes[i].plot(close_times, real[-display_count:], "y:", label=name)

    if args.CCI: # CCI
        name = 'CCI'
        real = talib.CCI(klines_df["high"], klines_df["low"], klines_df["close"], timeperiod=14)
        i += 1
        axes[i].set_ylabel(name)
        axes[i].grid(True)
        axes[i].plot(close_times, real[-display_count:], "y:", label=name)

    if args.CMO: # CMO
        name = 'CMO'
        real = talib.CMO(klines_df["close"], timeperiod=14)
        i += 1
        axes[i].set_ylabel(name)
        axes[i].grid(True)
        axes[i].plot(close_times, real[-display_count:], "y:", label=name)

    if args.DX: # DX
        name = 'DX'
        dxs = talib.DX(klines_df["high"], klines_df["low"], klines_df["close"], timeperiod=14)
        i += 1
        axes[i].set_ylabel(name)
        axes[i].grid(True)
        axes[i].plot(close_times, dxs[-display_count:], "y", label=name)

    if args.MACD: # MACD
        name = 'MACD'
        fastperiod = 12
        slowperiod = 26
        signalperiod = 9
        macd, macdsignal, macdhist = talib.MACD(klines_df["close"], fastperiod=fastperiod, slowperiod=slowperiod, signalperiod=signalperiod)
        i += 1
        axes[i].set_ylabel("%s(%s,%s,%s)"%(name, fastperiod, slowperiod, signalperiod))
        axes[i].grid(True)
        axes[i].plot(close_times, macd[-display_count:], "y", label="dif")
        axes[i].plot(close_times, macdsignal[-display_count:], "b", label="dea")
        axes[i].plot(close_times, macdhist[-display_count:], "r", drawstyle="steps", label="macd")

    if args.MACDEXT: # MACDEXT
        name = 'MACDEXT'
        fastperiod = 12
        slowperiod = 26
        signalperiod = 9
        macd, macdsignal, macdhist = talib.MACDEXT(klines_df["close"],
            fastperiod=fastperiod, fastmatype=0, slowperiod=slowperiod, slowmatype=0, signalperiod=signalperiod, signalmatype=0)
        i += 1
        axes[i].set_ylabel("%s(%s,%s,%s)"%(name, fastperiod, slowperiod, signalperiod))
        axes[i].grid(True)
        axes[i].plot(close_times, macd[-display_count:], "y", label="dif")
        axes[i].plot(close_times, macdsignal[-display_count:], "b", label="dea")
        axes[i].plot(close_times, macdhist[-display_count:], "r", drawstyle="steps", label="macd")

    if args.MACDFIX: # MACDFIX
        name = 'MACDFIX'
        signalperiod = 9
        macd, macdsignal, macdhist = talib.MACDFIX(klines_df["close"], signalperiod=signalperiod)
        i += 1
        axes[i].set_ylabel("%s(%s)"%(name, signalperiod))
        axes[i].grid(True)
        axes[i].plot(close_times, macd[-display_count:], "y", label="dif")
        axes[i].plot(close_times, macdsignal[-display_count:], "b", label="dea")
        axes[i].plot(close_times, macdhist[-display_count:], "r", drawstyle="steps", label="macd")

    if args.MFI: # 
        name = 'MFI'
        real = talib.MFI(klines_df["high"], klines_df["low"], klines_df["close"], klines_df["volume"])
        i += 1
        axes[i].set_ylabel(name)
        axes[i].grid(True)
        axes[i].plot(close_times, real[-display_count:], "y:", label=name)

    if args.MINUS_DI: # 
        name = 'MINUS_DI'
        real = talib.MINUS_DI(klines_df["high"], klines_df["low"], klines_df["close"], timeperiod=14)
        i += 1
        axes[i].set_ylabel(name)
        axes[i].grid(True)
        axes[i].plot(close_times, real[-display_count:], "y:", label=name)

    if args.MINUS_DM: # 
        name = 'MINUS_DM'
        real = talib.MINUS_DM(klines_df["high"], klines_df["low"], timeperiod=14)
        i += 1
        axes[i].set_ylabel(name)
        axes[i].grid(True)
        axes[i].plot(close_times, real[-display_count:], "y:", label=name)

    if args.MOM: # 
        name = 'MOM'
        real = talib.MOM(klines_df["close"], timeperiod=10)
        i += 1
        axes[i].set_ylabel(name)
        axes[i].grid(True)
        axes[i].plot(close_times, real[-display_count:], "y:", label=name)

    if args.PLUS_DI: # 
        name = 'PLUS_DI'
        real = talib.PLUS_DI(klines_df["high"], klines_df["low"], klines_df["close"], timeperiod=14)
        i += 1
        axes[i].set_ylabel(name)
        axes[i].grid(True)
        axes[i].plot(close_times, real[-display_count:], "y:", label=name)

    if args.PLUS_DM: # 
        name = 'PLUS_DM'
        real = talib.PLUS_DM(klines_df["high"], klines_df["low"], timeperiod=14)
        i += 1
        axes[i].set_ylabel(name)
        axes[i].grid(True)
        axes[i].plot(close_times, real[-display_count:], "y:", label=name)

    if args.PPO: # 
        name = 'PPO'
        real = talib.PPO(klines_df["close"], fastperiod=12, slowperiod=26, matype=0)
        i += 1
        axes[i].set_ylabel(name)
        axes[i].grid(True)
        axes[i].plot(close_times, real[-display_count:], "y:", label=name)

    if args.ROC: # 
        name = 'ROC'
        real = talib.ROC(klines_df["close"], timeperiod=10)
        i += 1
        axes[i].set_ylabel(name)
        axes[i].grid(True)
        axes[i].plot(close_times, real[-display_count:], "y:", label=name)

    if args.ROCP: # 
        name = 'ROCP'
        real = talib.ROCP(klines_df["close"], timeperiod=10)
        i += 1
        axes[i].set_ylabel(name)
        axes[i].grid(True)
        axes[i].plot(close_times, real[-display_count:], "k:", label=name)

    if args.ROCR: # 
        name = 'ROCR'
        real = talib.ROCR(klines_df["close"], timeperiod=10)
        i += 1
        axes[i].set_ylabel(name)
        axes[i].grid(True)
        axes[i].plot(close_times, real[-display_count:], "m:", label=name)

    if args.ROCR100: # 
        name = 'ROCR100'
        real = talib.ROCR100(klines_df["close"], timeperiod=10)
        i += 1
        axes[i].set_ylabel(name)
        axes[i].grid(True)
        axes[i].plot(close_times, real[-display_count:], "b:", label=name)

    if args.RSI is not None: # RSI
        name = 'RSI'
        i += 1
        axes[i].grid(True)

        if len(args.RSI) == 0:
            tps = [14]
        else:
            tps = args.RSI
        cs = ["r", "y", "b"]
        axes[i].set_ylabel("%s %s"%(name, tps))
        for idx, tp in enumerate(tps):
            rsis = talib.RSI(klines_df["close"], timeperiod=tp)
            rsis = [round(a, 3) for a in rsis][-display_count:]
            axes[i].plot(close_times, rsis, cs[idx], label="rsi")

            linetype = "."
            axes[i].plot(close_times, [90]*len(rsis), linetype, color='r')
            axes[i].plot(close_times, [80]*len(rsis), linetype, color='r')
            axes[i].plot(close_times, [50]*len(rsis), linetype, color='r')
            axes[i].plot(close_times, [40]*len(rsis), linetype, color='r')

            linetype = "."
            axes[i].plot(close_times, [65]*len(rsis), linetype, color='b')
            axes[i].plot(close_times, [55]*len(rsis), linetype, color='b')
            axes[i].plot(close_times, [30]*len(rsis), linetype, color='b')
            axes[i].plot(close_times, [20]*len(rsis), linetype, color='b')

    if args.STOCH: # STOCH
        name = 'STOCH'
        slowk, slowd = talib.STOCH(klines_df["high"], klines_df["low"], klines_df["close"],
            fastk_period=5, slowk_period=3, slowk_matype=0, slowd_period=3, slowd_matype=0)
        i += 1
        axes[i].set_ylabel(name)
        axes[i].grid(True)
        axes[i].plot(close_times, slowk[-display_count:], "y", label="slowk")
        axes[i].plot(close_times, slowd[-display_count:], "b", label="slowd")

    if args.STOCHF: # 
        name = 'STOCHF'
        fastk, fastd = talib.STOCHF(klines_df["high"], klines_df["low"], klines_df["close"],
            fastk_period=5, fastd_period=3, fastd_matype=0)
        i += 1
        axes[i].set_ylabel(name)
        axes[i].grid(True)
        axes[i].plot(close_times, fastk[-display_count:], "b", label="fastk")
        axes[i].plot(close_times, fastd[-display_count:], "y", label="fastd")

    if args.STOCHRSI: # 
        name = 'STOCHRSI'
        fastk, fastd = talib.STOCHRSI(klines_df["close"],
            timeperiod=14, fastk_period=5, fastd_period=3, fastd_matype=0)
        i += 1
        axes[i].set_ylabel(name)
        axes[i].grid(True)
        axes[i].plot(close_times, fastk[-display_count:], "b", label="fastk")
        axes[i].plot(close_times, fastd[-display_count:], "y", label="fastd")

    if args.TRIX is not None: #
        name = 'TRIX'
        i += 1
        axes[i].grid(True)
        if len(args.TRIX) == 0:
            tps = [30]
        else:
            tps = args.TRIX
        axes[i].set_ylabel("%s %s"%(name, tps))

        for idx, tp in enumerate(tps):
            real = talib.TRIX(klines_df["close"], timeperiod=tp)
            axes[i].plot(close_times, real[-display_count:], plot_colors[idx], label=name)

    if args.ULTOSC: # 
        name = 'ULTOSC'
        real = talib.ULTOSC(klines_df["high"], klines_df["low"], klines_df["close"], timeperiod1=7, timeperiod2=14, timeperiod3=28)
        i += 1
        axes[i].set_ylabel(name)
        axes[i].grid(True)
        axes[i].plot(close_times, real[-display_count:], "y:", label=name)

    if args.WILLR:
        tp = 14
        name = 'WILLR %s' % tp
        real = talib.WILLR(klines_df["high"], klines_df["low"], klines_df["close"], timeperiod=tp)
        i += 1
        axes[i].set_ylabel(name)
        axes[i].grid(True)
        axes[i].plot(close_times, real[-display_count:], "y:", label=name)

def handle_momentum_indicators2(args, kdf):
    sss = []
    '''
    if args.macd: # macd
        name = 'macd'
        kdf = ic.pd_macd(kdf)
        difs = [round(a, 2) for a in kdf["dif"]]
        deas = [round(a, 2) for a in kdf["dea"]]
        macds = [round(a, 2) for a in kdf["macd"]]
        sss.append([('dif', difs, {'color': 'm'}),
                    ('dea', deas, {'color': 'y'}),
                    (name, macds, {'type': 'bar', 'color': 'g'})])

    if args.mr: # macd rate
        name = 'macd rate'
        kdf = ic.pd_macd(kdf)
        closes = kdf["close"]
        closes = pd.to_numeric(closes)
        mrs = [round(a, 4) for a in (kdf["macd"] / closes)]
        sss.append([(name, mrr, {'color': 'r'})])

    if args.kdj: # kdj
        name = 'kdj'
        ks, ds, js = ic.pd_kdj(kdf)
        sss.append([('k', ks, {'color': 'y'}),
                    ('d', ds, {'color': 'b'}),
                    ('j', js, {'color': 'm'})])
    '''

    # talib
    if args.ADX: # ADX
        name = 'ADX'
        tp = 14
        real = talib.ADX(kdf["high"], kdf["low"], kdf["close"], timeperiod=tp)
        sss.append([('%s %s'%(name, tp), real, {})])

    if args.ADXR: # ADXR
        name = 'ADXR'
        tp = 14
        real = talib.ADXR(kdf["high"], kdf["low"], kdf["close"], timeperiod=tp)
        sss.append([('%s %s'%(name, tp), real, {})])

    if args.APO: # APO
        name = 'APO'
        fp = 12
        sp = 26
        real = talib.APO(kdf["close"], fastperiod=fp, slowperiod=sp, matype=0)
        sss.append([('%s %s %s'%(name, fp, sp), real, {})])

    if args.AROON: # AROON
        name = 'AROON'
        tp = 14
        aroondown, aroonup = talib.AROON(kdf["high"], kdf["low"], timeperiod=tp)
        sss.append([('%s %s down'%(name, tp), aroondown, {'color': 'r'}),
                    ('%s %s up'%(name, tp), aroonup, {'color': 'g'})])

    if args.AROONOSC: # AROONOSC
        name = 'AROONOSC'
        tp = 14
        real = talib.AROONOSC(kdf["high"], kdf["low"], timeperiod=tp)
        sss.append([('%s %s'%(name, tp), real, {})])

    if args.BOP: # BOP
        name = 'BOP'
        real = talib.BOP(kdf["open"], kdf["high"], kdf["low"], kdf["close"])
        sss.append([('%s'%(name), real, {})])

    if args.CCI: # CCI
        name = 'CCI'
        tp = 14
        real = talib.CCI(kdf["high"], kdf["low"], kdf["close"], timeperiod=tp)
        sss.append([('%s %s'%(name, tp), real, {})])

    if args.CMO: # CMO
        name = 'CMO'
        tp = 14
        real = talib.CMO(kdf["close"], timeperiod=tp)
        sss.append([('%s %s'%(name, tp), real, {})])

    if args.DX: # DX
        name = 'DX'
        tp = 14
        real = talib.DX(kdf["high"], kdf["low"], kdf["close"], timeperiod=tp)
        sss.append([('%s %s'%(name, tp), real, {})])

    if args.MACD: # MACD
        name = 'MACD'
        fastperiod = 12
        slowperiod = 26
        signalperiod = 9
        macd, macdsignal, macdhist = talib.MACD(kdf["close"], fastperiod=fastperiod, slowperiod=slowperiod, signalperiod=signalperiod)
        sss.append([('dif', macd, {'color': 'm'}),
                    ('dea', macdsignal, {'color': 'y'}),
                    (name, macdhist, {'type': 'bar', 'color': 'g'})])

    if args.MACDEXT: # MACDEXT
        name = 'MACDEXT'
        fastperiod = 12
        slowperiod = 26
        signalperiod = 9
        macd, macdsignal, macdhist = talib.MACDEXT(kdf["close"],
            fastperiod=fastperiod, fastmatype=0, slowperiod=slowperiod, slowmatype=0, signalperiod=signalperiod, signalmatype=0)
        sss.append([('dif', macd, {'color': 'm'}),
                    ('dea', macdsignal, {'color': 'y'}),
                    (name, macdhist, {'type': 'bar', 'color': 'g'})])

    if args.MACDFIX: # MACDFIX
        name = 'MACDFIX'
        signalperiod = 9
        macd, macdsignal, macdhist = talib.MACDFIX(kdf["close"], signalperiod=signalperiod)
        sss.append([('dif', macd, {'color': 'm'}),
                    ('dea', macdsignal, {'color': 'y'}),
                    (name, macdhist, {'type': 'bar', 'color': 'g'})])

    if args.MFI: # 
        name = 'MFI'
        real = talib.MFI(kdf["high"], kdf["low"], kdf["close"], kdf["volume"])
        sss.append([('%s'%(name), real, {})])

    if args.MINUS_DI: # 
        name = 'MINUS_DI'
        tp = 14
        real = talib.MINUS_DI(kdf["high"], kdf["low"], kdf["close"], timeperiod=tp)
        sss.append([('%s %s'%(name, tp), real, {})])

    if args.MINUS_DM: # 
        name = 'MINUS_DM'
        tp = 14
        real = talib.MINUS_DM(kdf["high"], kdf["low"], timeperiod=tp)
        sss.append([('%s %s'%(name, tp), real, {})])

    if args.MOM: # 
        name = 'MOM'
        tp = 10
        real = talib.MOM(kdf["close"], timeperiod=tp)
        sss.append([('%s %s'%(name, tp), real, {})])

    if args.PLUS_DI: # 
        name = 'PLUS_DI'
        tp = 14
        real = talib.PLUS_DI(kdf["high"], kdf["low"], kdf["close"], timeperiod=tp)
        sss.append([('%s %s'%(name, tp), real, {})])

    if args.PLUS_DM: # 
        name = 'PLUS_DM'
        tp = 14
        real = talib.PLUS_DM(kdf["high"], kdf["low"], timeperiod=tp)
        sss.append([('%s %s'%(name, tp), real, {})])

    if args.PPO: # 
        name = 'PPO'
        fp = 12
        sp = 26
        real = talib.PPO(kdf["close"], fastperiod=fp, slowperiod=sp, matype=0)
        sss.append([('%s %s %s'%(name, fp, sp), real, {})])

    if args.ROC: # 
        name = 'ROC'
        tp = 10
        real = talib.ROC(kdf["close"], timeperiod=tp)
        sss.append([('%s %s'%(name, tp), real, {})])

    if args.ROCP: # 
        name = 'ROCP'
        tp = 10
        real = talib.ROCP(kdf["close"], timeperiod=tp)
        sss.append([('%s %s'%(name, tp), real, {})])

    if args.ROCR: # 
        name = 'ROCR'
        tp = 10
        real = talib.ROCR(kdf["close"], timeperiod=tp)
        sss.append([('%s %s'%(name, tp), real, {})])

    if args.ROCR100: # 
        name = 'ROCR100'
        tp = 10
        real = talib.ROCR100(kdf["close"], timeperiod=tp)
        sss.append([('%s %s'%(name, tp), real, {})])

    if args.RSI is not None: # RSI
        name = 'RSI'
        if len(args.RSI) == 0:
            tps = [14]
        else:
            tps = args.RSI

        ss = []
        for idx, tp in enumerate(tps):
            rsis = talib.RSI(kdf["close"], timeperiod=tp)
            rsis = [round(a, 3) for a in rsis]
            ss.append(('%s_%s'%(name, tp), rsis, {}))

        if args.RSIRank:
            for rsi in args.RSIRank:
                ss.append(('%s_%s'%(name, rsi), [rsi]*len(kdf), {}))
        sss.append(ss)

    if args.STOCH: # STOCH
        name = 'STOCH'
        slowk, slowd = talib.STOCH(kdf["high"], kdf["low"], kdf["close"],
            fastk_period=5, slowk_period=3, slowk_matype=0, slowd_period=3, slowd_matype=0)
        sss.append([('STOCH', slowk-slowd, {})])
        sss.append([('STOCH-k', slowk, {})])
        sss.append([('STOCH-d', slowd, {})])

    if args.STOCHF: # 
        name = 'STOCHF'
        fastk, fastd = talib.STOCHF(kdf["high"], kdf["low"], kdf["close"],
            fastk_period=5, fastd_period=3, fastd_matype=0)
        sss.append([('STOCHF', fastk-fastd, {})])
        sss.append([('STOCHF-k', fastk, {})])
        sss.append([('STOCHF-d', fastd, {})])

    if args.STOCHRSI: # 
        name = 'STOCHRSI'
        fastk, fastd = talib.STOCHRSI(kdf["close"],
            timeperiod=14, fastk_period=5, fastd_period=3, fastd_matype=0)
        sss.append([('STOCHRSI', fastk-fastd, {})])
        sss.append([('STOCHRSI-k', fastk, {})])
        sss.append([('STOCHRSI-d', fastd, {})])

    if args.TRIX is not None: #
        name = 'TRIX'
        if len(args.TRIX) == 0:
            tps = [30]
        else:
            tps = args.TRIX

        ss = []
        for idx, tp in enumerate(tps):
            real = talib.TRIX(kdf["close"], timeperiod=tp)
            ss.append(('%s_%s'%(name, tp), real, {}))
        sss.append(ss)

    if args.ULTOSC: # 
        name = 'ULTOSC'
        tp1 = 7
        tp2 = 14
        tp3 =28
        real = talib.ULTOSC(kdf["high"], kdf["low"], kdf["close"],
                            timeperiod1=tp1, timeperiod2=tp2, timeperiod3=tp3)
        sss.append([('%s %s %s %s'%(name, tp1, tp2, tp3), real, {})])

    if args.WILLR:
        name = 'WILLR'
        tp = 14
        real = talib.WILLR(kdf["high"], kdf["low"], kdf["close"], timeperiod=tp)
        sss.append([('%s %s'%(name, tp), real, {})])

    return sss