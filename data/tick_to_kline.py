
import sys
sys.path.append('../')
import argparse
import json
from datetime import datetime, timedelta
import db.mongodb as md
import common.kline as kl
from exchange.exchange_factory import get_exchange_names, create_exchange
from db.mongodb import get_mongodb
from setup import *
import pandas as pd
import csv

tick_prefix = ''#'KQ.m@SHFE.rb.'
tick_key_last   = tick_prefix + 'last_price'
tick_key_highest = tick_prefix + 'highest'
tick_key_lowest = tick_prefix + 'lowest'
tick_key_volume = tick_prefix + 'volume'
tick_key_oi     = tick_prefix + 'open_interest'


def is_day(t):
    return 9 <= t.hour < 15

def is_night(t):
    if 21 <= t.hour:
        return True
    if t.hour < 3:
        return True
    return False

def not_a_day(pre_t, t):
    return pre_t.date() != t.date()


def init_k_hl(pre_tick, tick, open_time, open_price):
    last_price = tick[tick_key_last]
    day_highest = tick[tick_key_highest]
    day_lowest  = tick[tick_key_lowest]

    if pre_tick is None:
        return day_highest, day_lowest

    # first k of a day
    pre_tick_time = pre_tick.last_time
    if ( is_day(pre_tick_time) and
        (is_night(tick.last_time) or not_a_day(pre_tick_time, tick.last_time))
    ):
        return day_highest, day_lowest

    if tick.last_time == open_time:
        return last_price, last_price

    if pre_tick[tick_key_highest] < day_highest:
        high = day_highest
    else:
        high = max(open_price, last_price)

    if pre_tick[tick_key_lowest] > day_lowest:
        low = day_lowest
    else:
        low = min(open_price, last_price)
    return high, low


def update_k_hl(exchange, pre_tick, tick, k):
    k_key_high = exchange.kline_key_high
    k_key_low  = exchange.kline_key_low
    last_price = tick[tick_key_last]
    day_highest = tick[tick_key_highest]
    if day_highest > pre_tick[tick_key_highest]:
        k[k_key_high] = day_highest
    elif last_price > k[k_key_high]:
        k[k_key_high] = last_price

    day_lowest = tick[tick_key_lowest]
    if day_lowest < pre_tick[tick_key_lowest]:
        k[k_key_low] = day_lowest
    elif last_price < k[k_key_low]:
        k[k_key_low] = last_price


def update_k_book(exchange, tick, k, prex=''):
    k[prex + exchange.tick_key_bid_price1] = tick[exchange.tick_key_bid_price1]
    k[prex + exchange.tick_key_bid_size1]  = tick[exchange.tick_key_bid_size1]
    k[prex + exchange.tick_key_ask_price1] = tick[exchange.tick_key_ask_price1]
    k[prex + exchange.tick_key_ask_size1]  = tick[exchange.tick_key_ask_size1]


def update_k(exchange, pre_tick, tick, k, k_start_day_volume, need_book):
    update_k_hl(exchange, pre_tick, tick, k)
    k[exchange.kline_key_volume] = tick[tick_key_volume] - k_start_day_volume
    k[exchange.kline_key_close]  = tick[tick_key_last]
    k[exchange.kline_key_oi]     = tick[tick_key_oi]
    if need_book:
        update_k_book(exchange, tick, k, prex='close_')


def to_kline(exchange, interval, tick_df, need_book=False):
    interval_td = kl.get_interval_timedelta(interval)
    kls = []
    start_cost_time = datetime.now()
    day_reset_tick = None
    first_k_is_ok = True
    pre_tick = None
    k_start_day_volume = 0  # tick[tick_key_volume]
    k = None
    open_time = None
    for i, tick in tick_df.iterrows():
        #日重置tick
        #2025-01-15 18:41:22.158000000,1736937682158000000,nan,nan,nan,nan,0,0,0,nan,0,nan,0
        #2025-02-05 06:09:21.378000000,1738706961378000000,nan,nan,nan,nan,0,0,17958,nan,0,nan,0
        #2022-01-03 22:59:59.999500000,1641221999999500000,,,,,0,0,1388687,,0,,0
        if not tick[exchange.tick_key_bid_size1] and not tick[exchange.tick_key_ask_size1]:
            #print(f'day reset tick: {tick}')
            if k:
                kls.append(k)
                k = 0
            k_start_day_volume = 0
            day_reset_tick = tick
            pre_tick = tick
            continue

        if i == 0 and first_k_is_ok:
            open_tick = tick
            pre_tick  = tick
            first_k_is_ok = False


        tick_time = tick.last_time
        day_volume = tick[tick_key_volume]
        last_price = tick[tick_key_last]

        #每天开盘第一个tick,应该归入第一个k
        #2025-01-15 20:59:00.016000000,1736945940016000000,2975,2975,2975,2975.0,42,1249500,42,2975,9,2999,5
        #2025-02-05 08:59:00.028000000,1738717140028000000,3052,3052,3052,3052.0,33,1007160,17984,3052,9,3053,2
        #2021-08-26 20:58:53.876000000,1629982733876000000,,,,,0,0,65880,3633.0,1,3638.0,2
        if pre_tick.equals(day_reset_tick):
            open_tick = tick
            pre_tick  = tick
            continue

        #非日第一个tick，阶段性初始的59分钟也应该归入下一个k
        #2023-05-25 22:59:59.968000000,1685026799968000000,3417.0,3445.0,3412.0,3427.0,461457,15818607110,1388103,3416.0,404,3417.0,100
        #2023-05-26 08:59:00.036000000,1685062740036000000,3415.0,3445.0,3412.0,3427.0,466165,15979385310,1384352,3415.0,63,3416.0,186
        #2023-05-26 09:00:00.085000000,1685062800085000000,3416.0,3445.0,3412.0,3427.0,466733,15998779050,1384329,3414.0,20,3416.0,16
        #2023-08-28 08:59:00.003000000,1693184340003000000,4900.0,4900.0,4862.0,4882.0,11695,571045400,90699
        #i2401 2023-12-13 08:58:59.108000000,1702429139108000000,1014.0,1020.0,1012.5,1016.0,19221,1953768000.0,271021,1013.0,24,1014.5,4
        if tick_time.minute in [58,59] and tick_time.hour == 8:
            if k:
                kls.append(k)
                k = 0
            k_start_day_volume = pre_tick[tick_key_volume]
            open_tick = tick
            pre_tick  = tick
            continue

        #
        if k:
            #时间正好处于分割线上的tick，既是当前k的结束，也是下一个k的开始
            if tick_time <= close_time:
                #
                #2021-08-26 21:00:00.687000000,1629982800687000000,,,,,0,0,65880,3634.0,1,3636.0,1
                #2021-08-26 21:00:01.187001000,1629982801187001000,3636.0,3636.0,3634.0,3635.0,2,72700,65881,3633.0,7,3637.0,1
                if pd.isna(k[exchange.kline_key_open]):
                    k[exchange.kline_key_open] = last_price
                update_k(exchange, pre_tick, tick, k, k_start_day_volume, need_book)

            if tick_time >= close_time:
                kls.append(k)

                if tick_time > close_time:
                    if tick_time - kls[-1]["datetime_str"] > timedelta(minutes=9):
                        #非连续k，从当前tick计算
                        open_tick = tick
                    else:
                        #连续k，从前一个tick开始计算
                        open_tick = pre_tick
                    k_start_day_volume = pre_tick[tick_key_volume]
                else:
                    k_start_day_volume = day_volume
                    open_tick = tick
                    #2022-03-24 21:29:14.500000000,1648128554500000000,4441.0,4441.0,4378.0,4408.0,196931,8681317390,1182885,4440.0,117,4441.0,47
                    #2022-03-24 21:29:15.000000000,1648128555000000000,4441.0,4442.0,4378.0,4408.0,197055,8686824110,1182901,4440.0,132,4441.0,13
                    pre_tick = tick
                k = None

        if not k:
            pre_open_time = open_time
            open_time = kl.get_open_time(interval, tick_time)
            close_time = open_time + kl.get_interval_timedelta(interval)

            #tick更新跨越多个k，需要补上
            #2022-12-06 09:59:30.291000000,1670291970291000000,3661.0,3666.0,3627.0,3643.0,192930,7029281270,796661
            #2022-12-06 10:02:34.371000000,1670292154371000000,3661.0,3666.0,3627.0,3643.0,192932,7029354490,796661
            if len(kls) > 0:
                pre_k = kls[-1]
                pre_k_open_time = pre_k["datetime_str"]
                tk_td = tick_time - pre_k_open_time
                if interval_td < tk_td:
                    if tk_td < timedelta(minutes=9):
                        lack_end_time = open_time
                    else:
                        #若在分割点左右连续缺k，下面没补全超过分隔点的k，临时这样，后续改进
                        if pre_k_open_time.minute < 15:
                            lack_end_hour   = pre_k_open_time.hour
                            lack_end_minute = 15
                        elif pre_k_open_time.minute < 30:
                            lack_end_hour   = pre_k_open_time.hour
                            lack_end_minute = 30
                        else:
                            lack_end_hour   = pre_k_open_time.hour + 1
                            lack_end_minute = 0
                        lack_end_time = datetime(year=pre_k_open_time.year, month=pre_k_open_time.month, day=pre_k_open_time.day,
                                                hour=lack_end_hour, minute=lack_end_minute, second=0)

                    open_price = pre_k[exchange.kline_key_close]
                    lack_open_time = pre_open_time + interval_td
                    while lack_open_time < lack_end_time:
                        lack_k = {
                            "datetime_str": lack_open_time,
                            exchange.kline_key_open_time: exchange.get_data_ts_from_time(lack_open_time),
                            exchange.kline_key_open:  open_price,
                            exchange.kline_key_high:  open_price,
                            exchange.kline_key_low:   open_price,
                            exchange.kline_key_close: open_price,
                            exchange.kline_key_volume: 0,
                            exchange.kline_key_oi: pre_k[exchange.kline_key_oi]
                        }
                        if need_book:
                            update_k_book(exchange, open_tick, lack_k, prex='open_')
                            update_k_book(exchange, open_tick, lack_k, prex='close_')

                        lack_open_time += interval_td
                        if lack_open_time == tick_time:
                            update_k(exchange, pre_tick, tick, lack_k, k_start_day_volume, need_book)
                            k_start_day_volume = tick[tick_key_volume]
                            open_tick = tick
                            pre_tick = tick
                        kls.append(lack_k)

            open_price = open_tick.last_price
            if pd.isna(open_price):
                open_price = last_price
            k = {
                "datetime_str": open_time,
                exchange.kline_key_open_time: exchange.get_data_ts_from_time(open_time),
                exchange.kline_key_open:  open_price,
                exchange.kline_key_high:  open_price,
                exchange.kline_key_low:   open_price,
                exchange.kline_key_close: last_price,
                exchange.kline_key_volume: day_volume - k_start_day_volume,
                exchange.kline_key_oi: tick[tick_key_oi]
            }
            update_k_hl(exchange, pre_tick, tick, k)
            if need_book:
                update_k_book(exchange, open_tick, k, prex='open_')
                update_k_book(exchange, tick, k, prex='close_')

            sys.stdout.flush()
            sys.stdout.write(
                "{}  progress: {:%},  cost: {},  tick: {}\r".format(
                    " "*10,
                    (i+1)/len(tick_df),
                    datetime.now() - start_cost_time,
                    tick_time,
                )
            )

        pre_tick = tick

    kls.append(k)
    sys.stdout.write('\n')
    if not first_k_is_ok:
        kls = kls[1:]
    return kls 


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('-source', required=True, choices=get_exchange_names(), help='market data source')
    #parser.add_argument('-symbol', required=True, help='symbol: btc_usdt')
    parser.add_argument('-interval', required=True, help='kline types: 1m, 5m, 1h, 1d')
    parser.add_argument('-files', required=True, nargs='*', help='')
    parser.add_argument('--book', action="store_true", help='book info')
    args = parser.parse_args()

    exchange = create_exchange(args.source)
    if not exchange:
        print("market data source error!")
        exit(1)

    for tick_file_name in args.files:
        print('read file: ', tick_file_name)
        cost_start = datetime.now()
        tick_df = pd.read_csv(tick_file_name)
        print('  cost: %s'%(datetime.now()-cost_start))
        tick_df['last_time'] = tick_df[exchange.tick_key_time].apply(exchange.get_time_from_data_ts)
        print(tick_df)
        
        suffix = '.csv'
        index = tick_file_name.find('tick' + suffix)
        mid_name = args.interval + '_'
        if args.book:
            mid_name += 'book'
        kline_file_name = tick_file_name[:index] + mid_name + suffix
        print(kline_file_name)

        symbol = tick_file_name.split('_')[0]
        from common.tick_to_kline import KLineGenerator
        gen = KLineGenerator(
            symbol=symbol,           # 合约代码，如 'DCE.y2701'
            intervals=[args.interval],  # K线周期列表
            need_book=True,          # 是否需要买卖盘口数据
            exchange=exchange
        )
        dfs = gen.load_history(tick_df)
        kls_df = dfs[0]

        #kls = to_kline(exchange, args.interval, tick_df, args.book)
        #kls_df = pd.DataFrame(kls)

        kls_df.to_csv(kline_file_name, encoding='utf-8', index=False)

