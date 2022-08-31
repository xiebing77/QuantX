import datetime
from pprint import pprint
import common
import common.log as log
from common.position import init_position, update_position_by_order
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
        self.symbol_precs = {}

        self.position = {}

    def get_symbol_prec(self, symbol):
        if symbol not in self.symbol_precs:
            b_prec, q_prec = self.trader.get_assetPrecision(symbol)
            self.symbol_precs[symbol] = (b_prec, q_prec)
        return self.symbol_precs[symbol]

    def new_bill(self, side, type, symbol, price, qty):
        order_id = self.trader.new_order(side, type, symbol, price, qty)
        if not order_id:
            return None
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
                            # to continue. long time part filled
                            self.trade_db.insert_many(self.trades_collection_name, r_trades)
                    self.trade_db.insert_one(self.orders_collection_name, order)
                    self.trade_db.update_one(self.bills_collection_name, open_bill['_id'], {
                        common.BILL_STATUS_KEY: common.BILL_STATUS_CLOSE,
                    })
                    if not self.position:
                        self._init_position(symbol)
                    update_position_by_order(self.trader, symbol, self.position, order)
                    continue

            if open_bill[common.SIDE_KEY] == common.SIDE_BUY:
                buy_open_bills.append(open_bill)
            else:
                sell_open_bills.append(open_bill)
        return buy_open_bills, sell_open_bills

    def cancel_bills(self, symbol, bills):
        orderIds = [bill[common.BILL_ORDER_ID_KEY] for bill in bills]
        self.trader.cancel_orders_byId(symbol, orderIds)

    def _get_trades_from_db(self, symbol, order_ids):
        query = {
            self.trader.TRADE_ORDER_ID_KEY: {"$in": order_ids},
        }
        trades = self.trade_db.find(self.trades_collection_name, query)
        return trades

    def _get_orders_from_db(self, symbol, order_ids):
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

    def _init_position(self, symbol):
        calc_pst_start = datetime.datetime.now()
        close_bills = self.get_bills(symbol, common.BILL_STATUS_CLOSE)
        order_ids = [b[common.BILL_ORDER_ID_KEY] for b in close_bills]
        orders = self._get_orders_from_db(symbol, order_ids)
        self.position = init_position()
        for order in orders:
            update_position_by_order(self.trader, symbol, self.position, order)
        #pst_base_qty, pst_quote_qty, deal_base_qty, deal_quote_qty = self.calc_position_by_order(symbol, order_ids)
        #pst_base_qty, pst_quote_qty, deal_base_qty, deal_quote_qty = self.calc_position_by_trade(symbol, order_ids)
        log.info("calc cost: %s" % (datetime.datetime.now() - calc_pst_start))
        log.info("close bills: %s" % (len(close_bills)))

        self.handle_open_bills(symbol)

    def get_position(self, symbol, ticker_price):
        if not self.position:
            self._init_position(symbol)
        log.info('position: %s' % (self.position))
        pst_base_qty = self.position['base_qty']
        pst_quote_qty = self.position['quote_qty']
        deal_base_qty = self.position['deal_base_qty']
        deal_quote_qty = self.position['deal_quote_qty']

        b_prec, q_prec = self.get_symbol_prec(symbol)
        base_asset_name, quote_asset_name = common.split_symbol_coins(symbol)
        fmt = '%11s:  %15s %5s,  %20s %5s'
        log.info(fmt % ('deal qty', round(deal_base_qty, b_prec), base_asset_name,
            round(deal_quote_qty, 10), quote_asset_name))
        log.info(fmt % ('positon qty', round(pst_base_qty, b_prec), base_asset_name,
            round(pst_quote_qty, 10), quote_asset_name))

        floating_gross_profit = pst_quote_qty + pst_base_qty * ticker_price
        log.info('positon floating gross profit: %s %s' % (
            round(floating_gross_profit, 10), quote_asset_name))
        return pst_base_qty, pst_quote_qty, deal_quote_qty, floating_gross_profit

    def _calc_position_by_trade(self, symbol, order_ids):
        pst_base_qty = 0
        pst_quote_qty = 0
        deal_base_qty = 0
        deal_quote_qty = 0
        commission = None
        commission_asset = None

        trades = self._get_trades_from_db(symbol, order_ids)
        for trade in trades:
            qty = float(trade[self.trader.Trade_Key_Qty])
            price = float(trade[self.trader.Trade_Key_Price])
            value = qty * price
            if self.trader.mytrade_is_buyer(trade):
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


