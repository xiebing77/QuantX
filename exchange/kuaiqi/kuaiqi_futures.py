#!/usr/bin/python
"""bybit spot"""
import os
import math
from datetime import datetime
import uuid
from . import Kuaiqi
import common
import common.log as log


yx_name     = os.environ.get('YIXIN_NAME')
yx_password = os.environ.get('YIXIN_PWD')


class KuaiqiFutures(Kuaiqi):
    name = Kuaiqi.name + '_futures'

    symbol_info_map = {}

    depth_limits = [20, 100]

    def __init__(self, debug=False):
        return

    def connect(self):
        from tqsdk import TqAccount, TqKq
        account = TqKq() # TqAccount()
        from tqsdk import TqApi, TqAuth
        api = TqApi(account, auth=TqAuth(yx_name, yx_password))
        self.__api = api
        return api

    def _get_assetPrecision(self, ex_symbol):
        if ex_symbol not in self.symbol_info_map:
            sy_infos = self._exchange_info()['data']
            for sy_info in sy_infos:
                if ex_symbol == sy_info['symbol']:
                    self.symbol_info_map[sy_info['symbol']] = sy_info
            #print(sy_info)
        sy_info = self.symbol_info_map[ex_symbol]
        return int(sy_info['quantityScale']), int(sy_info['priceScale'])

    # MARKETS
    def ping(self):
        return

    def time(self):
        return self.get_time_from_data_ts(self.__api.time()['data'])

    def _exchange_info(self, ex_symbol: str = None, ex_symbols: list = None):
        return self.__api.exchange_info()

    def _depth(self, exchange_symbol, **kwargs):
        ret = self.__api.depth(symbol=exchange_symbol, **kwargs)
        #print(ret)
        return ret['data']

    def _trades(self, exchange_symbol, limit=500):
        trades = self.__api.trades(symbol=exchange_symbol, limit=limit)['data']
        return trades

    def _historical_trades(self, exchange_symbol):
        trades = self.__api.historical_trades(symbol=exchange_symbol)
        return trades

    def _agg_trades(self, exchange_symbol):
        trades = self.__api.agg_trades(symbol=exchange_symbol)
        return trades

    def _ticker_price(self, exchange_symbol):
        ticker_info = self.__api.ticker(exchange_symbol)['data']
        return float(ticker_info['close'])

    def _klines(self, exchange_symbol, interval, size, since):
        return []

    def account(self):
        account = self.__api.get_account()
        print(account)
        if not account:
            return None
        nb = []
        #balances = account['balances']
        for item in account:
            if float(item['available'])==0 and float(item['frozen'])==0 and float(item['lock'])==0:
                continue
            nb.append(item)
        #account['balances'] = nb
        return nb


    def get_balances(self):
        account = self.account()
        #print(account)
        return account


    def get_balances_by_assets(self, *coins):
        """获取余额"""
        coin_balances = []
        balances = self.get_all_balances()
        for coin in coins:
            for item in balances:
                if item[self.BALANCE_ASSET_KEY] in [coin.upper, coin.lower]:
                    coin_balances.append(item)
                    break
        if len(coin_balances) <= 0:
            return
        elif len(coin_balances) == 1:
            return coin_balances[0]
        else:
            return tuple(coin_balances)

    def _my_trades(self, exchange_symbol, **kwargs):
        trades = self.__api.get_trade()
        log.info('_my_trades', trades)
        return [trade for trade in trades.values()]


    def _new_order(self, ex_side, ex_type, ex_symbol, price, qty, oc, client_order_id=None):
        #if not client_order_id:
        #    client_order_id = str(uuid.uuid1())

        if ex_type == common.ORDER_TYPE_LIMIT:
            limit_price = price
        elif ex_type == common.ORDER_TYPE_MARKET:
            limit_price = None
        else:
            return None

        # 上期所和上期能源分平今/平昨
        if hasattr(self, 'OC_CLOSETODAY') and oc == common.OC_CLOSE:
            ex_pst = self.__api.get_position(ex_symbol)
            self.__api.wait_update()
            log.info(ex_pst)
            if ex_side == self.SIDE_SELL:
                pos_his = ex_pst.pos_long_his
            else:
                pos_his = ex_pst.pos_short_his

            if pos_his >= qty:
                oc = self.OC_CLOSE
            else:
                oc = self.OC_CLOSETODAY

        params = {
            'symbol': ex_symbol,
            'offset': oc,
            'direction': ex_side,
            'limit_price': limit_price,
            'volume': qty
        }
        log.info('-----> insert order:  ', params)
        order = self.__api.insert_order(**params)
        '''
        log.info('before: ', order)
        while not order.order_id:
            self.__api.wait_update()
        log.info(' after: ', order)
        '''
        return order


    def _get_open_orders(self, exchange_symbol):
        return []

    def _get_order(self, exchange_symbol, order_id):
        order = self.__api.get_order(order_id)
        log.info('_get_order before id: {}, order: {}'.format(order_id, order))
        while not order.order_id:
            self.__api.wait_update()
        log.info('_get_order  after: ', order)
        log.info('trade_records', order.trade_records)
        return order

    def _get_orders(self, exchange_symbol, limit=None):
        return []
        orders = self.__api.get_order()
        self.__api.wait_update()
        log.info('_get_orders: ', orders)
        return orders

    def _cancel_order(self, exchange_symbol, order_id):
        log.info('-----> cancel order id:  ', order_id)
        self.__api.cancel_order(order_id)

    def _cancel_open_orders(self, exchange_symbol):
        return
