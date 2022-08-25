import datetime
import common
import common.log as log
import setup
from db.mongodb import get_mongodb
from . import *

POSITION_ORDER_COUNT = 'order_count'


def update_position_by_order(trader, position, order):
    '''
    order_status = order[trader.ORDER_STATUS_KEY]
    if order_status in pst[POSITION_ORDER_COUNT]:
        pst[POSITION_ORDER_COUNT][order_status] += 1
    else:
        pst[POSITION_ORDER_COUNT][order_status] = 1
    '''
    base_qty = float(order[trader.Order_Key_ExecutedQty])
    if base_qty == 0:
        return
    quote_qty = float(order[trader.Order_Key_CummulativeQuoteQty])
    if trader.order_is_buy(order):
        side = common.SIDE_BUY
    else:
        side = common.SIDE_SELL
    update_position(position, side, base_qty, quote_qty)
    return


def get_commission_from_trades(trader, trades):
    commission = {}
    for trade in trades:
        if not trade[trader.Trade_Key_CommissionQty]:
            continue
        trade_commissionQty = abs(float(trade[trader.Trade_Key_CommissionQty]))
        asset_name = trade[trader.Trade_Key_CommissionAsset]
        if asset_name in commission:
            commission[asset_name] += trade_commissionQty
        else:
            commission[asset_name] = trade_commissionQty
    return commission


class ExchangeTradeEngine(TradeEngine):
    def __init__(self, instance_id, trader):
        super().__init__()
        self.instance_id = instance_id
        self.trader = trader
        self.trade_db = get_mongodb(setup.trade_db_name)
        self.bills_collection_name = 'bills'
        self.orders_collection_name = trader.name+'_orders'
        self.trades_collection_name = trader.name+'_trades'
        self.symbol_precs = {}
        self.position = None

    def get_symbol_prec(self, symbol):
        if symbol not in self.symbol_precs:
            b_prec, q_prec = self.trader.get_assetPrecision(symbol)
            self.symbol_precs[symbol] = (b_prec, q_prec)
        return self.symbol_precs[symbol]

    def new_limit_bill(self, side, symbol, price, qty, rmk=''):
        typ = common.ORDER_TYPE_LIMIT
        order_id = self.trader.new_order(side, typ, symbol, price, qty)
        if not order_id:
            return None
        _id = self.trade_db.insert_one(self.bills_collection_name, {
            "create_time": datetime.datetime.now(),#time.time(),
            "instance_id": self.instance_id,
            "symbol": symbol,
            common.BILL_STATUS_KEY: common.BILL_STATUS_OPEN,
            common.SIDE_KEY: side,
            common.ORDER_TYPE_KEY: typ,
            "price": price,
            "qty": qty,
            common.BILL_ORDER_ID_KEY: order_id,
            "rmk": rmk,
        })
        return order_id

    def cancel_bills(self, symbol, bills):
        orderIds = [bill[common.BILL_ORDER_ID_KEY] for bill in bills]
        self.trader.cancel_orders_byId(symbol, orderIds)

    def get_bills(self, symbol, bill_status):
        open_bills = self.trade_db.find(self.bills_collection_name, {
            "instance_id": self.instance_id,
            "symbol": symbol,
            common.BILL_STATUS_KEY: bill_status,
        })
        #pprint(open_bills)
        return open_bills

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

    def _get_orders_from_db(self, symbol, order_ids):
        query = {
            self.trader.Order_Id_Key: {"$in": order_ids},
        }
        orders = self.trade_db.find(self.orders_collection_name, query)
        return orders

    def _get_trades_from_db(self, symbol, order_ids):
        query = {
            self.trader.Order_Id_Key: {"$in": order_ids},
        }
        trades = self.trade_db.find(self.trades_collection_name, query)
        return trades

    def _init_position(self, symbol):
        pst = init_position()
        pst[POSITION_ORDER_COUNT] = 0
        close_bills = self.get_bills(symbol, common.BILL_STATUS_CLOSE)
        order_ids = [b[common.BILL_ORDER_ID_KEY] for b in close_bills]
        orders = self._get_orders_from_db(symbol, order_ids)
        print('_init_position:  ', len(order_ids), len(orders))
        if order_ids and not orders:
            log.critical("_init_position: not find orders")
        for order in orders:
            update_position_by_order(self.trader, pst, order)

        trades = self._get_trades_from_db(symbol, order_ids)
        pst[POSITION_KEY_COMMISSION] = get_commission_from_trades(self.trader, trades)

        return pst


    def get_position(self, symbol):
        self.handle_open_bills(symbol)
        return self.position


    def handle_open_bills(self, symbol):
        if not self.position:
            self.position = self._init_position(symbol)

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
                    commission = {}
                    if float(order[self.trader.Order_Key_ExecutedQty]) > 0:
                        if not trades:
                            trades = self.trader.my_trades(symbol)
                        r_trades = self.trader.search_trades(order_id, trades)
                        if r_trades:
                            # to continue. long time part filled
                            commission = get_commission_from_trades(self.trader, r_trades)
                            self.trade_db.insert_many(self.trades_collection_name, r_trades)
                    self.trade_db.insert_one(self.orders_collection_name, order)
                    self.trade_db.update_one(self.bills_collection_name, open_bill['_id'], {
                        common.BILL_STATUS_KEY: common.BILL_STATUS_CLOSE,
                    })
                    update_position_by_order(self.trader, self.position, order)
                    update_pst_commission(self.position, commission)
                    continue

            if open_bill[common.SIDE_KEY] == common.SIDE_BUY:
                buy_open_bills.append(open_bill)
            else:
                sell_open_bills.append(open_bill)
        return buy_open_bills, sell_open_bills


    def cancel_bills(self, symbol, bills):
        orderIds = [bill[common.BILL_ORDER_ID_KEY] for bill in bills]
        self.trader.cancel_orders_byId(symbol, orderIds)

