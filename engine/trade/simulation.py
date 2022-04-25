import datetime
import common

from . import POSITION_KEY, POSITION_BASE_QTY_KEY, POSITION_QUOTE_QTY_KEY, POSITION_DEAL_BASE_QTY_KEY, POSITION_DEAL_QUOTE_QTY_KEY
from . import POSITION_HISTORY_QUOTE_QTY_KEY

def update_bill_position(pst, bill):
    if pst:
        new_pst = pst.copy()
    else:
        new_pst = {
            POSITION_BASE_QTY_KEY: 0,
            POSITION_QUOTE_QTY_KEY: 0,
            POSITION_HISTORY_QUOTE_QTY_KEY: 0,
            POSITION_DEAL_BASE_QTY_KEY: 0,
            POSITION_DEAL_QUOTE_QTY_KEY: 0
        }
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

    if new_pst[POSITION_BASE_QTY_KEY]==0:
        new_pst[POSITION_HISTORY_QUOTE_QTY_KEY] += new_pst[POSITION_QUOTE_QTY_KEY]

    new_pst[POSITION_DEAL_BASE_QTY_KEY] += bill_base_qty
    new_pst[POSITION_DEAL_QUOTE_QTY_KEY] += bill_quote_qty

    bill[POSITION_KEY] = new_pst
    return


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
        bills = self.bills
        if len(bills) == 0:
            return None

        if POSITION_KEY in bills[-1]:
            pst = bills[-1][POSITION_KEY]
            return pst

        if len(bills)>=2 and POSITION_KEY in bills[-2]:
            update_bill_position(bills[-2][POSITION_KEY],bills[-1])
            pst = bills[-1][POSITION_KEY]
            return pst

        pst = None
        for bill in bills:
            update_bill_position(pst,bill)
            pst = bill[POSITION_KEY]
        return pst
