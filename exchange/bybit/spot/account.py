from common import check_required_parameter, check_required_parameters


def new_order(self, symbol: str, side: str, type: str, **kwargs):
    """New Order (TRADE)

    Post a new order

    Args:
        symbol (str)
        side (str)
        type (str)
    Keyword Args:
        timeInForce (str, optional)
        quantity (float, optional)
        price (float, optional)
        newClientOrderId (str, optional): A unique id among open orders. Automatically generated if not sent.
        stopPrice (float, optional): Used with STOP_LOSS, STOP_LOSS_LIMIT, TAKE_PROFIT, and TAKE_PROFIT_LIMIT orders.
        icebergQty (float, optional): Used with LIMIT, STOP_LOSS_LIMIT, and TAKE_PROFIT_LIMIT to create an iceberg order.
        newOrderRespType (str, optional): Set the response JSON. ACK, RESULT, or FULL;
                MARKET and LIMIT order types default to FULL, all other orders default to ACK.
        recvWindow (int, optional): The value cannot be greater than 60000
    """

    check_required_parameters([[symbol, "symbol"], [side, "side"], [type, "type"]])
    params = {"symbol": symbol, "side": side, "type": type, **kwargs}
    return self.sign_request("POST", '/v1/order', params)


def cancel_order(self, symbol: str, **kwargs):
    """Cancel Order (TRADE)

    Cancel an active order.

    Args:
        symbol (str)
    Keyword Args:
        orderId (int, optional)
        origClientOrderId (str, optional)
        newClientOrderId (str, optional)
        recvWindow (int, optional): The value cannot be greater than 60000
    """
    check_required_parameter(symbol, "symbol")
    payload = {"symbol": symbol, **kwargs}
    return self.sign_request("DELETE", '/v1/order', payload)


def get_order(self, symbol, **kwargs):
    """Query Order (USER_DATA)

    Check an order's status.

    Args:
        symbol (str)
    Keyword Args:
        orderId (int, optional)
        origClientOrderId (str, optional)
        recvWindow (int, optional): The value cannot be greater than 60000
    """
    check_required_parameter(symbol, "symbol")
    payload = {"symbol": symbol, **kwargs}
    return self.sign_request("GET", '/v1/order', payload)


def get_open_orders(self, symbol=None, **kwargs):
    """Current Open Orders (USER_DATA)

    Get all open orders on a symbol.

    Args:
        symbol (str, optional)
    Keyword Args:
        recvWindow (int, optional): The value cannot be greater than 60000
    """

    payload = {"symbol": symbol, **kwargs}
    return self.sign_request("GET", '/v1/open-orders', payload)


def get_history_orders(self, symbol: str, **kwargs):
    """All Orders (USER_DATA)

    Get all account orders; active, canceled, or filled.

    Args:
        symbol (str)
    Keyword Args:
        orderId (int, optional)
        startTime (int, optional)
        endTime (int, optional)
        limit (int, optional): Default 100; max 1000.
        recvWindow (int, optional): The value cannot be greater than 60000
    """
    check_required_parameter(symbol, "symbol")
    payload = {"symbol": symbol, **kwargs}
    return self.sign_request("GET", '/v1/history-orders', payload)


def account(self, **kwargs):
    """Account Information (USER_DATA)

    Get current account information

    Keyword Args:
        recvWindow (int, optional): 
    """

    return self.sign_request("GET", '/v1/account', {**kwargs})


def my_trades(self, symbol: str, **kwargs):
    """Account Trade List (USER_DATA)

    Get trades for a specific account and symbol.

    Args:
        symbol (str)
    Keyword Args:
        startTime (int, optional)
        endTime (int, optional)
        fromId (int, optional): TradeId to fetch from. Default gets most recent trades.
        limit (int, optional): Default Value: 100; Max Value: 1000
        recvWindow (int, optional): 
    """

    check_required_parameter(symbol, "symbol")
    payload = {"symbol": symbol, **kwargs}
    return self.sign_request("GET", '/v1/myTrades', payload)

