from common import check_required_parameter, check_required_parameters


def new_order(self, symbol: str, side: str, type: str, price: float, size: float, clientOid: str, **kwargs):
    check_required_parameters([[symbol, "symbol"], [side, "side"], [type, "type"]])
    params = {"symbol": symbol, "side": side, "type": type,
        "price": str(price), "size": str(size), "clientOid": clientOid, **kwargs}
    return self.sign_request("POST", '/v1/orders', params)


def cancel_order(self, orderId: str, **kwargs):
    check_required_parameter(orderId, "orderId")
    return self.sign_request("DELETE", '/v1/orders/'+orderId)


def get_order(self, orderId: str, **kwargs):
    check_required_parameter(orderId, "orderId")
    return self.sign_request("GET", '/v1/orders/'+orderId)


def get_open_orders(self, symbol=None, **kwargs):
    payload = {"symbol": symbol, "status": 'active', **kwargs}
    return self.sign_request("GET", '/v1/orders', payload)


def get_orders(self, symbol: str, **kwargs):
    check_required_parameter(symbol, "symbol")
    payload = {"symbol": symbol, **kwargs}
    return self.sign_request("GET", '/v1/orders', payload)


def account(self, **kwargs):
    return self.sign_request("GET", '/v1/accounts', {**kwargs})


def my_trades(self, symbol: str, **kwargs):
    check_required_parameter(symbol, "symbol")
    payload = {"symbol": symbol, **kwargs}
    return self.sign_request("GET", '/v1/fills', payload)

