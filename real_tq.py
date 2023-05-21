#!/usr/bin/env python
#  -*- coding: utf-8 -*-
__author__ = ''

import time
from datetime import datetime
import pandas as pd
import argparse

import common
import common.log as log
from common.cell import get_cell, get_cell_info, get_cell_broker
from exchange.exchange_factory import get_exchange_names, create_exchange
from engine.quote import QuoteEngine
from engine.trade.exchange import ExchangeTradeEngine
from db.mongodb import get_mongodb
import setup



def sycn_order_to_bill(cell_id, trader, trade_engine, order):
    if not order:
        return None
    if not trader.check_status_is_close(order):
        return order

    if trader.get_order_exec_qty(order) > 0:
        trades = [trade for trade in order.trade_records.values()]
        if len(trades) == 0:
            log.info('not trades! close order: {}'.format(order))
            return order
    else:
        trades = []

    trade_engine.sync_bill(trader, order, trades)
    trade_engine.get_position(cell_id)
    return None


def check_alive_orders(cell_id, trader, trade_engine, orders):
    if not orders:
        return []

    alive_orders = []
    for order in orders:
        if sycn_order_to_bill(cell_id, trader, trade_engine, order):
            alive_orders.append(order)
    return alive_orders


def create_orders(strategy, signal, cell_id, trader, rmk):
    orders = strategy.new_signal(signal)
    log.info('-----> {} orders: {}'.format(rmk, orders))
    orders = check_alive_orders(cell_id, trader, strategy.trade_engine, orders)
    return orders


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


def tq_loop(strategy, exchange, cell_id):
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

    trade_engine = strategy.trade_engine
    log.info('cell_id: {},  pst: {}'.format(cell_id, trade_engine.get_position(cell_id)))

    account = api.get_account()
    log.info(account)

    key_open_time = exchange.kline_key_open_time
    trader = exchange
    close_orders = []
    open_orders  = []
    sl_orders    = []
    open_signal = None
    sl_signal   = None
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

        close_orders = check_alive_orders(cell_id, trader, trade_engine, close_orders)
        if not close_orders:
            if open_signal:
                open_orders = create_orders(strategy, open_signal, cell_id, trader, 'delay open')
                open_signal = None
                continue
            elif sl_signal:
                sl_orders = create_orders(strategy, sl_signal, cell_id, trader, 'delay stoploss')
                sl_signal = None
                continue

        open_orders = check_alive_orders(cell_id, trader, trade_engine, open_orders)
        sl_orders   = check_alive_orders(cell_id, trader, trade_engine, sl_orders)

        cur_sec = (now_time - cur_k_open_time).total_seconds()
        if cur_sec > interval_sec * 0.8 and (not cancel_time or (now_time - cancel_time).total_seconds() > 10):
            cancel_time = now_time
            cancel_bill_num = strategy.cancel_open_bills(cell_id)
            if cancel_bill_num > 0:
                log.info('{} cell_id: {},  cancel_bill_num: {}'.format(
                    now_time, cell_id, cancel_bill_num))

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

            log.info('kline ==> {}'.format(trade_engine.get_position(cell_id)))
            log.info(account)

            kdf = klines[:-1].copy()
            kdf = strategy.handle_feature(kdf)
            kdf = strategy.handle_df(kdf)
            log.info(kdf)

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
                close_orders = create_orders(strategy, close_signal, cell_id, trader, 'new close')

            if not close_orders:
                if open_signal:
                    open_orders = create_orders(strategy, open_signal, cell_id, trader, 'new open')
                    open_signal = None
                elif sl_signal:
                    sl_orders = create_orders(strategy, sl_signal, cell_id, trader, 'new stoploss')
                    sl_signal = None
            log.info('-----> kline handle finish!')
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

    threshold = cell['threshold']
    '''
    if threshold not in config['y']['threshold']:
        log.warning('threshold not in config')
        exit(1)
    '''

    broker_path, broker = get_cell_broker(cell)
    exchange = create_exchange(exchange_name, broker)
    if not exchange:
        log.info("exchange name: {} error!".format(exchange_name))
        exit(1)
    quote_engine = QuoteEngine(exchange)
    trade_engine = ExchangeTradeEngine()
    trade_engine.set_cell(cell_id, exchange, *get_cell_info(cell))
    strategy = common.createInstance(module_name, class_name, config, quote_engine, trade_engine)
    strategy.set_y_threshold(cell_id, threshold[0], threshold[1])

    if hasattr(strategy, 'trainning'):
        strategy.trainning()

    pd.reset_option('display.float_format')

    while True:

        if args.debug:
            tq_loop(strategy, exchange, cell_id)
        else:
            try:
                tq_loop(strategy, exchange, cell_id)
            except Exception as ept:
                log.critical(ept)
        time.sleep(60)

