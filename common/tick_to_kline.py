import pandas as pd
import numpy as np
from datetime import datetime, timedelta, time
from typing import Optional, Dict, List, Callable

# ==================== 常量（请根据项目实际调整） ====================
tick_key_last = 'last_price'
tick_key_volume = 'volume'
tick_key_oi = 'open_interest'
tick_key_highest = 'highest'
tick_key_lowest = 'lowest'

# ==================== 辅助函数（与您的模块保持一致） ====================
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


# ==================== 单周期处理器 ====================
class KLineProcessor:
    """
    单周期K线处理器，忠实移植最新 to_kline 核心逻辑。
    支持逐tick增量调用，与批量加载结果完全一致。
    """
    def __init__(self, exchange, interval: str, need_book: bool, tick_interval: float, window: int):
        self.exchange = exchange
        self.interval = interval
        self.need_book = need_book
        self.tick_interval_td = timedelta(seconds=tick_interval)
        self.stop_time = [
            time(hour=10, minute=15),
            time(hour=11, minute=30),
            time(hour=15),
            time(hour=23)] #目前使用的品种都是23:00收盘，后续有需要再改进
        self.window = window
        self.interval_td = self._parse_interval(interval)
        self.reset()

    def _parse_interval(self, interval: str) -> timedelta:
        num = ''
        unit = ''
        for char in interval.lower():
            if char.isdigit():
                num += char
            elif char.isalpha():
                unit += char
        num = int(num)
        if unit == 's':
            return timedelta(seconds=num)
        elif unit == 'm':
            return timedelta(minutes=num)
        elif unit == 'h':
            return timedelta(hours=num)
        else:
            raise ValueError(f"不支持的时间间隔: {interval}")

    def _get_open_time(self, tick_time: datetime) -> datetime:
        if self.interval_td.total_seconds() < 60:
            seconds = tick_time.second
            open_second = (seconds // self.interval_td.total_seconds()) * self.interval_td.total_seconds()
            return tick_time.replace(second=int(open_second), microsecond=0)
        else:
            minutes = self.interval_td.total_seconds() / 60
            tick_minutes = tick_time.hour * 60 + tick_time.minute
            open_minutes = (tick_minutes // minutes) * minutes
            open_hour = int(open_minutes // 60)
            open_minute = int(open_minutes % 60)
            return tick_time.replace(hour=open_hour, minute=open_minute, second=0, microsecond=0)

    def _convert_time(self, tick_time_raw) -> datetime:
        if self.exchange is not None:
            converted = self.exchange.get_time_from_data_ts(tick_time_raw)
        else:
            converted = tick_time_raw
        if isinstance(converted, datetime):
            result = converted
        elif isinstance(converted, pd.Timestamp):
            result = converted.to_pydatetime()
        elif isinstance(converted, str):
            result = pd.Timestamp(converted).to_pydatetime()
        elif isinstance(converted, (int, np.int64, float)):
            result = pd.Timestamp(int(converted), unit='ns').to_pydatetime()
        else:
            result = pd.Timestamp(converted).to_pydatetime()
        if result.tzinfo is not None:
            result = result.replace(tzinfo=None)
        return result

    def _is_day_reset_tick(self, tick: pd.Series) -> bool:
        return (not tick[self.exchange.tick_key_bid_size1] and 
                not tick[self.exchange.tick_key_ask_size1])

    def reset(self):
        self.k = None
        self.open_time = None
        self.open_tick = None
        self.day_reset_tick = None
        self.pre_tick = None
        self.k_start_day_volume = 0
        self.kls = []
        self.first_k_is_ok = True
        self.last_processed_tick_time = None

    def _append_kline(self, kline):
        # 首个不完整K线（kls为空且first_k_is_ok为False）直接丢弃
        if not self.kls and not self.first_k_is_ok:
            self.first_k_is_ok = True
            return
        self.kls.append(kline)

    def trim_window(self):
        """实盘模式下限制K线列表长度，控制内存"""
        if self.window and len(self.kls) > self.window:
            self.kls = self.kls[-self.window:]

    def process_tick(self, tick: pd.Series) -> bool:
        """处理单个tick，返回是否有新K线完成"""
        exchange = self.exchange
        need_book = self.need_book
        interval_td = self.interval_td

        # 日重置tick
        if self._is_day_reset_tick(tick):
            if self.k is not None:
                self._append_kline(self.k)
                self.k = None
            self.k_start_day_volume = 0
            self.day_reset_tick = tick
            self.pre_tick = tick
            return False

        tick_time = self._convert_time(tick.get('datetime'))
        day_volume = tick[tick_key_volume]
        last_price = tick[tick_key_last]

        if self.day_reset_tick is None:
            # 第一个有效tick处理（对应原 i==0 and first_k_is_ok）
            if self.first_k_is_ok:
                self.open_tick = tick
                self.pre_tick = tick
                self.first_k_is_ok = False
                return False
        else:
            # 每天开盘第一个tick
            if self.pre_tick.equals(self.day_reset_tick):
                self.open_tick = tick
                self.pre_tick = tick
                return False

        # 8:58/8:59 特殊处理
        if tick_time.minute in [58, 59] and tick_time.hour == 8:
            if self.k is not None:
                self._append_kline(self.k)
                self.k = None
            if self.pre_tick is not None:
                self.k_start_day_volume = self.pre_tick[tick_key_volume]
            self.open_tick = tick
            self.pre_tick = tick
            return False

        has_new = False

        early_complete = False
        # 处理当前K线
        if self.k is not None:
            close_time = self.k["datetime_str"] + interval_td
            if tick_time <= close_time:
                if pd.isna(self.k[exchange.kline_key_open]):
                    self.k[exchange.kline_key_open] = last_price
                update_k(exchange, self.pre_tick, tick, self.k,
                         self.k_start_day_volume, need_book)

            is_end_k = close_time.time() in self.stop_time
            normal_complete = tick_time >= close_time
            early_complete  = (not is_end_k and tick_time < close_time and
                      tick_time + self.tick_interval_td > close_time)

            if normal_complete or early_complete:
                self._append_kline(self.k)
                has_new = True
                old_k = self.k
                self.k = None

                if tick_time > close_time:
                    if tick_time - old_k["datetime_str"] > timedelta(minutes=9):
                        self.open_tick = tick
                    else:
                        self.open_tick = self.pre_tick
                    self.k_start_day_volume = self.pre_tick[tick_key_volume]
                else:
                    self.k_start_day_volume = day_volume
                    self.open_tick = tick
                    self.pre_tick = tick

        # 创建新K线
        if self.k is None:
            pre_open_time = self.open_time
            if early_complete:
                self.open_time = self._get_open_time(tick_time + self.tick_interval_td)
            else:
                self.open_time = self._get_open_time(tick_time)
            close_time = self.open_time + interval_td

            # 补缺失K线
            if len(self.kls) > 0 and pre_open_time is not None:
                pre_k = self.kls[-1]
                pre_k_open_time = pre_k["datetime_str"]
                tk_td = tick_time - pre_k_open_time
                if interval_td < tk_td:
                    if tk_td < timedelta(minutes=9):
                        lack_end_time = self.open_time
                    else:
                        if pre_k_open_time.minute < 15:
                            lack_end_hour = pre_k_open_time.hour
                            lack_end_minute = 15
                        elif pre_k_open_time.minute < 30:
                            lack_end_hour = pre_k_open_time.hour
                            lack_end_minute = 30
                        else:
                            lack_end_hour = pre_k_open_time.hour + 1
                            lack_end_minute = 0
                        lack_end_time = datetime(year=pre_k_open_time.year,
                                                 month=pre_k_open_time.month,
                                                 day=pre_k_open_time.day,
                                                 hour=lack_end_hour,
                                                 minute=lack_end_minute, second=0)

                    open_price = pre_k[exchange.kline_key_close]
                    lack_open_time = pre_open_time + interval_td
                    while lack_open_time < lack_end_time:
                        lack_k = {
                            "datetime_str": lack_open_time,
                            exchange.kline_key_open_time: exchange.get_data_ts_from_time(lack_open_time),
                            exchange.kline_key_open: open_price,
                            exchange.kline_key_high: open_price,
                            exchange.kline_key_low: open_price,
                            exchange.kline_key_close: open_price,
                            exchange.kline_key_volume: 0,
                            exchange.kline_key_oi: pre_k[exchange.kline_key_oi]
                        }
                        if need_book:
                            update_k_book(exchange, self.open_tick, lack_k, prex='open_')
                            update_k_book(exchange, self.open_tick, lack_k, prex='close_')

                        lack_open_time += interval_td
                        if lack_open_time == tick_time:
                            update_k(exchange, self.pre_tick, tick, lack_k,
                                     self.k_start_day_volume, need_book)
                            self.k_start_day_volume = tick[tick_key_volume]
                            self.open_tick = tick
                            self.pre_tick = tick
                        self._append_kline(lack_k)

            # 确定open_price
            if self.open_tick is not None:
                open_price = self.open_tick.last_price
            else:
                open_price = last_price
            if pd.isna(open_price):
                open_price = last_price

            self.k = {
                "datetime_str": self.open_time,
                exchange.kline_key_open_time: exchange.get_data_ts_from_time(self.open_time),
                exchange.kline_key_open: open_price,
                exchange.kline_key_high: open_price,
                exchange.kline_key_low: open_price,
                exchange.kline_key_close: last_price,
                exchange.kline_key_volume: day_volume - self.k_start_day_volume,
                exchange.kline_key_oi: tick[tick_key_oi]
            }
            update_k_hl(exchange, self.pre_tick, tick, self.k)

            if need_book:
                update_k_book(exchange, self.open_tick if self.open_tick is not None else tick,
                              self.k, prex='open_')
                update_k_book(exchange, tick, self.k, prex='close_')

        self.pre_tick = tick
        return has_new

    def force_complete_current_kline(self) -> bool:
        """实盘tick缺失时强制完成当前K线"""
        if self.k is not None and not self.first_k_is_ok:
            return False
        return False

    def finish(self):
        """回测结束时调用，处理最后一个K线"""
        if self.k is not None:
            self._append_kline(self.k)
            self.k = None

    def get_completed_klines(self) -> pd.DataFrame:
        if self.kls:
            return pd.DataFrame(self.kls)
        else:
            return pd.DataFrame()

    def get_current_kline(self) -> Optional[Dict]:
        return self.k

    def get_all_klines(self) -> pd.DataFrame:
        all_kls = list(self.kls) if self.kls else []
        if self.k is not None:
            all_kls.append(self.k)
        return pd.DataFrame(all_kls)


# ==================== 多周期生成器 ====================
class KLineGenerator:
    """
    多周期K线生成器，封装多个KLineProcessor
    实盘：update_realtime
    回测：load_history
    """
    def __init__(self, symbol: str = None, intervals: List[str] = ['15s', '1m', '5m'],
                 need_book: bool = False, exchange=None, tick_interval: float = 0.42,
                 network_delay: float = 0.5, window: int = 300):
        self.symbol = symbol
        self.intervals = intervals
        self.exchange = exchange
        self.need_book = need_book
        self.tick_interval = tick_interval
        self.network_delay = network_delay
        self.interval_tds = {interval: self._parse_interval(interval) for interval in intervals}
        self._validate_intervals()
        self.processors = {}
        for interval in intervals:
            self.processors[interval] = KLineProcessor(
                exchange=exchange,
                interval=interval,
                need_book=need_book,
                tick_interval=tick_interval,
                window=window
            )

    def _parse_interval(self, interval: str) -> timedelta:
        num = ''
        unit = ''
        for char in interval.lower():
            if char.isdigit():
                num += char
            elif char.isalpha():
                unit += char
        num = int(num)
        if unit == 's':
            return timedelta(seconds=num)
        elif unit == 'm':
            return timedelta(minutes=num)
        elif unit == 'h':
            return timedelta(hours=num)
        else:
            raise ValueError(f"不支持的时间间隔: {interval}")

    def _validate_intervals(self):
        if len(self.intervals) < 2:
            return
        sorted_intervals = sorted(self.intervals, key=lambda x: self.interval_tds[x].total_seconds())
        for i in range(1, len(sorted_intervals)):
            smaller = self.interval_tds[sorted_intervals[i-1]].total_seconds()
            larger = self.interval_tds[sorted_intervals[i]].total_seconds()
            if larger % smaller != 0:
                raise ValueError(f"周期之间必须是整数倍关系: {sorted_intervals[i-1]}({smaller}s) 和 {sorted_intervals[i]}({larger}s)")

    def update_realtime(self, tick_df: pd.DataFrame) -> Dict[str, bool]:
        """实盘模式：处理新增tick，返回各周期是否有新K线完成"""
        has_new = {interval: False for interval in self.intervals}
        if tick_df.empty:
            return has_new

        # 获取各处理器中最小的最后处理时间
        last_times = [p.last_processed_tick_time for p in self.processors.values()
                      if p.last_processed_tick_time is not None]
        if last_times:
            min_last = min(last_times)
            last_ts = self.exchange.get_data_ts_from_time(min_last)
            new_ticks = tick_df[tick_df['datetime'] > last_ts]
        else:
            new_ticks = tick_df

        if new_ticks.empty:
            return has_new

        # 处理新增tick
        for _, tick in new_ticks.iterrows():
            for p in self.processors.values():
                if p.process_tick(tick):
                    has_new[p.interval] = True

        # 更新最后处理时间
        convert = self.processors[self.intervals[0]]._convert_time
        last_time = convert(new_ticks.iloc[-1]['datetime'])
        for p in self.processors.values():
            p.last_processed_tick_time = last_time
            p.trim_window()  # 实盘模式限制K线列表长度

        return has_new

    def get_completed_klines(self) -> List[pd.DataFrame]:
        return [self.processors[iv].get_completed_klines() for iv in self.intervals]

    def get_completed_klines_by_interval(self, interval: str) -> pd.DataFrame:
        return self.processors[interval].get_completed_klines()

    def get_current_kline(self, interval: str) -> Optional[Dict]:
        return self.processors[interval].get_current_kline()

    def get_all_klines(self) -> List[pd.DataFrame]:
        return [self.processors[iv].get_all_klines() for iv in self.intervals]

    def load_history(self, tick_df: pd.DataFrame, show_progress: bool = True) -> List[pd.DataFrame]:
        """回测模式：批量处理所有tick，不截断K线"""
        import sys, time
        for p in self.processors.values():
            p.reset()
        total = len(tick_df)
        start = time.time()
        last = -1
        for idx, (_, tick) in enumerate(tick_df.iterrows()):
            for p in self.processors.values():
                p.process_tick(tick)
            if show_progress and total:
                prog = int((idx+1)*100/total)
                if prog != last and prog % 10 == 0:
                    el = time.time()-start
                    spd = (idx+1)/el if el > 0 else 0
                    eta = (total-idx-1)/spd if spd > 0 else 0
                    sys.stdout.write(f"\r进度: {prog}% ({idx+1}/{total}) 耗时:{el:.1f}s 剩余:{eta:.1f}s")
                    sys.stdout.flush()
                    last = prog
        if show_progress and total:
            el = time.time()-start
            sys.stdout.write(f"\r完成: {total} ticks, 耗时:{el:.1f}s\n")
            sys.stdout.flush()
        for p in self.processors.values():
            p.finish()
        return self.get_completed_klines()

    def reset(self):
        for p in self.processors.values():
            p.reset()