import datetime
import common
from common import get_orderids_by_bill, get_orderids_by_bills
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


def collect_commission_from_trades(trader, trades):
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


def calc_commission_by_trades(multiplier, trader, trades, commission_rate, commission_prec):
    commission = {}
    asset_name = trader.currency
    for trade in trades:
        trade_commissionQty = (float(trade[trader.Trade_Key_Price]) *
                               float(trade[trader.Trade_Key_Qty]) *
                               multiplier *
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
    def __init__(self, config=None):
        super().__init__(config)
        self.trade_db = get_mongodb(setup.trade_db_name)
        self.bills_collection_name = 'bills'
        self.symbol_precs = {}

        self.position = {}
        self.cells = {}

    def get_symbol_prec(self, trader, symbol):
        if symbol not in self.symbol_precs:
            b_prec, q_prec = trader.get_assetPrecision(symbol)
            self.symbol_precs[symbol] = (b_prec, q_prec)
        return self.symbol_precs[symbol]

    def set_cell(self, cell_id, trader, value, amount, slippage_rate, rate, prec):
        if cell_id in self.cells:
            return
        if value and amount:
            return
        if not value and not amount:
            return
        cell = {
            'cell_id': cell_id,
            'trader': trader,
            'orders_collection_name': trader.name+'_orders',
            'trades_collection_name': trader.name+'_trades',
            'value': value,
            'amount': amount,
            'slippage_rate': slippage_rate,
            'commission_rate': rate,
            'commission_prec': prec
        }
        self.cells[cell_id] = cell

    def get_cell_trader(self, cell_id):
        cell = self.cells[cell_id]
        return cell['trader']

    def get_cell_orders_collection_name(self, cell_id):
        cell = self.cells[cell_id]
        return cell['orders_collection_name']

    def get_cell_trades_collection_name(self, cell_id):
        cell = self.cells[cell_id]
        return cell['trades_collection_name']

    def get_cell_value(self, cell_id):
        cell = self.cells[cell_id]
        return cell['value']

    def get_cell_amount(self, cell_id):
        cell = self.cells[cell_id]
        return cell['amount']

    def get_cell_slippage_rate(self, cell_id):
        cell = self.cells[cell_id]
        return cell['slippage_rate']

    def get_cell_commission(self, cell_id):
        cell = self.cells[cell_id]
        return cell['commission_rate'], cell['commission_prec']

    def get_all_cell_ids(self):
        return self.cells.keys()

    def new_limit_bill(self, cell_id, side, symbol, multiplier, price, qty, rmk='', oc=None):
        trader = self.get_cell_trader(cell_id)
        typ = common.ORDER_TYPE_LIMIT
        ret = trader.new_order(side, typ, symbol, price, qty, oc=oc)
        log.info('-----> new_limit_bill ret type: {}  {}'.format(type(ret), ret))
        if not ret:
            return None

        if type(ret) in [str, int] :
            order_ids = ret
        elif type(ret) is list:
            if type(ret[0]) in [str, int]:
                order_ids = ret
            else:
                order_ids = [order[trader.Order_Id_Key] for order in ret]
        else:
            order = ret
            order_ids = order[trader.Order_Id_Key]
            ret = [ret]

        if not order_ids:
            return None
        bill = {
            "create_time": datetime.datetime.now(),#time.time(),
            common.BILL_KEY_CELL_ID: cell_id,
            common.BILL_SYMBOL_KEY: symbol,
            common.BILL_MULTIPLIER_KEY: multiplier,
            common.BILL_STATUS_KEY: common.BILL_STATUS_OPEN,
            common.SIDE_KEY: side,
            common.ORDER_TYPE_KEY: typ,
            "price": price,
            "qty": qty,
            common.BILL_ORDER_ID_KEY: order_ids,
            "rmk": rmk,
        }
        if type(order_ids) is list:
            bill[common.BILL_OPEN_ORDER_IDS_KEY] = order_ids
        if oc:
            bill['oc'] = oc
        _id = self.trade_db.insert_one(self.bills_collection_name, bill)
        return ret

    def cancel_bills(self, bills):
        for bill in bills:
            cell_id = bill[common.BILL_KEY_CELL_ID]
            trader = self.get_cell_trader(cell_id)

            symbol  = bill[common.BILL_SYMBOL_KEY]
            orderIds = get_orderids_by_bill(bill)
            trader.cancel_orders_byId(symbol, orderIds)

    def get_bills(self, cell_id, bill_status=None):
        f = {common.BILL_KEY_CELL_ID: cell_id}
        if bill_status:
            f[common.BILL_STATUS_KEY] = bill_status
        bills = self.trade_db.find(self.bills_collection_name, f)
        return bills

    def get_open_bills(self, cell_id):
        return self.get_bills(cell_id, common.BILL_STATUS_OPEN)

    def get_close_bills(self, cell_id):
        return self.get_bills(cell_id, common.BILL_STATUS_CLOSE)

    def get_all_bills(self, cell_id):
        return self.get_bills(cell_id)

    def get_bill(self, order_id):
        bills = self.trade_db.find(self.bills_collection_name, {
            "order_id": order_id})
        #pprint(bills)
        if len(bills) > 1:
            log.debug('{}'.format(bills))
        elif len(bills) == 1:
            return bills[0]
        else:
            return None

    def get_orders_from_db(self, trader, orders_collection_name, order_ids):
        query = {
            trader.Order_Id_Key: {"$in": order_ids},
        }
        orders = self.trade_db.find(orders_collection_name, query)
        return orders

    def _get_trades_from_db(self, trader, trades_collection_name, order_ids):
        query = {
            trader.Order_Id_Key: {"$in": order_ids},
        }
        trades = self.trade_db.find(trades_collection_name, query)
        return trades

    def _get_commission_from_trades(self, cell_id, multiplier, trades):
        commission = {}
        if len(trades) == 0:
            return commission

        trader = self.get_cell_trader(cell_id)
        commission_rate, commission_prec = self.get_cell_commission(cell_id)

        if hasattr(trader, 'Trade_Key_CommissionQty'):
            commission = collect_commission_from_trades(trader, trades)
        elif commission_rate:
            commission = calc_commission_by_trades(multiplier, trader, trades,
                commission_rate, commission_prec)
        return commission


    def get_bill_commission(self, bill):
        cell_id = bill[common.BILL_KEY_CELL_ID]
        trader = self.get_cell_trader(cell_id)
        trades_collection_name = self.get_cell_trades_collection_name(cell_id)

        order_ids = get_orderids_by_bill(bill)
        trades = self._get_trades_from_db(trader, trades_collection_name, order_ids)
        multiplier = bill[common.BILL_MULTIPLIER_KEY]
        commission = self._get_commission_from_trades(cell_id, multiplier, trades)
        return commission


    def get_order_commission(self, cell_id, multiplier, order):
        trader = self.get_cell_trader(cell_id)
        trades_collection_name = self.get_cell_trades_collection_name(cell_id)

        order_id = order[trader.Order_Id_Key]
        trades = self._get_trades_from_db(trader, trades_collection_name, [order_id])
        commission = self._get_commission_from_trades(cell_id, multiplier, trades)
        return commission


    def get_bill_deal_info(self, bill):
        cell_id = bill[common.BILL_KEY_CELL_ID]
        trader = self.get_cell_trader(cell_id)
        orders_collection_name = self.get_cell_orders_collection_name(cell_id)

        total_deal_qty = 0
        total_quote_qty = 0
        order_ids = get_orderids_by_bill(bill)
        orders = self.get_orders_from_db(trader, orders_collection_name, order_ids)
        if len(orders) == 0:
            log.info('order not find! ids: {}'.format(order_ids))
            return 0, 0

        for order in orders:
            deal_qty = trader.get_order_exec_qty(order)
            if hasattr(trader, 'get_order_deal_price'):
                deal_price = trader.get_order_deal_price(order)
            else:
                pass

            total_deal_qty += deal_qty
            total_quote_qty += deal_qty * deal_price

        if total_deal_qty == 0:
            return 0, 0

        return total_deal_qty, (total_quote_qty / total_deal_qty)


    def _init_position(self, cell_id):
        trader = self.get_cell_trader(cell_id)
        orders_collection_name = self.get_cell_orders_collection_name(cell_id)

        pst = init_position()
        pst[POSITION_ORDER_COUNT] = 0
        close_bills = self.get_close_bills(cell_id)
        order_ids = get_orderids_by_bills(close_bills)
        log.info('_init_position  order len: {},  bill len: {}'.format(len(order_ids), len(close_bills)))
        for bill in close_bills:
            symbol = bill[common.BILL_SYMBOL_KEY]
            multiplier = self.get_multiplier_by_bill(bill)
            order_ids = get_orderids_by_bill(bill)
            orders = self.get_orders_from_db(trader, orders_collection_name, order_ids)
            if not orders:
                log.critical("_init_position: not find order! ids: {}".format(order_ids))
                continue
            for order in orders:
                commission = self.get_order_commission(cell_id, multiplier, order)
                update_position_by_order(symbol, multiplier, trader, pst, order, commission)
        return pst


    def get_position(self, cell_id):
        self.handle_open_bills(cell_id)
        return self.position[cell_id]


    def close_bill_to_db(self, bill, order, trades):
        cell_id = bill[common.BILL_KEY_CELL_ID]
        trader = self.get_cell_trader(cell_id)
        orders_collection_name = self.get_cell_orders_collection_name(cell_id)
        trades_collection_name = self.get_cell_trades_collection_name(cell_id)

        if common.BILL_OPEN_ORDER_IDS_KEY in bill:
            order_id = order[trader.Order_Id_Key]
            bill_open_order_ids = bill[common.BILL_OPEN_ORDER_IDS_KEY]
            if not order_id in bill_open_order_ids:
               return

        if len(trades) > 0:
            self.trade_db.insert_many(trades_collection_name, trades)
        self.trade_db.insert_one(orders_collection_name, order)

        symbol = bill[common.BILL_SYMBOL_KEY]
        multiplier = self.get_multiplier_by_bill(bill)
        commission = self._get_commission_from_trades(cell_id, multiplier, trades)
        update_position_by_order(symbol, multiplier, trader,
                                 self.position[cell_id], order, commission)

        if common.BILL_OPEN_ORDER_IDS_KEY in bill:
            bill_open_order_ids.remove(order_id)
            self.trade_db.update_one(self.bills_collection_name, bill['_id'],
                {common.BILL_OPEN_ORDER_IDS_KEY: bill_open_order_ids})
            if len(bill_open_order_ids) > 0:
                return

        self.trade_db.update_one(self.bills_collection_name, bill['_id'],
            {common.BILL_STATUS_KEY: common.BILL_STATUS_CLOSE})


    def sync_bill(self, trader, order, trades):
        if not trader.check_status_is_close(order):
            return
        order_id = order[trader.Order_Id_Key]
        bill = self.get_bill(order_id)
        if not bill:
            return
        self.close_bill_to_db(bill, order, trades)
        cell_id = bill[common.BILL_KEY_CELL_ID]
        log.info('sync_bill => {}'.format(self.position[cell_id]))


    def handle_open_bills(self, cell_id):
        if not cell_id in self.position:
            self.position[cell_id] = self._init_position(cell_id)

        open_bills = self.get_open_bills(cell_id)
        if not open_bills:
            return [], []

        trader = self.get_cell_trader(cell_id)

        orders = None
        trades = None
        buy_open_bills = []
        sell_open_bills = []
        for open_bill in open_bills:
            symbol = open_bill[common.BILL_SYMBOL_KEY]
            open_orders = trader.get_open_orders(symbol)
            open_order_ids = [o[trader.Order_Id_Key] for o in open_orders]

            order_ids = get_orderids_by_bill(open_bill)
            for order_id in order_ids:
                log.info('%s %s %s %s'%(order_ids, order_id, open_order_ids, order_id in open_order_ids))
                if order_id in open_order_ids:
                    continue

                if not orders:
                    orders = trader.get_orders(symbol)
                order = trader.search_order(order_id, orders)
                if not order:
                    order = trader.get_order(symbol, order_id)
                if not order:
                    log.debug('    not order, bill: {}'.format(open_bill))
                    self.trade_db.update_one(self.bills_collection_name, open_bill['_id'], {
                        common.BILL_STATUS_KEY: common.BILL_STATUS_CLOSE,
                    })
                    continue

                if not trader.check_status_is_close(order):
                    log.debug('    order is openning!\n    {}'.format(order))
                    continue

                r_trades = []
                if trader.get_order_exec_qty(order) > 0:
                    if not trades:
                        trades = trader.my_trades(symbol)
                    r_trades = trader.search_trades(order_id, trades)
                self.close_bill_to_db(open_bill, order, r_trades)

            if open_bill[common.SIDE_KEY] == common.SIDE_BUY:
                buy_open_bills.append(open_bill)
            else:
                sell_open_bills.append(open_bill)
            log.info('handle_open_bills => {}'.format(self.position[cell_id]))
        return buy_open_bills, sell_open_bills

