#!/usr/bin/python
from common import check_required_parameter, check_required_parameters, check_type_parameter, convert_list_to_json_array


def ping(self):
    """Test Connectivity
    Test connectivity to the Rest API.
    """
    return self.query('/openApi/spot/v1/ping')


def time(self):
    """Check Server Time
    Test connectivity to the Rest API and get the current server time.
    """
    return self.query('/openApi/spot/v1/time')


def exchange_info(self, symbol: str):
    """Exchange Information
    Current exchange trading rules and symbol information
    """
    params = {"symbol": symbol}
    return self.query('/openApi/spot/v1/common/symbols', params)


def depth(self, symbol: str, **kwargs):
    """Get orderbook.

    Args:
        symbol (str): the trading pair
    Keyword Args:
        limit (int, optional): limit the results. Default 100; valid limits:[5, 10, 20, 50, 100, 500, 1000]
    """
    check_required_parameter(symbol, "symbol")
    params = {"symbol": symbol, **kwargs}
    return self.query("/openApi/spot/v1/market/depth", params)


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
    return self.query('/openApi/spot/v1/market/trades', params)



def ticker_price(self, symbol: str = None):
    """Symbol Price Ticker
    Latest price for a symbol or symbols.

    Args:
        symbol (str, optional): the trading pair
    """

    params = {
        "symbol": symbol,
    }
    return self.query("/api/v1/market/getTicker", params)


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

