import datetime
from pprint import pprint
import common
import setup
from db.mongodb import get_mongodb

DB_BILLS_NAME = 'bills'

class TradeEngine(object):
    def __init__(self, instance_id, trader):
        self.instance_id = instance_id
        self.trade_db = get_mongodb(setup.trade_db_name)
        self.trader = trader

    def new_bill(self, side, type, symbol, price, qty):
        order_id = self.trader.new_order(side, type, symbol, price, qty)
        _id = self.trade_db.insert_one(DB_BILLS_NAME, {
            "create_time": datetime.datetime.now(),#time.time(),
            "instance_id": self.instance_id,
            "symbol": symbol,
            common.BILL_STATUS_KEY: common.BILL_STATUS_OPEN,
            common.SIDE_KEY: side,
            common.ORDER_TYPE_KEY: type,
            "price": price,
            "qty": qty,
            common.BILL_ORDER_ID_KEY: order_id,
        })
        return order_id

    def get_open_bills(self, symbol):
        open_bills = self.trade_db.find(DB_BILLS_NAME, {
            "instance_id": self.instance_id,
            "symbol": symbol,
            common.BILL_STATUS_KEY: common.BILL_STATUS_OPEN,
        })

        buy_open_bills = []
        sell_open_bills = []
        if open_bills:
            #pprint(open_bills)
            open_order_ids = [open_bill[common.BILL_ORDER_ID_KEY] for open_bill in open_bills]
            close_order_ids = self.trader.check_orders_close_status(symbol, open_order_ids)
            #print(open_order_ids, close_order_ids)
            for open_bill in open_bills:
                order_id = open_bill[common.BILL_ORDER_ID_KEY]
                #print(order_id, close_order_ids)
                #print(type(order_id), type(close_order_ids[0]) if close_order_ids else None, order_id in close_order_ids)
                if order_id in close_order_ids:
                    self.trade_db.update_one(DB_BILLS_NAME, open_bill['_id'], {
                        common.BILL_STATUS_KEY: common.BILL_STATUS_CLOSE,
                    })
                else:
                    if open_bill[common.SIDE_KEY] == common.SIDE_BUY:
                        buy_open_bills.append(open_bill)
                    else:
                        sell_open_bills.append(open_bill)

        return buy_open_bills, sell_open_bills

    def cancel_bills(self, symbol, bills):
        orderIds = [bill[common.BILL_ORDER_ID_KEY] for bill in bills]
        self.trader.cancel_orders_byId(symbol, orderIds)


