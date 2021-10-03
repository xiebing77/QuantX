#!/usr/bin/python
""""""

class Trade():

    def create_order(self, side, type, symbol, price, amount, client_order_id=None):
        #log.info('create order: pair(%s), side(%s), type(%s), price(%f), amount(%f)' % (exchange_symbol, binance_side, binance_type, price, amount))
        if hasattr(self, '_before_create_order'):
            target_coin, base_coin = xq.get_symbol_coins(symbol)
            self._before_create_order(self._trans_side(side), target_coin, base_coin,
                price, amount, client_order_id)
        return self._create_order(
            self._trans_type(type), self._trans_side(side), self._trans_symbol(symbol),
            price, amount, client_order_id)

    def cancel_order(self, symbol, order_id):
        self._cancel_order(self._trans_symbol(symbol), orderId=order_id)

    def cancel_all_open_orders(self, symbol):
        self._cancel_all_open_orders(self._trans_symbol(symbol))

    def cancel_orders(self, symbol, order_ids):
        for order_id in order_ids:
            self.cancel_order(symbol, order_id)

    def get_open_orders(self, symbol):
        return self._get_open_orders(self._trans_symbol(symbol))

    def get_open_order_ids(self, symbol):
        return self._get_open_order_ids(self._trans_symbol(symbol))

    def order_status_is_close(self, symbol, order_id):
        return self._order_status_is_close(self._trans_symbol(symbol))

    def get_trades(self, symbol):
        return self._get_trades(self._trans_symbol(symbol))
