#!/usr/bin/python
""""""
import kline as kl

kline_default_size = 200


class MarketData():

    def depth(self, symbol, limit):
        return self._depth(self._trans_symbol(symbol), limit=limit)

    def trades(self, symbol):
        trades = self._trades(symbol=self._trans_symbol(symbol))
        return trades

    def historical_trades(self, symbol):
        trades = self._historical_trades(symbol=self._trans_symbol(symbol))
        return trades

    def agg_trades(self, symbol):
        trades = self._agg_trades(symbol=self._trans_symbol(symbol))
        return trades

    def ticker_price(self, symbol):
        return self._ticker_price(self._trans_symbol(symbol))

    def klines(self, symbol, interval, size=kline_default_size, since=None):
        return self._klines(self._trans_symbol(symbol),
            self.ex_interval[interval], size, since)

    def klines_1day(self, symbol, size=kline_default_size, since=None):
        return self.klines(symbol, kl.KLINE_INTERVAL_1DAY, size, since)

    def klines_1min(self, symbol, size=kline_default_size, since=None):
        return self.klines(symbol, kl.KLINE_INTERVAL_1MINUTE, size, since)

    def klines_1hour(self, symbol, size=kline_default_size, since=None):
        return self.klines(symbol, kl.KLINE_INTERVAL_1HOUR, size, since)

