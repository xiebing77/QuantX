#!/usr/bin/python
""""""
import common

class Account():

    # adpation
    def new_order(self, side, type, symbol, price, qty, client_order_id=None):
        #log.info('create order: pair(%s), side(%s), type(%s), price(%f), amount(%f)' % (exchange_symbol, binance_side, binance_type, price, amount))
        ex_side = self.ex_sides[side]
        if hasattr(self, '_before_create_order'):
            target_coin, base_coin = common.get_symbol_coins(symbol)
            self._before_create_order(ex_side, target_coin, base_coin,
                price, qty, client_order_id)
        return self._new_order(ex_side=ex_side, ex_type=self.ex_order_types[type],
            ex_symbol=self._trans_symbol(symbol), price=price, qty=qty, client_order_id=client_order_id)

    def cancel_order(self, symbol, order_id):
        self._cancel_order(self._trans_symbol(symbol), order_id=order_id)

    def cancel_open_orders(self, symbol):
        self._cancel_open_orders(self._trans_symbol(symbol))

    def get_order(self, symbol, order_id):
        return self._get_order(self._trans_symbol(symbol), order_id)

    def get_orders(self, symbol, limit):
        return self._get_orders(self._trans_symbol(symbol), limit=limit)

    def get_open_orders(self, symbol):
        return self._get_open_orders(self._trans_symbol(symbol))

    def order_status_is_close(self, symbol, order_id):
        return self._order_status_is_close(self._trans_symbol(symbol))

    def my_trades(self, symbol, limit):
        return self._my_trades(self._trans_symbol(symbol), limit=limit)


    #
    def cancel_orders(self, symbol, order_ids):
        for order_id in order_ids:
            self.cancel_order(symbol, order_id)

    def get_open_order_ids(self, symbol):
        orders = self.get_open_orders(symbol)
        return [order[self.Order_Id_Key] for order in orders]

    def order_is_buy(self, order):
        return order[self.Order_Key_Side] == self.ex_sides[common.SIDE_BUY]

