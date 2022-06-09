import common
from . import *


def update_bill_position(pst, bill):
    new_pst = pst.copy()
    if pst[POSITION_BASE_QTY_KEY]==0:
        new_pst[POSITION_HISTORY_QUOTE_QTY_KEY] += pst[POSITION_QUOTE_QTY_KEY]

    bill_base_qty = bill['qty']
    bill_quote_qty = bill['qty'] * bill['price']

    if new_pst[POSITION_BASE_QTY_KEY]==0:
        new_pst[POSITION_QUOTE_QTY_KEY] = 0

    if bill[common.SIDE_KEY] == common.SIDE_BUY:
        new_pst[POSITION_BASE_QTY_KEY] += bill_base_qty
        new_pst[POSITION_QUOTE_QTY_KEY] -= bill_quote_qty
    else:
        new_pst[POSITION_BASE_QTY_KEY] -= bill_base_qty
        new_pst[POSITION_QUOTE_QTY_KEY] += bill_quote_qty

    new_pst[POSITION_DEAL_BASE_QTY_KEY] += bill_base_qty
    new_pst[POSITION_DEAL_QUOTE_QTY_KEY] += bill_quote_qty

    bill[POSITION_KEY] = new_pst
    return


def calc_position(bills):
    if len(bills) == 0:
        return init_position()

    if POSITION_KEY in bills[-1]:
        pst = bills[-1][POSITION_KEY]
        return pst

    if len(bills)>=2 and POSITION_KEY in bills[-2]:
        update_bill_position(bills[-2][POSITION_KEY],bills[-1])
        pst = bills[-1][POSITION_KEY]
        return pst

    pst = init_position()
    for bill in bills:
        update_bill_position(pst,bill)
        pst = bill[POSITION_KEY]
    return pst


class SimulationTradeEngine(TradeEngine):
    def __init__(self):
        super().__init__()
        self.bills = []
        self.now_time = None

    def new_limit_bill(self, side, symbol, price, qty, rmk=''):
        self.bills.append({
            common.ORDER_TYPE_KEY: common.ORDER_TYPE_LIMIT,
            "create_time": self.now_time,
            "symbol": symbol,
            common.BILL_STATUS_KEY: common.BILL_STATUS_CLOSE,
            common.SIDE_KEY: side,
            "price": price,
            "qty": qty,
            "rmk": rmk
        })

    def get_position(self, symbol):
        return calc_position(self.bills)

    def get_position_by_bills(self, bills):
        return calc_position(bills)

    def get_bills(self):
        return self.bills

    def reset_bills(self):
        self.bills = []
