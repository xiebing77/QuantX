from pprint import pprint
import common
import common.log as log

class Account():

    need_oc = False

    def trans_side(self, side):
        if side == common.SIDE_BUY:
            return self.SIDE_BUY
        return self.SIDE_SELL

    def _get_pos(self, ex_symbol, ex_side):
        pos_long_his, pos_long_today, pos_short_his, pos_short_today = self._get_ex_pst(ex_symbol)
        if ex_side == self.SIDE_SELL:
            pos_his = pos_long_his
            pos_today = pos_long_today
        else:
            pos_his = pos_short_his
            pos_today = pos_short_today
        return pos_his, pos_today

    # adpation
    def new_order(self, side, typ, symbol, price, qty, client_order_id=None, oc=None):
        log.info('create order: pair(%s), side(%s), type(%s), price(%s), qty(%s), oc(%s)' % (symbol, side, typ, price, qty, oc))
        ex_side = self.trans_side(side)
        if hasattr(self, '_before_create_order'):
            target_coin, base_coin = common.get_symbol_coins(symbol)
            self._before_create_order(ex_side, target_coin, base_coin,
                price, qty, client_order_id)

        if hasattr(self, 'ex_order_types'):
            ex_type = self.ex_order_types[typ]
        else:
            ex_type = typ

        ex_symbol = self._trans_symbol(symbol)
        params = {
            'ex_side': ex_side,
            'ex_type': ex_type,
            'ex_symbol': ex_symbol,
            'price': price,
            'qty': qty,
            'client_order_id': client_order_id
        }

        if not self.need_oc:
            return self._new_order(**params)

        if oc == common.OC_OPEN:
            params['ex_oc'] = self.OC_OPEN
            return self._new_order(**params)

        if not hasattr(self, 'OC_CLOSETODAY'):
            params['ex_oc'] = self.OC_CLOSE
            return self._new_order(**params)

        # 上期所和上期能源分平今/平昨
        pos_his, pos_toady = self._get_pos(ex_symbol, ex_side)
        if qty <= pos_his:
            params['ex_oc'] = self.OC_CLOSE
            order = self._new_order(**params)
            if not self.check_status_is_close(order):
                return order
            if not self.close_pos_his_not_enough(order):
                return order
            pos_his, pos_toady = self._get_pos(ex_symbol, ex_side)

        # 上期所和上期能源才需要平今，其它返回
        if qty <= pos_toady:
            params['ex_oc'] = self.OC_CLOSETODAY
            order = self._new_order(**params)
            if not self.check_status_is_close(order):
                return order
            if not self.close_pos_today_not_enough(order):
                return order
            pos_his, pos_toady = self._get_pos(ex_symbol, ex_side)

        for i in range(3):
            if qty > pos_his + pos_toady:
                log.critical('_new_order qty({}) > pos his({}) + today({})'.format(
                    qty, pos_his, pos_toady))
                break

            params['ex_oc'] = self.OC_CLOSE
            params['qty'] = pos_his
            order = self._new_order(**params)
            if self.check_status_is_close(order) and self.close_pos_his_not_enough(order):
                pos_his, pos_toady = self._get_pos(ex_symbol, ex_side)
                continue

            params['ex_oc'] = self.OC_CLOSETODAY
            params['qty'] = qty - pos_his
            order2 = self._new_order(**params)
            return [order, order2]

        return None


    def cancel_order(self, symbol, order_id):
        self._cancel_order(self._trans_symbol(symbol), order_id=order_id)

    def cancel_open_orders(self, symbol):
        self._cancel_open_orders(self._trans_symbol(symbol))

    def get_order(self, symbol, order_id):
        return self._get_order(self._trans_symbol(symbol), order_id)

    def get_orders(self, symbol, **kwargs):
        return self._get_orders(self._trans_symbol(symbol), **kwargs)

    def get_open_orders(self, symbol):
        return self._get_open_orders(self._trans_symbol(symbol))

    def search_order(self, order_id, orders):
        for order in orders:
            if order_id == order[self.Order_Id_Key]:
                return order
        return None

    def get_order_exec_qty(self, order):
        return float(order[self.Order_Key_ExecutedQty])

    def get_order_exec_quote_qty(self, order):
        return float(order[self.Order_Key_CummulativeQuoteQty])

    def check_orders_close_status(self, symbol, order_ids):
        orders = self.get_orders(symbol)
        close_order_ids = []
        for order in orders:
            order_id = order[self.Order_Id_Key]
            #print(order_id, order_ids, order_id in order_ids, type(order_id), type(order_ids[0]))
            if order_id in order_ids and self.check_status_is_close(order):
                close_order_ids.append(order_id)
        return close_order_ids

    def order_status_is_close(self, symbol, order_id):
        return self._order_status_is_close(self._trans_symbol(symbol), order_id)

    def my_trades(self, symbol, **kwargs):
        return self._my_trades(self._trans_symbol(symbol), **kwargs)

    def search_trades(self, order_id, trades):
        r_trades = []
        for trade in trades:
            if order_id == trade[self.TRADE_ORDER_ID_KEY]:
                r_trades.append(trade)
        return r_trades

    #
    def cancel_orders_byId(self, symbol, orderIds):
        for orderId in orderIds:
            self.cancel_order(symbol, orderId)

    def cancel_orders(self, symbol, orders):
        for order in orders:
            self.cancel_order(symbol, order[self.Order_Id_Key])

    def get_open_order_ids(self, symbol):
        orders = self.get_open_orders(symbol)
        return [order[self.Order_Id_Key] for order in orders]

    def order_is_buy(self, order):
        return order[self.Order_Key_Side] == self.SIDE_BUY


import common.kline as kl
kline_default_size = 200
class MarketData():

    def exchange_info(self, symbol: str = None, symbols: list = None):
        if symbol and symbols:
            raise ParameterArgumentError("symbol and symbols cannot be sent together.")
        if symbol:
            ex_symbol = self._trans_symbol(symbol)
        else:
            ex_symbol = None
        if symbols:
            ex_symbols = []
            for sy in symbols:
                ex_symbols.append(self._trans_symbol(symbol))
        else:
            ex_symbols = None
        return self._exchange_info(ex_symbol=ex_symbol, ex_symbols=ex_symbols)

    def get_assetPrecision(self, symbol):
        ex_symbol = self._trans_symbol(symbol)
        return self._get_assetPrecision(ex_symbol)

    def depth(self, symbol, **kwargs):
        return self._depth(self._trans_symbol(symbol), **kwargs)

    def trades(self, symbol, **kwargs):
        trades = self._trades(self._trans_symbol(symbol), **kwargs)
        return trades

    def historical_trades(self, symbol):
        trades = self._historical_trades(symbol=self._trans_symbol(symbol))
        return trades

    def agg_trades(self, symbol, **kwargs):
        trades = self._agg_trades(self._trans_symbol(symbol), **kwargs)
        return trades

    def ticker_price(self, symbol):
        return self._ticker_price(self._trans_symbol(symbol))

    def klines(self, symbol, interval, size=kline_default_size, since=None):
        return self._klines(self._trans_symbol(symbol),
            self.ex_intervals[interval], size, since)

    def klines_1day(self, symbol, size=kline_default_size, since=None):
        return self.klines(symbol, kl.KLINE_INTERVAL_1DAY, size, since)

    def klines_1min(self, symbol, size=kline_default_size, since=None):
        return self.klines(symbol, kl.KLINE_INTERVAL_1MINUTE, size, since)

    def klines_1hour(self, symbol, size=kline_default_size, since=None):
        return self.klines(symbol, kl.KLINE_INTERVAL_1HOUR, size, since)


class Exchange(MarketData, Account):
    def __init__(self):
        return

