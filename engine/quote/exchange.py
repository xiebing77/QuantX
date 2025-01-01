import common
from . import *


class ExchangeQuoteEngine(QuoteEngine):
    def __init__(self, quoter):
        super().__init__(quoter)

    def ticker_price(self, symbol):
        return self.quoter.ticker_price(symbol)

