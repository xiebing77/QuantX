import datetime
from pprint import pprint
import common
import common.log as log
import setup
from db.mongodb import get_mongodb


class TradeEngine(object):
    def __init__(self, instance_id, trader):
        self.instance_id = instance_id
        self.trader = trader
        self.trade_db = get_mongodb(setup.trade_db_name)
        self.bills_collection_name = 'bills'
        self.orders_collection_name = trader.name+'_orders'
        self.trades_collection_name = trader.name+'_trades'

    def new_bill(self, side, type, symbol, price, qty):
        order_id = self.trader.new_order(side, type, symbol, price, qty)
        _id = self.trade_db.insert_one(self.bills_collection_name, {
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

    def get_bills(self, symbol, bill_status):
        open_bills = self.trade_db.find(self.bills_collection_name, {
            "instance_id": self.instance_id,
            "symbol": symbol,
            common.BILL_STATUS_KEY: bill_status,
        })
        #pprint(open_bills)
        return open_bills

    def handle_open_bills(self, symbol):
        open_bills = self.get_bills(symbol, common.BILL_STATUS_OPEN)
        if not open_bills:
            return [], []

        open_orders = self.trader.get_open_orders(symbol)
        open_order_ids = [o[self.trader.Order_Id_Key] for o in open_orders]
        orders = None
        trades = None
        buy_open_bills = []
        sell_open_bills = []
        for open_bill in open_bills:
            order_id = open_bill[common.BILL_ORDER_ID_KEY]
            #log.info('%s %s %s'%(order_id, open_order_ids, order_id in open_order_ids))
            if order_id not in open_order_ids:
                if not orders:
                    orders = self.trader.get_orders(symbol)
                order = self.trader.search_order(order_id, orders)
                if not order:
                    order = self.trader.get_order(symbol, order_id)
                if not order:
                    log.debug('error bill: %s' % bill)
                if order and self.trader.check_status_is_close(order):
                    if float(order[self.trader.Order_Key_ExecutedQty]) > 0:
                        if not trades:
                            trades = self.trader.my_trades(symbol)
                        r_trades = self.trader.search_trades(order_id, trades)
                        if r_trades:
                            self.trade_db.insert_many(self.trades_collection_name, r_trades)
                    self.trade_db.insert_one(self.orders_collection_name, order)
                    self.trade_db.update_one(self.bills_collection_name, open_bill['_id'], {
                        common.BILL_STATUS_KEY: common.BILL_STATUS_CLOSE,
                    })
                    continue

            if open_bill[common.SIDE_KEY] == common.SIDE_BUY:
                buy_open_bills.append(open_bill)
            else:
                sell_open_bills.append(open_bill)
        return buy_open_bills, sell_open_bills

    def cancel_bills(self, symbol, bills):
        orderIds = [bill[common.BILL_ORDER_ID_KEY] for bill in bills]
        self.trader.cancel_orders_byId(symbol, orderIds)

    def get_trades_from_db(self, symbol, order_ids):
        query = {
            self.trader.TRADE_ORDER_ID_KEY: {"$in": order_ids},
        }
        trades = self.trade_db.find(self.trades_collection_name, query)
        return trades

    def get_orders_from_db(self, symbol, order_ids):
        query = {
            self.trader.Order_Id_Key: {"$in": order_ids},
        }
        orders = self.trade_db.find(self.orders_collection_name, query)
        return orders

    def get_order_from_db(self, symbol, order_id):
        orders = self.trade_db.find(self.orders_collection_name, {
            self.trader.Order_Id_Key: order_id,
        })

        if len(orders) > 1:
            log.debug('%s: %s' % (symbol, orders))
        elif len(orders) == 1:
            return orders[0]
        else:
            return None

    def get_position(self, symbol):
        close_bills = self.get_bills(symbol, common.BILL_STATUS_CLOSE)
        order_ids = [b[common.BILL_ORDER_ID_KEY] for b in close_bills]
        return self.calc_position_by_order(symbol, order_ids)
        #return self.calc_position_by_trade(symbol, order_ids)

    def calc_position_by_order(self, symbol, order_ids):
        order_count = {}
        pst_base_qty = 0
        pst_quote_qty = 0
        deal_base_qty = 0
        deal_quote_qty = 0

        orders = self.get_orders_from_db(symbol, order_ids)
        for order in orders:
            order_status = order[self.trader.ORDER_STATUS_KEY]
            if order_status in order_count:
                order_count[order_status] += 1
            else:
                order_count[order_status] = 1

            executed_qty = float(order[self.trader.Order_Key_ExecutedQty])
            if executed_qty == 0:
                continue
            value = float(order[self.trader.Order_Key_CummulativeQuoteQty])
            if self.trader.order_is_buy(order):
                pst_base_qty += executed_qty
                pst_quote_qty -= value
            else:
                pst_base_qty -= executed_qty
                pst_quote_qty += value
            deal_base_qty += executed_qty
            deal_quote_qty += value
        log.info('order count: %s' % (order_count))
        return pst_base_qty, pst_quote_qty, deal_base_qty, deal_quote_qty


    def calc_position_by_trade(self, symbol, order_ids):
        pst_base_qty = 0
        pst_quote_qty = 0
        deal_base_qty = 0
        deal_quote_qty = 0
        commission = None
        commission_asset = None

        trades = self.get_trades_from_db(symbol, order_ids)
        for trade in trades:
            qty = float(trade[self.trader.Trade_Key_Qty])
            price = float(trade[self.trader.Trade_Key_Price])
            value = qty * price
            if trade[self.trader.Trade_Key_IsBuyer]:
                pst_base_qty += qty
                pst_quote_qty -= value
            else:
                pst_base_qty -= qty
                pst_quote_qty += value
            deal_base_qty += qty
            deal_quote_qty += value

            if self.trader.Trade_Key_CommissionAsset in trade:
                if not commission_asset:
                    commission_asset = trade[self.trader.Trade_Key_CommissionAsset]
                    commission = float([self.trader.Trade_Key_CommissionQty])
                else:
                    commission += float([self.trader.Trade_Key_CommissionQty])

        return pst_base_qty, pst_quote_qty, deal_base_qty, deal_quote_qty


