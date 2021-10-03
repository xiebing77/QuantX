#!/usr/bin/python
""""""
import sys
sys.path.append('../')
from interface.market_data import MarketData
from interface.trade import Trade
from common import get_symbol_coins


class Exchange(MarketData, Trade):
    def __init__(self):
        return

    def _trans_symbol(self, symbol):
        target_coin, base_coin = get_symbol_coins(symbol)
        return '%s%s' % (self._get_coinkey(target_coin), self._get_coinkey(base_coin))

