#!/usr/bin/env python
#  -*- coding: utf-8 -*-
__author__ = ''

import time
from datetime import datetime
import pandas as pd
import argparse

import common
import common.log as log
from common.instance import INSTANCE_COLLECTION_NAME, INSTANCE_STATUS_START, INSTANCE_STATUS_STOP, instance_statuses, add_instance, delete_instance, update_instance
from exchange.exchange_factory import get_exchange_names, create_exchange
from engine.quote import QuoteEngine
from engine.trade.exchange import ExchangeTradeEngine
from db.mongodb import get_mongodb
import setup


td_db = get_mongodb(setup.trade_db_name)


def sycn_order_to_bill(trader, strategy, order):
    if not order:
        return False
    if not trader.check_status_is_close(order):
        return False

    if trader.get_order_exec_qty(order) > 0:
        trades = [trade for trade in order.trade_records.values()]
    else:
        trades = []

    strategy.sync_bill(order, trades)
    strategy.get_position()
    return True


def check_run_time(now_time):
    #if now_time.weekday() in [5, 6]:
    #    return

    if 15 <= now_time.hour < 20:
        return False
    if 20 == now_time.hour and now_time.minute < 30:
        return False

    if 3 <= now_time.hour < 8:
        return False
    if 8 == now_time.hour and now_time.minute < 30:
        return False

    return True


def tq_loop(strategy, exchange):
    now_time = datetime.now()
    if not check_run_time(now_time):
        #print('{} not run time!'.format(now_time))
        return

    log.info('{}  tq connect start!'.format(now_time))
    api = exchange.connect()

    strategy.open_day()
    symbol = strategy.symbol
    interval_sec = int(strategy.interval_timedelta.total_seconds())
    log.info('{}  {}'.format(symbol, interval_sec))

    klines = api.get_kline_serial(symbol, interval_sec, data_length=300)
    log.info(klines)

    #pd.set_option('display.max_rows', None)
    #pd.set_option('display.max_columns', None)

    log.info(strategy.get_position())
    account = api.get_account()
    log.info(account)

    key_open_time = exchange.kline_key_open_time
    trade_engine = strategy.trade_engine
    trader = trade_engine.trader
    close_key = strategy.key_close
    check_key = trader.ORDER_STATUS_KEY
    close_order = None
    open_order = None
    sl_order = None
    open_signal = None
    cancel_bill_num = 0
    cancel_time = None
    cur_k_open_time = exchange.get_time_from_data_ts(klines[key_open_time].iloc[-1])
    while True:
        '''
        api.wait_update()
        '''
        is_update = api.wait_update(deadline=time.time() + 60)

        now_time = datetime.now()
        if not check_run_time(now_time):
            log.info('{}  tq connect stop!'.format(now_time))
            break

        if not is_update:
            # print('{}  not update'.format(now_time))
            continue

        if api.is_changing(close_order, check_key):
            log.info('{}  close_order  {}'.format(now_time, close_order))
            sycn_order_to_bill(trader, strategy, close_order)
            close_order = None
            if open_signal:
                open_order = strategy.new_signal(open_signal)
                sycn_order_to_bill(trader, strategy, open_order)
                continue
            elif sl_signal:
                sl_order = strategy.new_signal(sl_signal)
                sycn_order_to_bill(trader, strategy, sl_order)
                continue

        if api.is_changing(open_order, check_key):
            log.info('{}   open_order  {}'.format(now_time, open_order))
            sycn_order_to_bill(trader, strategy, open_order)
            open_order = None

        if api.is_changing(sl_order, check_key):
            log.info('{}     sl_order  {}'.format(now_time, sl_order))
            sycn_order_to_bill(trader, strategy, sl_order)
            sl_order = None

        cur_sec = (now_time - cur_k_open_time).total_seconds()
        if cur_sec > interval_sec * 0.8 and (not cancel_time or (now_time - cancel_time).total_seconds() > 10):
            cancel_time = now_time
            #if cancel_bill_num > 0:
            #    strategy.get_position()
            cancel_bill_num = strategy.cancel_open_bills()
            if cancel_bill_num > 0:
                log.info('{}  cancel_bill_num: {}'.format(now_time, cancel_bill_num))
                continue

        if api.is_changing(klines.iloc[-1], key_open_time):
            klines['open_time'] = klines[key_open_time].apply(exchange.get_time_from_data_ts)
            pre_k = klines.iloc[-2]
            cur_k = klines.iloc[-1]
            cur_k_open_time = cur_k.open_time
            #print(klines)
            log.info("\n{} {} {}  new kline id: {}, open time: {};  close  pre: {}  cur: {}".format(
                '-'*30, now_time, '-'*30, cur_k.id, cur_k_open_time, pre_k.close, cur_k.close))
            if (cur_k_open_time - pre_k.open_time).total_seconds() > interval_sec:
                continue

            log.info('kline ==> {}'.format(strategy.get_position()))
            log.info(account)

            kdf = klines[:-1].copy()
            kdf = strategy.handle_feature(kdf)
            kdf = strategy.handle_df(kdf)
            log.info(kdf)

            close_signal, open_signal, sl_signal = strategy.creat_signals(kdf.iloc[-1])
            log.info('close_signal: {}'.format(close_signal))
            log.info(' open_signal: {}'.format(open_signal))
            log.info('   sl_signal: {}'.format(sl_signal))
            if close_signal:
                close_order = strategy.new_signal(close_signal)
                log.info('close_order: {}'.format(close_order))
                if close_order and not sycn_order_to_bill(trader, strategy, close_order):
                    continue
            if open_signal:
                open_order = strategy.new_signal(open_signal)
                log.info('open_order: {}'.format(open_order))
                sycn_order_to_bill(trader, strategy, open_order)
            elif sl_signal:
                sl_order = strategy.new_signal(sl_signal)
                sycn_order_to_bill(trader, strategy, sl_order)
            log.info('kline handle finish!')
    api.close()


def tq_run():
    parser = argparse.ArgumentParser(description='real tq')
    parser.add_argument('-iid', required=True, help='instance id')
    parser.add_argument('-debug', action="store_true", help='run debug')
    parser.add_argument('--log', action="store_true", help='log info')
    parser.add_argument('--print', action="store_true", help='print info')
    args = parser.parse_args()

    instance_id = args.iid
    ss = td_db.find(INSTANCE_COLLECTION_NAME, {"instance_id": instance_id})
    if not ss:
        print('%s not exist' % (instance_id))
        exit(1)
    s = ss[0]
    exchange_name = s['exchange']
    limit_amount = s['amount']
    config_path = s["config_path"]
    config = common.get_json_config(config_path)
    module_name = config["module_name"].replace("/", ".")
    class_name = config["class_name"]

    if args.print:
        log.print_switch = True
    if args.log:
        log.log_switch = True
        logfilename = instance_id + ".log"
        log.init('real', logfilename)

    slippage_rate = s['slippage_rate']
    threshold = s['threshold']
    if threshold not in config['y']['threshold']:
        log.warning('threshold not in config')
        exit(1)

    exchange = create_exchange(exchange_name)
    if not exchange:
        log.info("exchange name: {} error!".format(exchange_name))
        exit(1)
    quote_engine = QuoteEngine(exchange)
    trade_engine = ExchangeTradeEngine(instance_id, exchange)
    strategy = common.createInstance(module_name, class_name, instance_id, config, quote_engine, trade_engine)
    strategy.set_amount(limit_amount)
    strategy.set_slippage_rate(slippage_rate)
    strategy.set_y_threshold(threshold[0], threshold[1])
    if hasattr(strategy, 'load_model'):
        strategy.load_train()
        strategy.load_model()

    pd.reset_option('display.float_format')

    while True:

        if args.debug:
            tq_loop(strategy, exchange)
        else:
            try:
                tq_loop(strategy, exchange)
            except Exception as ept:
                log.critical(ept)
        time.sleep(60)

