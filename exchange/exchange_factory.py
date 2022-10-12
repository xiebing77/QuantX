#!/usr/bin/python
"""exchange factory"""

from exchange.binance.binance_spot import BinanceSpot
from exchange.bitrue.bitrue_spot import BitrueSpot
from exchange.bybit.bybit_spot import BybitSpot
from exchange.kucoin.kucoin_spot import KucoinSpot
from exchange.bingx.bingx_spot import BingXSpot
from exchange.bitget.bitget_spot import BitgetSpot
from exchange.kuaiqi import KuaiQi


exchangeClasses = [BinanceSpot, BitrueSpot, BybitSpot, KucoinSpot, BingXSpot, BitgetSpot, KuaiQi]


def get_exchange_names():
    return [ ec.name for ec in exchangeClasses]


def create_exchange(exchange_name):
    for ec in exchangeClasses:
        if ec.name == exchange_name:
            return ec(debug=True)
    return None

