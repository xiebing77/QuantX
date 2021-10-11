#!/usr/bin/python
from common import check_required_parameter, check_required_parameters, check_type_parameter, convert_list_to_json_array

# https://github.com/Bitrue-exchange/bitrue-official-api-docs

def ping(self):
    """Test Connectivity
    Test connectivity to the Rest API.
    """
    return self.query('/api/v1/ping')


def time(self):
    """Check Server Time
    Test connectivity to the Rest API and get the current server time.
    """
    return self.query('/api/v1/time')


def exchange_info(self):
    """Exchange Information
    Current exchange trading rules and symbol information
    """
    return self.query('/api/v1/exchangeInfo')


def depth(self, symbol: str, **kwargs):
    """Get orderbook.

    Args:
        symbol (str): the trading pair
    Keyword Args:
        limit (int, optional): limit the results. Default 100; valid limits:[5, 10, 20, 50, 100, 500, 1000]
    """
    check_required_parameter(symbol, "symbol")
    params = {"symbol": symbol, **kwargs}
    return self.query("/api/v1/depth", params)


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
    return self.query("/api/v1/trades", params)


def historical_trades(self, symbol: str, **kwargs):
    """Old Trade Lookup
    Get older market trades.

    Args:
        symbol (str): the trading pair
    Keyword Args:
        limit (int, optional): limit the results. Default 100; max 1000.
        formId (int, optional): trade id to fetch from. Default gets most recent trades.
    """
    check_required_parameter(symbol, "symbol")
    params = {"symbol": symbol, **kwargs}
    return self.limit_request("GET", "/api/v3/historicalTrades", params)


    check_required_parameters([[symbol, "symbol"]])
    params = {"symbol": symbol, **kwargs}
    return self.query('/api/v1/ticker/price', params)


def agg_trades(self, symbol: str, **kwargs):
    """Compressed/Aggregate Trades List
    Get compressed, aggregate trades. Trades that fill at the time, from the same order,
    with the same price will have the quantity aggregated.

    Args:
        symbol (str): the trading pair
    Keyword Args:
        limit (int, optional): limit the results. Default 500; max 1000.
        formId (int, optional): id to get aggregate trades from INCLUSIVE.
        startTime (int, optional): Timestamp in ms to get aggregate trades from INCLUSIVE.
        endTime (int, optional): Timestamp in ms to get aggregate trades until INCLUSIVE.

    If both startTime and endTime are sent, time between startTime and endTime must be less than 1 hour.
    If fromId, startTime, and endTime are not sent, the most recent aggregate trades will be returned.

    """

    check_required_parameter(symbol, "symbol")
    params = {"symbol": symbol, **kwargs}
    return self.query("/api/v1/aggTrades", params)


def ticker_price(self, symbol: str = None):
    """Symbol Price Ticker
    Latest price for a symbol or symbols.

    Args:
        symbol (str, optional): the trading pair
    """

    params = {
        "symbol": symbol,
    }
    return self.query("/api/v1/ticker/price", params)


def book_ticker(self, symbol: str = None):
    """Symbol Order Book Ticker
    Best price/qty on the order book for a symbol or symbols.

    Args:
        symbol (str, optional): the trading pair
    """

    params = {
        "symbol": symbol,
    }
    return self.query("/api/v3/ticker/bookTicker", params)

