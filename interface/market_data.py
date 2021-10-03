#!/usr/bin/python
""""""
import kline as kl

kline_default_size = 300


class MarketData():

    def get_price(self, symbol):
        return self._get_price(self._trans_symbol(symbol))

    def get_klines(self, symbol, interval, size=kline_default_size, since=None):
        return self._get_klines(self._trans_symbol(symbol),
            self.ex_interval[interval], size, since)

    def get_klines_1day(self, symbol, size=kline_default_size, since=None):
        return self.get_klines(symbol, kl.KLINE_INTERVAL_1DAY, size, since)

    def get_klines_1min(self, symbol, size=kline_default_size, since=None):
        return self.get_klines(symbol, kl.KLINE_INTERVAL_1MINUTE, size, since)

    def get_klines_1hour(self, symbol, size=kline_default_size, since=None):
        return self.get_klines(symbol, kl.KLINE_INTERVAL_1HOUR, size, since)

    def get_order_book(self, symbol, limit=100):
        return self._get_order_book(self._trans_symbol(symbol), limit=limit)

