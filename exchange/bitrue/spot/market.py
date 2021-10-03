#!/usr/bin/python
from common import check_required_parameter, check_required_parameters

    
def ping(self):
    return self.query('/api/v1/ping')

def time(self):
    return self.query('/api/v1/time')

def ticker_price(self, symbol: str, **kwargs):
    check_required_parameters([[symbol, "symbol"]])
    params = {"symbol": symbol, **kwargs}
    return self.query('/api/v1/ticker/price', params)

def depth(self, symbol: str, **kwargs):
    check_required_parameter(symbol, "symbol")
    params = {"symbol": symbol, **kwargs}
    return self.query("/api/v1/depth", params)


