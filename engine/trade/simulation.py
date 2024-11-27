import common
from . import *


class SimulationTradeEngine(TradeEngine):
    def __init__(self, value, amount, commission_rate):
        super().__init__()
        self.value = value
        self.amount = amount
        self.commission_rate = commission_rate
        self.cell_bills = {}
        self.now_time = None

    def get_cell_value(self, cell_id):
        return self.value

    def get_cell_amount(self, cell_id):
        return self.amount

    def get_cell_slippage_rate(self, cell_id):
        return 0

    def get_all_cell_ids(self):
        return self.cell_bills.keys()

    def new_limit_bill(self, cell_id, side, symbol, multiplier, price, qty, rmk='', oc=None):
        bill = {
            common.BILL_KEY_CELL_ID: cell_id,
            common.ORDER_TYPE_KEY: common.ORDER_TYPE_LIMIT,
            "create_time": self.now_time,
            "symbol": symbol,
            "multiplier": multiplier,
            common.BILL_STATUS_KEY: common.BILL_STATUS_CLOSE,
            common.SIDE_KEY: side,
            "price": price,
            "qty": qty,
            "rmk": rmk
        }
        if oc:
            bill['oc'] = oc

        if cell_id in self.cell_bills:
            self.cell_bills[cell_id].append(bill)
        else:
            self.cell_bills[cell_id] = [bill]

    def update_bill_position(self, pst, bill):
        symbol = bill[common.BILL_SYMBOL_KEY]
        multiplier = self.get_multiplier_by_bill(bill)
        side = bill[common.SIDE_KEY]
        base_qty = bill['qty']
        quote_qty = bill['qty'] * bill['price'] * multiplier

        commission = {}
        new_pst = pst.copy()
        update_position(new_pst, symbol, multiplier, side, base_qty, quote_qty, commission)
        bill[POSITION_KEY] = new_pst
        return


    def calc_position(self, bills):
        if len(bills) == 0:
            return init_position()

        if POSITION_KEY in bills[-1]:
            pst = bills[-1][POSITION_KEY]
            return pst

        if len(bills)>=2 and POSITION_KEY in bills[-2]:
            self.update_bill_position(bills[-2][POSITION_KEY], bills[-1])
            pst = bills[-1][POSITION_KEY]
            return pst

        pst = init_position()
        for bill in bills:
            self.update_bill_position(pst, bill)
            pst = bill[POSITION_KEY]
        return pst

    def get_position(self, cell_id):
        if cell_id in self.cell_bills:
            bills = self.cell_bills[cell_id]
        else:
            bills = []
        return self.calc_position(bills)

    def get_position_by_bills(self, bills):
        return self.calc_position(bills)

    def get_all_bills(self, cell_id):
        if cell_id in self.cell_bills:
            return self.cell_bills[cell_id]
        else:
            return []

    def reset_bills(self, cell_id):
        self.cell_bills[cell_id] = []

    def reset_all_bills(self):
        self.cell_bills = {}

    def get_bill_deal_info(self, bill):
        return bill['qty'], bill['price']

    def get_bill_commission(self, bill):
        deal_qty, deal_price = self.get_bill_deal_info(bill)
        deal_value = deal_qty * deal_price * bill[common.BILL_MULTIPLIER_KEY]
        #return {self.trader.currency: deal_value * self.commission_rate}
        return {"CNY": deal_value * self.commission_rate}
