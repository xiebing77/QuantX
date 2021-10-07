#!/usr/bin/python
""""""
import common

class Account():

    def new_order(self, side, type, symbol, price, amount, client_order_id=None):
        #log.info('create order: pair(%s), side(%s), type(%s), price(%f), amount(%f)' % (exchange_symbol, binance_side, binance_type, price, amount))
        ex_side = self.ex_sides[side]
        if hasattr(self, '_before_create_order'):
            target_coin, base_coin = common.get_symbol_coins(symbol)
            self._before_create_order(ex_side, target_coin, base_coin,
                price, amount, client_order_id)
        return self._new_order(self.ex_order_types[type], ex_side,
            self._trans_symbol(symbol), price, amount, client_order_id)

    def cancel_order(self, symbol, order_id):
        self._cancel_order(self._trans_symbol(symbol), orderId=order_id)

    def cancel_all_open_orders(self, symbol):
        self._cancel_all_open_orders(self._trans_symbol(symbol))

    def cancel_orders(self, symbol, order_ids):
        for order_id in order_ids:
            self.cancel_order(symbol, order_id)

    def get_order(self, symbol):
        return self._get_orders(self._trans_symbol(symbol))

    def get_open_orders(self, symbol):
        return self._get_open_orders(self._trans_symbol(symbol))

    def get_open_order_ids(self, symbol):
        orders = self.get_open_orders(symbol)
        return [order[self.Order_Id_Key] for order in orders]

    def order_status_is_close(self, symbol, order_id):
        return self._order_status_is_close(self._trans_symbol(symbol))

    def my_trades(self, symbol):
        return self._my_trades(self._trans_symbol(symbol))
