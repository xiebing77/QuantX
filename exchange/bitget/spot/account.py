from common import check_required_parameter, check_required_parameters


def new_order(self, symbol: str, side: str, type: str, price: float, size: float, clientOid: str, **kwargs):
    check_required_parameters([[symbol, "symbol"], [side, "side"], [type, "type"]])
    params = {"symbol": symbol, "side": side, "orderType": type, "force": "normal",
        "price": str(price), "quantity": str(size), "clientOrderId": clientOid, **kwargs}
    return self.sign_request("POST", '/spot/v1/trade/orders', params)


def cancel_order(self, symbol: str, orderId: str):
    check_required_parameter(orderId, "orderId")
    payload = {"symbol": symbol, "orderId": orderId}
    return self.sign_request("POST", '/spot/v1/trade/cancel-order', payload)


def get_order(self, symbol: str, orderId: str, **kwargs):
    check_required_parameter(orderId, "orderId")
    payload = {"symbol": symbol, "orderId": orderId, **kwargs}
    return self.sign_request("POST", '/spot/v1/trade/orderInfo', payload)


def get_open_orders(self, symbol=None, **kwargs):
    payload = {"symbol": symbol, **kwargs}
    return self.sign_request("POST", '/spot/v1/trade/open-orders', payload)


def get_orders(self, symbol: str, **kwargs):
    check_required_parameter(symbol, "symbol")
    payload = {"symbol": symbol, **kwargs}
    return self.sign_request("POST", '/spot/v1/trade/history', payload)


def account(self, **kwargs):
    return self.sign_request("GET", '/spot/v1/account/assets', {**kwargs})


def my_trades(self, symbol: str, **kwargs):
    check_required_parameter(symbol, "symbol")
    payload = {"symbol": symbol, **kwargs}
    return self.sign_request("POST", '/spot/v1/trade/fills', payload)

