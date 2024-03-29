#!/usr/bin/python
"""exchange factory"""

from exchange.binance.binance_spot import BinanceSpot
from exchange.bitrue.bitrue_spot import BitrueSpot
from exchange.bybit.bybit_spot import BybitSpot
from exchange.kucoin.kucoin_spot import KucoinSpot
from exchange.bingx.bingx_spot import BingXSpot
from exchange.bitget.bitget_spot import BitgetSpot
from exchange.kuaiqi.kuaiqi_futures import KuaiqiFutures, KuaiqiFuturesSim


exchangeClasses = [BinanceSpot, BitrueSpot, BybitSpot, KucoinSpot, BingXSpot, BitgetSpot, KuaiqiFutures, KuaiqiFuturesSim]


def get_exchange_names():
    return [ ec.name for ec in exchangeClasses]


def create_exchange(exchange_name, broker=None):
    for ec in exchangeClasses:
        if ec.name == exchange_name:
            return ec(broker, debug=True)
    return None

