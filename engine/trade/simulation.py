import common
from . import calc_position

class SimulationTradeEngine(object):
    def __init__(self):
        self.bills = []
        self.now_time = None

    def new_limit_bill(self, side, symbol, price, qty, slippage_rate=0, rmk=''):
        if side == common.SIDE_BUY:
            limit_price = price * (1+slippage_rate)
        else:
            limit_price = price * (1-slippage_rate)
        self.bills.append({
            common.ORDER_TYPE_KEY: common.ORDER_TYPE_LIMIT,
            "create_time": self.now_time,
            "symbol": symbol,
            common.BILL_STATUS_KEY: common.BILL_STATUS_CLOSE,
            common.SIDE_KEY: side,
            "price": limit_price,
            "qty": qty,
            "rmk": rmk
        })

    def get_position(self, symbol):
        return calc_position(self.bills)

    def get_bills(self):
        return self.bills

    def reset_bills(self):
        self.bills = []
