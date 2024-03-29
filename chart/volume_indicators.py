#!/usr/bin/python3

import pandas as pd
import talib

#import utils.indicator as ic


def add_argument_volume_indicators(parser):
    # Volume Indicators

    # talib
    group = parser.add_argument_group('Volume Indicators (TaLib)')
    group.add_argument('--AD'   , action="store_true", help='Chaikin A/D Line')
    group.add_argument('--ADOSC', action="store_true", help='Chaikin A/D Oscillator')
    group.add_argument('--OBV'  , action="store_true", help='On Balance Volume')


def get_volume_indicators_count(args):
    count = 0

    if args.AD: # 
        count += 1
    if args.ADOSC: # 
        count += 1
    if args.OBV: # 
        count += 1

    return count


def handle_volume_indicators(args, axes, i, klines_df, close_times, display_count):
    # talib
    if args.AD: # AD
        name = 'AD'
        real = talib.AD(klines_df["high"], klines_df["low"], klines_df["close"], klines_df["volume"])
        i += 1
        axes[i].set_ylabel(name)
        axes[i].grid(True)
        axes[i].plot(close_times, real[-display_count:], "y:", label=name)

    if args.ADOSC: # ADOSC
        name = 'ADOSC'
        real = talib.ADOSC(klines_df["high"], klines_df["low"], klines_df["close"], klines_df["volume"], fastperiod=3, slowperiod=10)
        i += 1
        axes[i].set_ylabel(name)
        axes[i].grid(True)
        axes[i].plot(close_times, real[-display_count:], "y:", label=name)

    if args.OBV: # OBV
        name = 'OBV'
        real = talib.OBV(klines_df["close"], klines_df["volume"])
        i += 1
        axes[i].set_ylabel(name)
        axes[i].grid(True)
        axes[i].plot(close_times, real[-display_count:], "y:", label=name)


def handle_volume_indicators2(args, kdf):
    # talib
    sss = []
    if args.AD:
        real = talib.AD(kdf["high"], kdf["low"], kdf["close"], kdf["volume"])
        sss.append([('AD', real, {})])
    if args.ADOSC:
        real = talib.ADOSC(kdf["high"], kdf["low"], kdf["close"], kdf["volume"], fastperiod=3, slowperiod=10)
        sss.append([('ADOSC', real, {})])
    if args.OBV:
        real = talib.OBV(kdf["close"], kdf["volume"])
        sss.append([('OBV', real, {})])
    return sss

