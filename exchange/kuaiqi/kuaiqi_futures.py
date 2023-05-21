#!/usr/bin/python
"""bybit spot"""
import os
import math
import time
from datetime import datetime
import uuid
from . import Kuaiqi
import common
import common.log as log


class KuaiqiFutures(Kuaiqi):
    name = Kuaiqi.name + '_futures'

    symbol_info_map = {}

    depth_limits = [20, 100]

    need_oc = True

    def __init__(self, broker, debug=False):
        if broker:
            self.yx_name     = broker['YIXIN_NAME']
            self.yx_password = broker['YIXIN_PWD']

            self.broker_name     = broker['BROKER_NAME']
            self.broker_account  = broker['BROKER_ACCOUNT']
            self.broker_password = broker['BROKER_PWD']
        else:
            self.yx_name     = os.environ.get('YIXIN_NAME')
            self.yx_password = os.environ.get('YIXIN_PWD')

            self.broker_name     = os.environ.get('BROKER_NAME')
            self.broker_account  = os.environ.get('BROKER_ACCOUNT')
            self.broker_password = os.environ.get('BROKER_PWD')
        self._api = None
        return

    #def __exit__(self, *exc_details):
    def close(self):
        log.info('KuaiqiFutures __exit__')
        if self._api:
            self._api.close()
            self._api = None

    def connect(self):
        if not self._api:
            from tqsdk import TqAccount
            from tqsdk import TqApi, TqAuth
            account = TqAccount(self.broker_name, self.broker_account, self.broker_password)
            self._api = TqApi(account, auth=TqAuth(self.yx_name, self.yx_password))
        return self._api

    def _get_api(self):
        if not self._api:
            self.connect()
        return self._api

    def _get_assetPrecision(self, ex_symbol):
        if ex_symbol not in self.symbol_info_map:
            q = self._get_api().get_quote(ex_symbol)
            self.symbol_info_map[ex_symbol] = [0, q['price_decs']]
        sy_info = self.symbol_info_map[ex_symbol]
        return sy_info[0], sy_info[1]

    # MARKETS
    def ping(self):
        return

    def time(self):
        return self.get_time_from_data_ts(self._get_api().time()['data'])

    def _exchange_info(self, ex_symbol: str = None, ex_symbols: list = None):
        return None

    def _depth(self, exchange_symbol, **kwargs):
        ret = self._get_api().depth(symbol=exchange_symbol, **kwargs)
        #print(ret)
        return ret['data']

    def _trades(self, exchange_symbol, limit=500):
        trades = self._get_api().trades(symbol=exchange_symbol, limit=limit)['data']
        return trades

    def _historical_trades(self, exchange_symbol):
        trades = self._get_api().historical_trades(symbol=exchange_symbol)
        return trades

    def _agg_trades(self, exchange_symbol):
        trades = self._get_api().agg_trades(symbol=exchange_symbol)
        return trades

    def _ticker_price(self, exchange_symbol):
        ticker_info = self._get_api().get_quote(exchange_symbol)
        return float(ticker_info.last_price)

    def _klines(self, exchange_symbol, interval, size, since):
        klines = self._get_api().get_kline_serial(exchange_symbol, interval, data_length=size)
        return klines

    def account(self):
        return self._get_api().get_account()

    def get_balances(self):
        account = self.account()
        #print(account)
        return account

    def get_balances_by_assets(self, *coins):
        return

    def _my_trades(self, exchange_symbol, **kwargs):
        trades = self._get_api().get_trade()
        log.info('_my_trades: {}'.format(trades))
        return [trade for trade in trades.values()]


    def _get_ex_pst(self, ex_symbol):
        ex_pst = self._get_api().get_position(ex_symbol)
        #self._get_api().wait_update()
        log.info('ex_pst: {}'.format(ex_pst))
        return ex_pst.pos_long_his, ex_pst.pos_long_today, ex_pst.pos_short_his, ex_pst.pos_short_today

    def close_pos_his_not_enough(self, order):
        if order['is_error'] and order['last_msg'] == 'CTP:平昨仓位不足':
            return True
        return False

    def close_pos_today_not_enough(self, order):
        if order['is_error'] and order['last_msg'] == 'CTP:平今仓位不足':
            return True
        return False

    def _new_order(self, ex_side, ex_type, ex_symbol, price, qty, ex_oc, client_order_id=None):
        #if not client_order_id:
        #    client_order_id = str(uuid.uuid1())

        if ex_type == common.ORDER_TYPE_LIMIT:
            limit_price = price
        elif ex_type == common.ORDER_TYPE_MARKET:
            limit_price = None
        else:
            return None

        params = {
            'symbol': ex_symbol,
            'offset': ex_oc,
            'direction': ex_side,
            'limit_price': limit_price,
            'volume': qty
        }
        order = self._send_order(params)
        return order


    def _send_order(self, params):
        log.info('-----> insert order:  {}'.format(params))
        order = self._get_api().insert_order(**params)
        from datetime import datetime
        insert_dt = datetime.now()
        log.info('{} insert wait_update before: {}'.format(insert_dt, order))
        while not order.exchange_order_id:
            if (datetime.now()-insert_dt).total_seconds() > 5:
                break
            self._get_api().wait_update(deadline=time.time() + 1)
        log.info('{} insert wait_update  after: {}'.format(datetime.now(), order))
        return order


    def _get_open_orders(self, exchange_symbol):
        return []

    def _get_order(self, exchange_symbol, order_id):
        order = self._get_api().get_order(order_id)
        log.info('_get_order id: {}'.format(order_id))
        log.info('_get_order before: {}'.format(order))
        get_dt = datetime.now()
        while not order.order_id:
            now = datetime.now()
            if (now-get_dt).total_seconds() > 10:
                return None
            self._get_api().wait_update(deadline=time.time() + 1)
        log.info('_get_order  after: {}'.format(order))
        log.info('trade_records: {}'.format(order.trade_records))
        return order

    def _get_orders(self, exchange_symbol, limit=None):
        return []
        orders = self._get_api().get_order()
        self._get_api().wait_update()
        log.info('_get_orders: {}'.format(orders))
        return orders

    def _cancel_order(self, exchange_symbol, order_id):
        log.info('-----> cancel order id:  {}'.format(order_id))
        self._get_api().cancel_order(order_id)

    def _cancel_open_orders(self, exchange_symbol):
        return


class KuaiqiFuturesSim(KuaiqiFutures):
    name = KuaiqiFutures.name + '_sim'
    data_src = KuaiqiFutures.name
    def connect(self):
        if not self._api:
            from tqsdk import TqKq
            from tqsdk import TqApi, TqAuth
            self._api = TqApi(TqKq(), auth=TqAuth(self.yx_name, self.yx_password))
        return self._api

