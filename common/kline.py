#!/usr/bin/python

from datetime import datetime, timedelta, time


KLINE_DATA_TYPE_LIST = 0
KLINE_DATA_TYPE_JSON = 1

KLINE_KEY_OPEN_TIME  = "open_time"
KLINE_KEY_CLOSE_TIME = "close_time"
KLINE_KEY_OPEN       = "open"
KLINE_KEY_CLOSE      = "close"
KLINE_KEY_HIGH       = "high"
KLINE_KEY_LOW        = "low"
KLINE_KEY_VOLUME     = "volume"

KLINE_INTERVAL_1SECOND  = '1s'
KLINE_INTERVAL_5SECOND  = '5s'
KLINE_INTERVAL_10SECOND = '10s'
KLINE_INTERVAL_15SECOND = '15s'
KLINE_INTERVAL_20SECOND = '20s'
KLINE_INTERVAL_30SECOND = '30s'

KLINE_INTERVAL__25SECOND =  '25s'
KLINE_INTERVAL__36SECOND =  '36s'
KLINE_INTERVAL__45SECOND =  '45s'
KLINE_INTERVAL__50SECOND =  '50s'
KLINE_INTERVAL__75SECOND =  '75s'
KLINE_INTERVAL__90SECOND =  '90s'
KLINE_INTERVAL_100SECOND = '100s'
KLINE_INTERVAL_150SECOND = '150s'
KLINE_INTERVAL_225SECOND = '225s'
KLINE_INTERVAL_450SECOND = '450s'

KLINE_INTERVAL_1MINUTE = '1m'
KLINE_INTERVAL_3MINUTE = '3m'
KLINE_INTERVAL_5MINUTE = '5m'
KLINE_INTERVAL_15MINUTE = '15m'
KLINE_INTERVAL_30MINUTE = '30m'

KLINE_INTERVAL_1HOUR = '1h'
KLINE_INTERVAL_2HOUR = '2h'
KLINE_INTERVAL_4HOUR = '4h'
KLINE_INTERVAL_6HOUR = '6h'
KLINE_INTERVAL_8HOUR = '8h'
KLINE_INTERVAL_12HOUR = '12h'

KLINE_INTERVAL_1DAY = '1d'
KLINE_INTERVAL_3DAY = '3d'

KLINE_INTERVAL_1WEEK = '1w'

KLINE_INTERVAL_1MONTH = '1M'

SECONDS_MINUTE = 60
SECONDS_HOUR = 60 * SECONDS_MINUTE
SECONDS_DAY = 24 * SECONDS_HOUR

def get_kline_collection(symbol, interval):
    return "kline_%s_%s" % (symbol, interval)

def calc_open_time_by_seconds(interval, dt):
    hour_seconds = 60 * 60
    interval_seconds = int(get_interval_timedelta(interval).total_seconds())
    #interval_seconds = get_interval_seconds(interval)
    if interval_seconds > hour_seconds:
        return None
    seconds = dt.minute * 60 + dt.second
    open_seconds = (seconds // interval_seconds) * interval_seconds
    #open_seconds = seconds - seconds % interval_seconds
    open_minute = open_seconds // 60
    open_second = open_seconds  % 60
    return datetime.combine(dt.date(), time(dt.hour, open_minute, open_second))

def get_open_time(interval, dt):
    if interval == KLINE_INTERVAL_1SECOND:
        return datetime.combine(dt.date(), time(dt.hour, dt.minute, dt.second))
    elif interval == KLINE_INTERVAL_5SECOND:
        open_second = (dt.second // 5) * 5
        return datetime.combine(dt.date(), time(dt.hour, dt.minute, open_second))
    elif interval == KLINE_INTERVAL_10SECOND:
        open_second = (dt.second // 10) * 10
        return datetime.combine(dt.date(), time(dt.hour, dt.minute, open_second))
    elif interval == KLINE_INTERVAL_15SECOND:
        open_second = (dt.second // 15) * 15
        return datetime.combine(dt.date(), time(dt.hour, dt.minute, open_second))
    elif interval == KLINE_INTERVAL_20SECOND:
        open_second = (dt.second // 20) * 20
        return datetime.combine(dt.date(), time(dt.hour, dt.minute, open_second))
    elif interval == KLINE_INTERVAL_30SECOND:
        open_second = (dt.second // 30) * 30
        return datetime.combine(dt.date(), time(dt.hour, dt.minute, open_second))

    elif interval in [
        KLINE_INTERVAL__25SECOND,
        KLINE_INTERVAL__36SECOND,
        KLINE_INTERVAL__45SECOND,
        KLINE_INTERVAL__50SECOND,
        KLINE_INTERVAL__75SECOND,
        KLINE_INTERVAL__90SECOND,
        KLINE_INTERVAL_100SECOND,
        KLINE_INTERVAL_150SECOND,
        KLINE_INTERVAL_225SECOND,
        KLINE_INTERVAL_450SECOND
    ]:
        return calc_open_time_by_seconds(interval, dt)

    elif interval == KLINE_INTERVAL_1MINUTE:
        return datetime.combine(dt.date(), time(dt.hour, dt.minute, 0))
    elif interval == KLINE_INTERVAL_3MINUTE:
        open_minute = (dt.minute // 3) * 3
        return datetime.combine(dt.date(), time(dt.hour, open_minute, 0))
    elif interval == KLINE_INTERVAL_5MINUTE:
        open_minute = (dt.minute // 5) * 5
        return datetime.combine(dt.date(), time(dt.hour, open_minute, 0))
    elif interval == KLINE_INTERVAL_15MINUTE:
        open_minute = (dt.minute // 15) * 15
        return datetime.combine(dt.date(), time(dt.hour, open_minute, 0))
    elif interval == KLINE_INTERVAL_30MINUTE:
        if dt.minute < 30:
            open_minute = 0
        else:
            open_minute = 30
        return datetime.combine(dt.date(), time(dt.hour, open_minute, 0))

    elif interval == KLINE_INTERVAL_1HOUR:
        open_hour = dt.hour
        return datetime.combine(dt.date(), time(open_hour, 0, 0))
    elif interval == KLINE_INTERVAL_2HOUR:
        open_hour = (dt.hour // 2) * 2
        return datetime.combine(dt.date(), time(open_hour, 0, 0))
    elif interval == KLINE_INTERVAL_4HOUR:
        open_hour = (dt.hour // 4) * 4
        return datetime.combine(dt.date(), time(open_hour, 0, 0))

    elif interval == KLINE_INTERVAL_6HOUR:
        if dt.hour < 2:
            return datetime.combine(dt.date() - timedelta(days=1), time(20, 0, 0))
        elif dt.hour < 8:
            return datetime.combine(dt.date(), time(2, 0, 0))
        elif dt.hour < 14:
            return datetime.combine(dt.date(), time(8, 0, 0))
        elif dt.hour < 20:
            return datetime.combine(dt.date(), time(14, 0, 0))
        else:
            return datetime.combine(dt.date(), time(20, 0, 0))

    elif interval == KLINE_INTERVAL_8HOUR:
        open_hour = (dt.hour // 8) * 8
        return datetime.combine(dt.date(), time(open_hour, 0, 0))

    elif interval == KLINE_INTERVAL_12HOUR:
        if dt.hour < 8:
            return datetime.combine(dt.date() - timedelta(days=1), time(20, 0, 0))
        elif dt.hour >= 20:
            return datetime.combine(dt.date(), time(20, 0, 0))
        else:
            return datetime.combine(dt.date(), time(8, 0, 0))

    elif interval == KLINE_INTERVAL_1DAY:
        if dt.hour < 8:
            return datetime.combine(dt.date() - timedelta(days=1), time(8, 0, 0))
        else:
            return datetime.combine(dt.date(), time(8, 0, 0))
    else:
        return None

def get_interval_timedelta(interval):
    if interval == KLINE_INTERVAL_1SECOND:
        return timedelta(seconds=1)
    elif interval == KLINE_INTERVAL_5SECOND:
        return timedelta(seconds=5)
    elif interval == KLINE_INTERVAL_10SECOND:
        return timedelta(seconds=10)
    elif interval == KLINE_INTERVAL_15SECOND:
        return timedelta(seconds=15)
    elif interval == KLINE_INTERVAL_20SECOND:
        return timedelta(seconds=20)
    elif interval == KLINE_INTERVAL_30SECOND:
        return timedelta(seconds=30)

    elif interval == KLINE_INTERVAL__25SECOND:
        return timedelta(seconds=25)
    elif interval == KLINE_INTERVAL__36SECOND:
        return timedelta(seconds=36)
    elif interval == KLINE_INTERVAL__45SECOND:
        return timedelta(seconds=45)
    elif interval == KLINE_INTERVAL__50SECOND:
        return timedelta(seconds=50)
    elif interval == KLINE_INTERVAL__75SECOND:
        return timedelta(minutes=1, seconds=15)
    elif interval == KLINE_INTERVAL__90SECOND:
        return timedelta(minutes=1, seconds=30)
    elif interval == KLINE_INTERVAL_100SECOND:
        return timedelta(minutes=1, seconds=40)
    elif interval == KLINE_INTERVAL_150SECOND:
        return timedelta(minutes=2, seconds=30)
    elif interval == KLINE_INTERVAL_225SECOND:
        return timedelta(minutes=3, seconds=45)
    elif interval == KLINE_INTERVAL_450SECOND:
        return timedelta(minutes=7, seconds=30)

    elif interval == KLINE_INTERVAL_1MINUTE:
        return timedelta(minutes=1)
    elif interval == KLINE_INTERVAL_3MINUTE:
        return timedelta(minutes=3)
    elif interval == KLINE_INTERVAL_5MINUTE:
        return timedelta(minutes=5)
    elif interval == KLINE_INTERVAL_15MINUTE:
        return timedelta(minutes=15)
    elif interval == KLINE_INTERVAL_30MINUTE:
        return timedelta(minutes=30)

    elif interval == KLINE_INTERVAL_1HOUR:
        return timedelta(hours=1)
    elif interval == KLINE_INTERVAL_2HOUR:
        return timedelta(hours=2)
    elif interval == KLINE_INTERVAL_4HOUR:
        return timedelta(hours=4)
    elif interval == KLINE_INTERVAL_6HOUR:
        return timedelta(hours=6)
    elif interval == KLINE_INTERVAL_8HOUR:
        return timedelta(hours=8)
    elif interval == KLINE_INTERVAL_12HOUR:
        return timedelta(hours=12)

    elif interval == KLINE_INTERVAL_1DAY:
        return timedelta(days=1)

    else:
        return None

def get_interval_seconds(interval):
    if interval == KLINE_INTERVAL_1SECOND:
        return 1
    if interval == KLINE_INTERVAL_5SECOND:
        return 5
    if interval == KLINE_INTERVAL_10SECOND:
        return 10
    if interval == KLINE_INTERVAL_15SECOND:
        return 15
    if interval == KLINE_INTERVAL_20SECOND:
        return 20
    if interval == KLINE_INTERVAL_30SECOND:
        return 30

    if interval == KLINE_INTERVAL__25SECOND:
        return 25
    if interval == KLINE_INTERVAL__36SECOND:
        return 36
    if interval == KLINE_INTERVAL__45SECOND:
        return 45
    if interval == KLINE_INTERVAL__50SECOND:
        return 50
    if interval == KLINE_INTERVAL__75SECOND:
        return 75
    if interval == KLINE_INTERVAL__90SECOND:
        return 90
    if interval == KLINE_INTERVAL_100SECOND:
        return 100
    if interval == KLINE_INTERVAL_150SECOND:
        return 150
    if interval == KLINE_INTERVAL_225SECOND:
        return 225
    if interval == KLINE_INTERVAL_450SECOND:
        return 450

    elif interval == KLINE_INTERVAL_1MINUTE:
        return 1 * SECONDS_MINUTE
    elif interval == KLINE_INTERVAL_3MINUTE:
        return 3 * SECONDS_MINUTE
    elif interval == KLINE_INTERVAL_5MINUTE:
        return 5 * SECONDS_MINUTE
    elif interval == KLINE_INTERVAL_15MINUTE:
        return 15 * SECONDS_MINUTE
    elif interval == KLINE_INTERVAL_30MINUTE:
        return 30 * SECONDS_MINUTE

    elif interval == KLINE_INTERVAL_1HOUR:
        return 1 * SECONDS_HOUR
    elif interval == KLINE_INTERVAL_2HOUR:
        return 2 * SECONDS_HOUR
    elif interval == KLINE_INTERVAL_4HOUR:
        return 4 * SECONDS_HOUR
    elif interval == KLINE_INTERVAL_6HOUR:
        return 6 * SECONDS_HOUR
    elif interval == KLINE_INTERVAL_8HOUR:
        return 8 * SECONDS_HOUR
    elif interval == KLINE_INTERVAL_12HOUR:
        return 12 * SECONDS_HOUR

    elif interval == KLINE_INTERVAL_1DAY:
        return SECONDS_DAY

    else:
        return None

def get_next_open_time(interval, dt):
    return get_open_time(interval, dt) + get_interval_timedelta(interval)

def get_next_open_timedelta(interval, dt):
    return get_next_open_time(interval, dt) - dt

def get_kline_index(key, kline_column_names):
    for index, value in enumerate(kline_column_names):
        if value == key:
            return index

def trans_from_json_to_list(kls, kline_column_names):
    return [[(kline[column_name] if (column_name in kline) else "0") for column_name in kline_column_names] for kline in kls]

def trans_from_list_to_json(kls_list, kline_column_names):
    kls_json = []
    for kl_list in kls_list:
        kl_json = {}
        for idx, v in enumerate(kl_list):
            kl_json[kline_column_names[idx]] = v
        kls_json.append(kl_json)
    return kls_json
