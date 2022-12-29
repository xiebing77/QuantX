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


def handle_order(trader, strategy, order):
    if trader.get_order_exec_qty(order) > 0:
        trades = [trade for trade in order.trade_records.values()]
    else:
        trades = []
    strategy.sync_bill(order, trades)
    strategy.get_position()


def tq_run():
    parser = argparse.ArgumentParser(description='real tq')
    parser.add_argument('-iid', required=True, help='instance id')
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
    config_path = s["config_path"]
    config = common.get_json_config(config_path)
    module_name = config["module_name"].replace("/", ".")
    class_name = config["class_name"]

    if args.print:
        log.print_switch = True
    if args.log:
        log.log_switch = True
        logfilename = instance_id + ".log"
        print(logfilename)
        log.init('real', logfilename)

    exchange = create_exchange(exchange_name)
    if not exchange:
        log.info("exchange name: {} error!".format(exchange_name))
        exit(1)
    quote_engine = QuoteEngine(exchange)
    trade_engine = ExchangeTradeEngine(instance_id, exchange)
    strategy = common.createInstance(module_name, class_name, instance_id, config, quote_engine, trade_engine)
    strategy.set_amount(1)
    strategy.set_slippage_rate(0)
    if hasattr(strategy, 'load_model'):
        strategy.load_train()
        strategy.load_model()

    symbol = strategy.symbol
    interval_sec = int(strategy.interval_timedelta.total_seconds())
    key_open_time = 'datetime'
    log.info('{}  {}'.format(symbol, interval_sec))

    pd.reset_option('display.float_format')

    api = exchange.connect()
    klines = api.get_kline_serial(symbol, interval_sec, data_length=300)
    log.info(klines)

    #pd.set_option('display.max_rows', None)
    #pd.set_option('display.max_columns', None)

    log.info(strategy.get_position())
    account = api.get_account()
    log.info(account)

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
        api.wait_update()
        '''
        is_update = api.wait_update(deadline=time.time()+5)
        if not is_update:
            print(datetime.now())
            continue
        '''
        now_time = datetime.now()

        if api.is_changing(close_order, check_key):
            log.info(now_time, '  close_order  ', close_order)
            handle_order(trader, strategy, close_order)
            close_order = None
            if open_signal:
                open_order = strategy.new_signal(open_signal)
                continue
            elif sl_signal:
                sl_order = strategy.new_signal(sl_signal)
                continue

        if api.is_changing(open_order, check_key):
            log.info(now_time, '   open_order  ', open_order)
            handle_order(trader, strategy, open_order)
            open_order = None

        if api.is_changing(sl_order, check_key):
            log.info(now_time, '     sl_order  ', sl_order)
            handle_order(trader, strategy, sl_order)
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
            '''
            for bill in strategy.creat_bills(kdf.iloc[-1]):
                if bill:
                    trade_engine.new_limit_bill(**bill)
            '''
            close_signal, open_signal, sl_signal = strategy.creat_signals(kdf.iloc[-1])
            #print('close_signal: ', close_signal)
            #print(' open_signal: ', open_signal)
            #print('   sl_signal: ', sl_signal)
            if close_signal:
                close_order = strategy.new_signal(close_signal)
                if close_order:
                    continue
            if open_signal:
                open_order = strategy.new_signal(open_signal)
            elif sl_signal:
                sl_order = strategy.new_signal(sl_signal)

    api.close()
