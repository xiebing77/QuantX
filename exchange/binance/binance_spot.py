#!/usr/bin/python
"""binance spot"""
import os
from datetime import datetime
from .binance import Binance, api_key, secret_key
from .spot import Spot
from common import create_balance


class BinanceSpot(Binance):
    name = Binance.name + '_spot'
    start_time = datetime(2017, 8, 17, 8)

    def __init__(self, debug=False):
        return

    def connect(self):
        self.__api = Spot(key=api_key, secret=secret_key,
            user_agent=Binance.name+'/python', exchange=self)

    # ACCOUNT(including orders and trades)
    def ping(self):
        return self.__api.ping()

    def time(self):
        return self.get_time_from_data_ts(self.__api.time()['serverTime'])

    def exchange_info(self):
        return self.exchange_info()

    def _depth(self, exchange_symbol, limit=100):
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

    def _get_klines(self, exchange_symbol, interval, size, since):
        if since is None:
            klines = self.__api.get_klines(symbol=exchange_symbol, interval=interval, limit=size)
        else:
            klines = self.__api.get_klines(symbol=exchange_symbol, interval=interval, limit=size, startTime=since)

        return klines

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


    def get_all_balances(self):
        """获取余额"""
        balances = []
        account = self.account()
        for item in account['balances']:
            balance = create_balance(item['asset'], item['free'], item['locked'])
            balances.append(balance)
        return balances


    def get_balances(self, *coins):
        """获取余额"""
        coin_balances = []
        account = self.account()
        balances = account['balances']
        for coin in coins:
            coinKey = self.__get_coinkey(coin)
            for item in balances:
                if coinKey == item['asset']:
                    balance = create_balance(coin, item['free'], item['locked'])
                    coin_balances.append(balance)
                    break
        if len(coin_balances) <= 0:
            return
        elif len(coin_balances) == 1:
            return coin_balances[0]
        else:
            return tuple(coin_balances)

    def _my_trades(self, exchange_symbol):
        trades = self.__api.my_trades(symbol=exchange_symbol)
        return trades

    def _new_order(self, binance_side, binance_type, exchange_symbol, price, amount, client_order_id=None):
        ret = self.__api.new_order(symbol=exchange_symbol, side=binance_side, type=binance_type,
            timeInForce=TIME_IN_FORCE_GTC, price=price, quantity=amount)
        log.debug(ret)
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
        return orders

    def _get_order(self, exchange_symbol, order_id):
        return self.__api.get_order(symbol=exchange_symbol, orderId=order_id)

    def _cancel_order(self, exchange_symbol, order_id):
        self.__api.cancel_order(symbol=exchange_symbol, orderId=order_id)

    def _cancel_open_orders(self, exchange_symbol):
        self.__api.cancel_open_orders(symbol=exchange_symbol)

