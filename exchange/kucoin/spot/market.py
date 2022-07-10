#!/usr/bin/python
from common import check_required_parameter, check_required_parameters, check_type_parameter, convert_list_to_json_array

# https://bybit-exchange.github.io/docs/spot


def time(self):
    """Check Server Time
    Test connectivity to the Rest API and get the current server time.
    """
    return self.query('/v1/timestamp')


def exchange_info(self):
    """Exchange Information
    Current exchange trading rules and symbol information
    """
    return self.query('/v1/symbols')


def depth_part(self, symbol: str, limit: int, **kwargs):
    """Get orderbook.

    Args:
        symbol (str): the trading pair
    Keyword Args:
        limit (int, optional): limit the results. Default 100; valid limits:[5, 10, 20, 50, 100, 500, 1000]
    """
    check_required_parameter(symbol, "symbol")
    params = {"symbol": symbol, **kwargs}
    return self.query("/v1/market/orderbook/level2_{}".format(limit), params)


def depth_all(self, symbol: str, **kwargs):
    """Get orderbook.

    Args:
        symbol (str): the trading pair
    Keyword Args:
        limit (int, optional): limit the results. Default 100; valid limits:[5, 10, 20, 50, 100, 500, 1000]
    """
    check_required_parameter(symbol, "symbol")
    params = {"symbol": symbol, **kwargs}
    return self.sign_request("GET", "/v3/market/orderbook/level2", params, version='2')


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
    return self.query("/quote/v1/trades", params)


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


def ticker_price(self, symbol: str = None):
    """Symbol Price Ticker
    Latest price for a symbol or symbols.

    Args:
        symbol (str, optional): the trading pair
    """

    params = {
        "symbol": symbol,
    }
    return self.query("/v1/market/orderbook/level1", params)


def book_ticker(self, symbol: str = None):
    """Symbol Order Book Ticker
    Best price/qty on the order book for a symbol or symbols.

    Args:
        symbol (str, optional): the trading pair
    """

    params = {
        "symbol": symbol,
    }
    return self.query("/quote/v1/ticker/bookTicker", params)

