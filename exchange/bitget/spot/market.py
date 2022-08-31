#!/usr/bin/python
from common import check_required_parameter, check_required_parameters, check_type_parameter, convert_list_to_json_array

# https://bybit-exchange.github.io/docs/spot


def time(self):
    """Check Server Time
    Test connectivity to the Rest API and get the current server time.
    """
    return self.query('/spot/v1/public/time')


def exchange_info(self):
    """Exchange Information
    Current exchange trading rules and symbol information
    """
    return self.query('/spot/v1/public/products')


def depth(self, symbol: str, **kwargs):
    """Get orderbook.

    Args:
        symbol (str): the trading pair
    Keyword Args:
        limit (int, optional): limit the results. Default 100; valid limits:[5, 10, 20, 50, 100, 500, 1000]
    """
    check_required_parameter(symbol, "symbol")
    params = {"symbol": symbol, **kwargs}
    return self.query("/spot/v1/market/depth", params)


def trades(self, symbol: str, **kwargs):
    """Recent Trades List
    Get recent trades (up to last 500).

    Args:
        symbol (str): the trading pair
    Keyword Args:
        limit (int, optional): limit the results. Default 100; max 1000.
    """
    check_required_parameter(symbol, "symbol")
    params = {"symbol": symbol, **kwargs}
    return self.query("/spot/v1/market/fills", params)


def klines(self, symbol: str, interval: str, **kwargs):
    """Kline/Candlestick Data

    Args:
        symbol (str): the trading pair
        interval (str): the interval of kline, e.g 1m, 5m, 1h, 1d, etc.
    Keyword Args:
        limit (int, optional): limit the results. Default 1000; max 1000.
        startTime (int, optional): Timestamp in ms to get aggregate trades from INCLUSIVE.
        endTime (int, optional): Timestamp in ms to get aggregate trades until INCLUSIVE.
    """
    check_required_parameters([[symbol, "symbol"], [interval, "interval"]])

    params = {"symbol": symbol, "interval": interval, **kwargs}
    return self.query("/quote/v1/kline", params)


def ticker(self, symbol: str = None):
    params = {
        "symbol": symbol,
    }
    return self.query("/spot/v1/market/ticker", params)

