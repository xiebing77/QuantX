import datetime
import common
import common.log as log
import setup
from db.mongodb import get_mongodb
from . import *

POSITION_ORDER_COUNT = 'order_count'


def update_position_by_order(symbol, multiplier, trader, position, order, commission):
    position[POSITION_ORDER_COUNT] += 1
    base_qty = trader.get_order_exec_qty(order)
    if base_qty == 0:
        return
    quote_qty = multiplier * trader.get_order_exec_quote_qty(order)

    if hasattr(trader, 'currency'):
        base_asset_name = None
        quote_asset_name = trader.currency
    else:
        base_asset_name, quote_asset_name = common.split_symbol_coins(symbol)
        base_asset_name = trader._get_coinkey(base_asset_name)
        quote_asset_name = trader._get_coinkey(quote_asset_name)

    if trader.order_is_buy(order):
        side = common.SIDE_BUY
        if base_asset_name in commission:
            fee_base = abs(commission[base_asset_name])
            fee = (fee_base / base_qty) * quote_qty
            base_qty -= fee_base
            del commission[base_asset_name]
            commission[quote_asset_name] = fee
            quote_qty -= fee #
        elif quote_asset_name in commission:
            fee = abs(commission[quote_asset_name])
            #quote_qty += fee
        else:
            pass
    else:
        side = common.SIDE_SELL
        if quote_asset_name in commission:
            fee = abs(commission[quote_asset_name])
            #quote_qty -= fee
        elif base_asset_name in commission:
            log.critical('{}'.format(commission))
        else:
            pass

    update_position(position, symbol, multiplier, side, base_qty, quote_qty, commission)
    return


def get_commission_from_trades(trader, trades):
    commission = {}
    for trade in trades:
        trade_commissionQty = abs(float(trade[trader.Trade_Key_CommissionQty]))
        if hasattr(trader, 'Trade_Key_CommissionAsset'):
            asset_name = trade[trader.Trade_Key_CommissionAsset]
        else:
            asset_name = trader.currency
        if asset_name in commission:
            commission[asset_name] += trade_commissionQty
        else:
            commission[asset_name] = trade_commissionQty
    return commission


def calc_commission_by_trades(bill, trader, trades, commission_rate, commission_prec):
    commission = {}
    asset_name = trader.currency
    for trade in trades:
        trade_commissionQty = (float(trade[trader.Trade_Key_Price]) *
                               float(trade[trader.Trade_Key_Qty]) *
                               bill[common.BILL_MULTIPLIER_KEY] *
                               commission_rate)
        trade_commissionQty = round(trade_commissionQty, commission_prec)
        if asset_name in commission:
            commission[asset_name] += trade_commissionQty
        else:
            commission[asset_name] = trade_commissionQty
    return commission


def round_commission(commission):
    for coin in commission:
        commission[coin] = round(commission[coin], 8)
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
        self.commission_rate = None
        self.commission_prec = None

    def get_symbol_prec(self, symbol):
        if symbol not in self.symbol_precs:
            b_prec, q_prec = self.trader.get_assetPrecision(symbol)
            self.symbol_precs[symbol] = (b_prec, q_prec)
        return self.symbol_precs[symbol]

    def set_commission(self, rate, prec):
        self.commission_rate = rate
        self.commission_prec = prec

    def new_limit_bill(self, side, symbol, multiplier, price, qty, rmk='', oc=None):
        typ = common.ORDER_TYPE_LIMIT
        ret = self.trader.new_order(side, typ, symbol, price, qty, oc=oc)
        #print('new_limit_bill ret type: {}  {}'.format(type(ret), ret))
        if not ret:
            return None

        if type(ret) in [str, int] :
            order_id = ret
        else:
            order = ret
            order_id = order[self.trader.Order_Id_Key]
        if not order_id:
            return None
        bill = {
            "create_time": datetime.datetime.now(),#time.time(),
            "instance_id": self.instance_id,
            common.BILL_SYMBOL_KEY: symbol,
            common.BILL_MULTIPLIER_KEY: multiplier,
            common.BILL_STATUS_KEY: common.BILL_STATUS_OPEN,
            common.SIDE_KEY: side,
            common.ORDER_TYPE_KEY: typ,
            "price": price,
            "qty": qty,
            common.BILL_ORDER_ID_KEY: order_id,
            "rmk": rmk,
        }
        if oc:
            bill['oc'] = oc
        _id = self.trade_db.insert_one(self.bills_collection_name, bill)
        return ret

    def cancel_bills(self, bills):
        for bill in bills:
            symbol  = bill[common.BILL_SYMBOL_KEY]
            orderId = bill[common.BILL_ORDER_ID_KEY]
            self.trader.cancel_orders(symbol, orderId)

    def get_bills(self, bill_status):
        open_bills = self.trade_db.find(self.bills_collection_name, {
            "instance_id": self.instance_id,
            common.BILL_STATUS_KEY: bill_status,
        })
        #pprint(open_bills)
        return open_bills

    def get_bill(self, order_id):
        bills = self.trade_db.find(self.bills_collection_name, {
            "instance_id": self.instance_id,
            "order_id": order_id})
        #pprint(bills)
        if len(bills) > 1:
            log.debug('{}'.format(bills))
        elif len(bills) == 1:
            return bills[0]
        else:
            return None

    def get_order_from_db(self, order_id):
        orders = self.trade_db.find(self.orders_collection_name, {
            self.trader.Order_Id_Key: order_id,
        })

        if len(orders) > 1:
            log.debug('%s: %s' % (orders))
        elif len(orders) == 1:
            return orders[0]
        else:
            return None

    def _get_orders_from_db(self, order_ids):
        query = {
            self.trader.Order_Id_Key: {"$in": order_ids},
        }
        orders = self.trade_db.find(self.orders_collection_name, query)
        return orders

    def _get_trades_from_db(self, order_ids):
        query = {
            self.trader.Order_Id_Key: {"$in": order_ids},
        }
        trades = self.trade_db.find(self.trades_collection_name, query)
        return trades

    def _get_commission_from_trades(self, bill, trades):
        commission = {}
        if len(trades) == 0:
            return commission

        if hasattr(self.trader, 'Trade_Key_CommissionQty'):
            commission = get_commission_from_trades(self.trader, trades)
        elif self.commission_rate:
            commission = calc_commission_by_trades(bill, self.trader, trades,
                self.commission_rate, self.commission_prec)
        return commission

    def _init_position(self):
        pst = init_position()
        pst[POSITION_ORDER_COUNT] = 0
        close_bills = self.get_bills(common.BILL_STATUS_CLOSE)
        order_ids = [b[common.BILL_ORDER_ID_KEY] for b in close_bills]
        log.info('_init_position:  {} {}'.format(len(order_ids), len(close_bills)))
        for bill in close_bills:
            symbol = bill[common.BILL_SYMBOL_KEY]
            multiplier = self.get_multiplier_by_bill(bill)
            order_id = bill[common.BILL_ORDER_ID_KEY]
            order = self.get_order_from_db(order_id)
            if not order:
                log.critical("_init_position: not find order! id: {}".format(order_id))
                continue
            #order_id = order[self.trader.Order_Id_Key]
            trades = self._get_trades_from_db([order_id])
            commission = self._get_commission_from_trades(bill, trades)
            update_position_by_order(symbol, multiplier, self.trader, pst, order, commission)
        return pst


    def get_position(self):
        self.handle_open_bills()
        return self.position

    def close_bill_to_db(self, bill, order, trades):
        if len(trades) > 0:
            self.trade_db.insert_many(self.trades_collection_name, trades)
        self.trade_db.insert_one(self.orders_collection_name, order)
        self.trade_db.update_one(self.bills_collection_name, bill['_id'],
            {common.BILL_STATUS_KEY: common.BILL_STATUS_CLOSE})
        commission = self._get_commission_from_trades(bill, trades)
        return commission


    def sync_bill(self, order, trades):
        if not self.trader.check_status_is_close(order):
            return
        order_id = order[self.trader.Order_Id_Key]
        bill = self.get_bill(order_id)
        if not bill:
            return
        symbol = bill[common.BILL_SYMBOL_KEY]
        multiplier = self.get_multiplier_by_bill(bill)
        commission = self.close_bill_to_db(bill, order, trades)
        update_position_by_order(symbol, multiplier, self.trader,
                                 self.position, order, commission)
        print('sync_bill => ', self.position)


    def handle_open_bills(self):
        if not self.position:
            self.position = self._init_position()

        open_bills = self.get_bills(common.BILL_STATUS_OPEN)
        if not open_bills:
            return [], []

        orders = None
        trades = None
        buy_open_bills = []
        sell_open_bills = []
        for open_bill in open_bills:
            symbol = open_bill[common.BILL_SYMBOL_KEY]
            open_orders = self.trader.get_open_orders(symbol)
            open_order_ids = [o[self.trader.Order_Id_Key] for o in open_orders]

            order_id = open_bill[common.BILL_ORDER_ID_KEY]
            #log.info('%s %s %s'%(order_id, open_order_ids, order_id in open_order_ids))
            if order_id not in open_order_ids:
                if not orders:
                    orders = self.trader.get_orders(symbol)
                order = self.trader.search_order(order_id, orders)
                if not order:
                    order = self.trader.get_order(symbol, order_id)
                if not order:
                    log.debug('not order: %s' % open_bill)
                    self.trade_db.update_one(self.bills_collection_name, open_bill['_id'], {
                        common.BILL_STATUS_KEY: common.BILL_STATUS_CLOSE,
                    })
                if order and self.trader.check_status_is_close(order):
                    r_trades = []
                    if self.trader.get_order_exec_qty(order) > 0:
                        if not trades:
                            trades = self.trader.my_trades(symbol)
                        r_trades = self.trader.search_trades(order_id, trades)
                    multiplier = self.get_multiplier_by_bill(open_bill)
                    commission = self.close_bill_to_db(open_bill, order, r_trades)
                    update_position_by_order(symbol, multiplier, self.trader,
                                             self.position, order, commission)
                    continue

            if open_bill[common.SIDE_KEY] == common.SIDE_BUY:
                buy_open_bills.append(open_bill)
            else:
                sell_open_bills.append(open_bill)
        print('handle_open_bills => ', self.position)
        return buy_open_bills, sell_open_bills

