#!/usr/bin/python
"""bitrue spot"""
import os
from datetime import datetime
from .bitrue import Bitrue, api_key, secret_key
from .spot import Spot
from common import create_balance
from common import TIME_IN_FORCE_GTC


class BitrueSpot(Bitrue):
    name = Bitrue.name + '_spot'
    start_time = datetime(2017, 8, 17, 8)

    symbol_info_map = {}

    depth_limits = [5, 10, 20, 50, 100, 500, 1000]

    def __init__(self, debug=False):
        return

    def connect(self):
        self.__api = Spot(key=api_key, secret=secret_key,
            exchange=self)
        self.__api.update_header({
            "Content-Type": "application/json;charset=utf-8",
            "User-Agent": Bitrue.name+'/python',
            "X-MBX-APIKEY": api_key})

    def _get_assetPrecision(self, ex_symbol):
        if ex_symbol not in self.symbol_info_map:
            sy_infos = self._exchange_info()['symbols']
            for sy_info in sy_infos:
                if ex_symbol == sy_info['symbol']:
                    self.symbol_info_map[sy_info['symbol']] = sy_info
        sy_info = self.symbol_info_map[ex_symbol]
        return sy_info['baseAssetPrecision'], sy_info['quotePrecision']

    # MARKETS
    def ping(self):
        return self.__api.ping()

    def time(self):
        return self.get_time_from_data_ts(self.__api.time()['serverTime'])

    def _exchange_info(self, ex_symbol: str = None, ex_symbols: list = None):
        return self.__api.exchange_info()

    def _depth(self, exchange_symbol, limit):
        return self.__api.depth(symbol=exchange_symbol, limit=limit)

    def _trades(self, exchange_symbol):
        trades = self.__api.trades(symbol=exchange_symbol)
        return trades

    def _historical_trades(self, exchange_symbol):
        trades = self.__api.historical_trades(symbol=exchange_symbol)
        return trades

    def _agg_trades(self, exchange_symbol):
        trades = self.__api.agg_trades(symbol=exchange_symbol)
        return trades

    def _ticker_price(self, exchange_symbol):
        return float(self.__api.ticker_price(exchange_symbol)['price'])

    def _klines(self, exchange_symbol, interval, size, since):
        return []

    # ACCOUNT(including orders and trades)
    def account(self):
        account = self.__api.account()
        nb = []
        balances = account['balances']
        for item in balances:
            if float(item['free'])==0 and float(item['locked'])==0:
                continue
            nb.append(item)
        account['balances'] = nb
        return account


    def get_balances(self):
        account = self.account()
        return account['balances']


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

    def _my_trades(self, exchange_symbol, limit):
        trades = self.__api.my_trades_v1(symbol=exchange_symbol, limit=limit)
        #trades += self.__api.my_trades_v2(symbol=exchange_symbol, limit=limit)
        return trades

    def _new_order(self, ex_side, ex_type, ex_symbol, price, qty, client_order_id=None):
        ret = self.__api.new_order(symbol=ex_symbol, side=ex_side, type=ex_type,
            timeInForce=TIME_IN_FORCE_GTC, price=price, quantity=qty)
        #print('_new_order:  ', ret)
        try:
            if ret['orderId']:

                #if ret['fills']:

                # self.debug('Return buy order ID: %s' % ret['orderId'])
                return ret['orderId']
            else:
                # self.debug('Place order failed')
                return None
        except Exception:
            # self.debug('Error result: %s' % ret)
            return None

    def _get_open_orders(self, exchange_symbol):
        orders = self.__api.get_open_orders(symbol=exchange_symbol)
        for o in orders:
            o[self.Order_Id_Key] = int(o[self.Order_Id_Key])
        return orders

    def _get_order(self, exchange_symbol, order_id):
        order = self.__api.get_order(symbol=exchange_symbol, orderId=order_id)
        if order:
            order[self.Order_Id_Key] = int(order[self.Order_Id_Key])
        return order

    def _get_orders(self, exchange_symbol, limit):
        orders = self.__api.get_orders(symbol=exchange_symbol, limit=limit)
        for o in orders:
            o[self.Order_Id_Key] = int(o[self.Order_Id_Key])
        return orders

    def _cancel_order(self, exchange_symbol, order_id):
        self.__api.cancel_order(symbol=exchange_symbol, orderId=order_id)

    def _cancel_open_orders(self, exchange_symbol):
        orders = self.__api.get_open_orders(symbol=exchange_symbol)
        for order in orders:
            order_id = order[self.Order_Id_Key]
            self.__api.cancel_order(symbol=exchange_symbol, orderId=order_id)

