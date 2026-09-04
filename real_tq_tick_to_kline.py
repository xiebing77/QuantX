#!/usr/bin/env python
#  -*- coding: utf-8 -*-
__author__ = ''

import time
from datetime import datetime, timedelta
import pandas as pd
import argparse

import common
import common.kline as kl
import common.log as log
from common.cell import get_cell, get_cell_info, get_cell_broker
from exchange.exchange_factory import get_exchange_names, create_exchange
from engine.quote.exchange import ExchangeQuoteEngine
from engine.trade.exchange import ExchangeTradeEngine
from db.mongodb import get_mongodb
from .real_tq import check_alive_orders, create_orders, check_run_time, get_book_info


def tq_loop(strategy, cell_id, realtime_gen):
    exchange = strategy.trade_engine.get_cell_trader(cell_id)

    now_time = datetime.now()
    if not check_run_time(now_time):
        #print('{} not run time!'.format(now_time))
        return

    log.info('{}  {}  tq connect start!'.format(now_time, cell_id))
    api = exchange.connect()

    strategy.open_day(now_time)
    symbol = strategy.symbol

    key_open_time = exchange.kline_key_open_time
    key_close = exchange.kline_key_close
    tick_df = api.get_tick_serial(symbol, data_length=10000)

    tick_start_time = exchange.get_time_from_data_ts(tick_df[key_open_time].iloc[0])
    tick_end_time = exchange.get_time_from_data_ts(tick_df[key_open_time].iloc[-1])
    log.info(f'tick len: {len(tick_df)};  time range:  {tick_start_time} ~ {tick_end_time}; {tick_end_time-tick_start_time}')

    tick_df['last_time'] = tick_df[key_open_time].apply(exchange.get_time_from_data_ts)

    '''
    del tick_df['ask_price2']
    del tick_df['ask_price3']
    del tick_df['ask_price4']
    del tick_df['ask_price5']
    del tick_df['ask_volume2']
    del tick_df['ask_volume3']
    del tick_df['ask_volume4']
    del tick_df['ask_volume5']

    del tick_df['bid_price2']
    del tick_df['bid_price3']
    del tick_df['bid_price4']
    del tick_df['bid_price5']
    del tick_df['bid_volume2']
    del tick_df['bid_volume3']
    del tick_df['bid_volume4']
    del tick_df['bid_volume5']
    '''
    log.info(tick_df.head(10))
    log.info(tick_df.tail(10))

    dfs = realtime_gen.get_all_klines()

    interval_secs = []
    interval_timedeltas = []
    for interval, df in zip(strategy.intervals, dfs):
        interval_timedelta = kl.get_interval_timedelta(interval)
        interval_sec = int(interval_timedelta.total_seconds())
        log.info('{}  {}'.format(symbol, interval_sec))

        log.info(df)
        log.info(f"{interval} K线数量: {len(df)}")

        interval_secs.append(interval_sec)
        interval_timedeltas.append(interval_timedelta)

    trade_engine = strategy.trade_engine
    log.info('cell_id: {},  pst: {}'.format(cell_id, trade_engine.get_position(cell_id)))

    account = api.get_account()
    log.info(account)

    quote = api.get_quote(symbol)

    trader = exchange
    close_orders = []
    open_orders  = []
    sl_orders    = []
    open_signal = None
    sl_signal   = None
    cancel_time = None
    interval = strategy.intervals[0]
    cur_k = realtime_gen.get_current_kline(interval)
    cur_k_open_time = exchange.get_time_from_data_ts(cur_k[key_open_time]) if cur_k else None
    print(f'cur_k_open_time: {cur_k_open_time}')
    handle_open_time = None
    while True:
        '''
        api.wait_update()
        '''
        is_update = api.wait_update(deadline=time.time() + 60)

        now_time = datetime.now()
        if not check_run_time(now_time):
            log.info(f'{quote.datetime} {now_time}  tq connect stop!')
            break

        if not is_update:
            # print('{}  not update'.format(now_time))
            continue

        info = f'local time: {now_time}'
        if api.is_changing(tick_df.iloc[-1], exchange.tick_key_time):
            cur_tick = tick_df.iloc[-1]
            cur_tick_time = exchange.get_time_from_data_ts(cur_tick[key_open_time])
            info += '    cur_tick_time: {};    id: {},         {:6.1f}({:4d})    {:6.1f}    {:6.1f}({:4d}),'.format(
                cur_tick_time, int(cur_tick["id"]),
                float(cur_tick['bid_price1']), int(cur_tick['bid_volume1']),
                float(cur_tick['last_price']),
                float(cur_tick['ask_price1']), int(cur_tick['ask_volume1'])
            )
        log.info(info)

        if api.is_changing(quote, "last_price"):
            log.info(get_book_info(quote))

        close_orders = check_alive_orders(cell_id, trader, trade_engine, close_orders)
        if not close_orders:
            if open_signal:
                log.info(get_book_info(quote))
                open_orders = create_orders(strategy, open_signal, cell_id, trader, 'delay open')
                open_signal = None
                continue
            elif sl_signal:
                log.info(get_book_info(quote))
                sl_orders = create_orders(strategy, sl_signal, cell_id, trader, 'delay stoploss')
                sl_signal = None
                continue

        open_orders = check_alive_orders(cell_id, trader, trade_engine, open_orders)
        sl_orders   = check_alive_orders(cell_id, trader, trade_engine, sl_orders)

        if cur_k_open_time:
            cur_sec = (now_time - cur_k_open_time).total_seconds()
            if cur_sec > interval_secs[0] * 0.8 and (not cancel_time or (now_time - cancel_time).total_seconds() > 10):
                cancel_time = now_time
                cancel_bill_num = strategy.cancel_open_bills(cell_id)
                if cancel_bill_num > 0:
                    log.info('{} cell_id: {},  cancel_bill_num: {}'.format(
                        now_time, cell_id, cancel_bill_num))

            diff_sec = interval_secs[0] - cur_sec
            if diff_sec <= 1 and ( not handle_open_time or handle_open_time < cur_k_open_time):
                log.info(get_book_info(quote))
                log.info(f'pre 1 sec for calc k')
                handle_open_time = cur_k_open_time

        has_new_klines = realtime_gen.update_realtime(tick_df)
        if any(has_new_klines.values()):
            dfs = realtime_gen.get_completed_klines()
            sub_df = dfs[0]
            sub_df['open_time_dt'] = sub_df[key_open_time].apply(exchange.get_time_from_data_ts)
            pre_k = sub_df.iloc[-1]

            cur_k = realtime_gen.get_current_kline(interval)
            cur_k_open_time = exchange.get_time_from_data_ts(cur_k[key_open_time])

            log.info("\n{} {} {}  new kline id: {}, open time: {};  close  pre: {}  cur: {}".format(
                '-'*30, now_time, '-'*30, cur_k['id'] if 'id' in cur_k else '', cur_k_open_time, pre_k.close, cur_k[key_close]))
            if (cur_k_open_time - pre_k.open_time_dt).total_seconds() > interval_secs[0]:
                continue
            log.info(sub_df.head(3))
            log.info(sub_df.tail(5))

            kdf = strategy.handle_feature(dfs)
            log.info(f'after handdle feature:  {datetime.now()}')
            kdf = strategy.predict(kdf)
            log.info(f'after predict        :  {datetime.now()}')
            #log.info(kdf)

            log.info(' {}   {}  cell id: {}  {}'.format(datetime.now(), '*'*20, cell_id, '*'*20))
            log.info(account)

            close_signal, open_signal, sl_signal = strategy.creat_cell_signals(kdf.iloc[-1], cell_id)
            log.info('-----> close_signal: {}'.format(close_signal))
            log.info('----->  open_signal: {}'.format(open_signal))
            log.info('----->    sl_signal: {}'.format(sl_signal))

            if close_orders or open_orders or sl_orders:
                log.info('-----> alive close_orders: {}'.format(close_orders))
                log.info('-----> alive  open_orders: {}'.format(open_orders))
                log.info('-----> alive    sl_orders: {}'.format(sl_orders))
                continue

            if close_signal:
                log.info(get_book_info(quote))
                close_orders = create_orders(strategy, close_signal, cell_id, trader, 'new close')

            if not close_orders:
                if open_signal:
                    log.info(get_book_info(quote))
                    open_orders = create_orders(strategy, open_signal, cell_id, trader, 'new open')
                    open_signal = None
                elif sl_signal:
                    log.info(get_book_info(quote))
                    sl_orders = create_orders(strategy, sl_signal, cell_id, trader, 'new stoploss')
                    sl_signal = None
            finish_time = datetime.now()
            log.info(f'-----> k handle ok!  cost: {finish_time-now_time}  local time: {finish_time}')
    exchange.close()


def tq_run():
    parser = argparse.ArgumentParser(description='real tq')
    parser.add_argument('-iid', required=True, help='cell id')
    parser.add_argument('-debug', action="store_true", help='run debug')
    parser.add_argument('--log', action="store_true", help='log info')
    parser.add_argument('--print', action="store_true", help='print info')
    args = parser.parse_args()

    cell_id = args.iid
    cell = get_cell(cell_id)
    exchange_name = cell['exchange']
    config_path   = cell["config_path"]

    config = common.get_json_config(config_path)
    module_name = config["module_name"].replace("/", ".")
    class_name = config["class_name"]

    if args.print:
        log.print_switch = True
    if args.log:
        log.log_switch = True
        logfilename = cell_id + ".log"
        log.init('real', logfilename)

    log.info(cell)
    cell_cluster = cell['cluster']
    cell_cluster_name  = cell_cluster[0]
    cell_cluster_model = cell_cluster[1]
    log.info(f'cell_cluster: {cell_cluster}')

    model_palams = config['cluster'][cell_cluster_name][cell_cluster_model]
    log.info(model_palams)
    threshold = cell['threshold']
    if threshold not in model_palams['thresholds']:
        log.warning('threshold not in config')
        exit(1)

    broker_path, broker = get_cell_broker(cell)
    exchange = create_exchange(exchange_name, broker)
    if not exchange:
        log.info("exchange name: {} error!".format(exchange_name))
        exit(1)
    quote_engine = ExchangeQuoteEngine(exchange)
    trade_engine = ExchangeTradeEngine(config)
    trade_engine.commission_rate = cell['commission']['rate']
    trade_engine.set_cell(cell_id, exchange, *get_cell_info(cell))
    strategy = common.createInstance(module_name, class_name, config, quote_engine, trade_engine)
    strategy.set_y_threshold(cell_id, threshold)
    log.info(f'slippage: {trade_engine.slippage}, min_price_change: {trade_engine.min_price_change}')

    strategy.set_cluster(cell_cluster_name, cell_cluster_model)

    if hasattr(strategy, 'trainning'):
        strategy.trainning()

    pd.set_option('display.max_rows', None)
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', 1000)
    pd.set_option('display.float_format', None)
    #pd.set_option('display.float_format', lambda x: '%.6f' % x)
    #pd.options.display.float_format = None
    #pd.reset_option('display.float_format')

    now_time = datetime.now()
    strategy.open_day(now_time)
    symbol = strategy.symbol
    download_tasks = {}
    csv_files = []

    e_time = now_time
    days = 0
    while days < 30:
        days += 1

        s_time = e_time - timedelta(days=days)
        s_time = s_time.replace(hour=16, minute=0, second=0, microsecond=0)
        if s_time.weekday() in [4, 5, 6]:
            continue
        log.info(f'**********  time range:    ({s_time}  ~~~  {e_time}) *****************')

        csv_file_name = f'{symbol}_{s_time}_{e_time}_tick.csv'
        log.info(csv_file_name)

        api = exchange.connect()
        from tqsdk.tools import DataDownloader
        kd = DataDownloader(api, symbol_list=symbol, dur_sec=0,
                            start_dt=s_time, end_dt=e_time,
                            csv_file_name=csv_file_name)
        download_tasks[symbol] = kd

        # 使用with closing机制确保下载完成后释放对应的资源
        from contextlib import closing
        import sys
        with closing(api):
            while not all([v.is_finished() for v in download_tasks.values()]):
                api.wait_update()
                sys.stdout.flush()
                info = { k:("%.2f%%" % v.get_progress()) for k,v in download_tasks.items() }
                sys.stdout.write("\rprogress: %s" % info)
            sys.stdout.write('\n')
        exchange.close()

        tick_df = pd.read_csv(csv_file_name)
        log.info(f'tick_df len: {len(tick_df)}')
        if len(tick_df) == 0:
            continue

        tick_df.rename(columns={'datetime': 'datetime_str', 'datetime_nano': 'datetime'}, inplace=True)
        index = csv_file_name.find('_')
        prefix = csv_file_name[:index] + '.'
        tick_df.columns = tick_df.columns.str.replace(prefix, '')
        log.info(tick_df.head(5))
        log.info(tick_df.tail(15))

        from common.tick_to_kline import KLineGenerator
        realtime_gen = KLineGenerator(symbol, intervals=strategy.intervals, need_book=True,
                                    exchange=exchange, window=strategy.window)
        has_new_klines = realtime_gen.update_realtime(tick_df)
        if not any(has_new_klines.values()):
            exit(1)
        dfs = realtime_gen.get_completed_klines()
        kline_df = dfs[0]
        interval = strategy.intervals[0]
        cur_k = realtime_gen.get_current_kline(interval)
        key_open_time = exchange.kline_key_open_time
        cur_k_open_time = exchange.get_time_from_data_ts(cur_k[key_open_time]) if cur_k else None
        log.info(kline_df.head(5))
        log.info(kline_df.tail(15))
        log.info(f'completed_kline_df len: {len(kline_df)};   current_kline open time: {cur_k_open_time}')
        if len(kline_df) >= strategy.window:
            break

    while True:

        if args.debug:
            tq_loop(strategy, cell_id, realtime_gen)
        else:
            try:
                tq_loop(strategy, cell_id, realtime_gen)
            except Exception as ept:
                log.critical(ept)
        time.sleep(60)

