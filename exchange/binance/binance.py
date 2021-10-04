#!/usr/bin/python
import os
import time
from datetime import datetime
import kline as kl
from exchange.exchange import Exchange
import common, order


api_key = os.environ.get('BINANCE_API_KEY')
secret_key = os.environ.get('BINANCE_SECRET_KEY')


class Binance(Exchange):
    name = 'binance'
    min_value = 10
    kl_bt_accuracy = kl.KLINE_INTERVAL_1MINUTE

    kline_data_type = kl.KLINE_DATA_TYPE_LIST

    kline_key_open_time  = kl.KLINE_KEY_OPEN_TIME
    kline_key_close_time = kl.KLINE_KEY_CLOSE_TIME
    kline_key_open       = kl.KLINE_KEY_OPEN
    kline_key_close      = kl.KLINE_KEY_CLOSE
    kline_key_high       = kl.KLINE_KEY_HIGH
    kline_key_low        = kl.KLINE_KEY_LOW
    kline_key_volume     = kl.KLINE_KEY_VOLUME

    kline_column_names = [kline_key_open_time, kline_key_open, kline_key_high, kline_key_low,
            kline_key_close, kline_key_volume, kline_key_close_time,
            'quote_asset_volume','number_of_trades','taker_buy_base_asset_volume','taker_buy_quote_asset_volume','ignore']

    kline_idx_open_time   = kl.get_kline_index(kl.KLINE_KEY_OPEN_TIME, kline_column_names)
    kline_idx_close_time  = kl.get_kline_index(kl.KLINE_KEY_CLOSE_TIME, kline_column_names)
    kline_idx_open        = kl.get_kline_index(kl.KLINE_KEY_OPEN, kline_column_names)
    kline_idx_close       = kl.get_kline_index(kl.KLINE_KEY_CLOSE, kline_column_names)
    kline_idx_high        = kl.get_kline_index(kl.KLINE_KEY_HIGH, kline_column_names)
    kline_idx_low         = kl.get_kline_index(kl.KLINE_KEY_LOW, kline_column_names)
    kline_idx_volume      = kl.get_kline_index(kl.KLINE_KEY_VOLUME, kline_column_names)
    max_count_of_single_download_kl = 1000

    ORDER_STATUS_NEW = 'NEW'
    ORDER_STATUS_PARTIALLY_FILLED = 'PARTIALLY_FILLED'
    ORDER_STATUS_FILLED = 'FILLED'
    ORDER_STATUS_CANCELED = 'CANCELED'
    ORDER_STATUS_PENDING_CANCEL = 'PENDING_CANCEL'
    ORDER_STATUS_REJECTED = 'REJECTED'
    ORDER_STATUS_EXPIRED = 'EXPIRED'

    ex_intervals = {
        kl.KLINE_INTERVAL_1MINUTE: '1m',
        kl.KLINE_INTERVAL_3MINUTE: '3m',
        kl.KLINE_INTERVAL_5MINUTE: '5m',
        kl.KLINE_INTERVAL_15MINUTE: '15m',
        kl.KLINE_INTERVAL_30MINUTE: '30m',
        kl.KLINE_INTERVAL_1HOUR: '1h',
        kl.KLINE_INTERVAL_2HOUR: '2h',
        kl.KLINE_INTERVAL_4HOUR: '4h',
        kl.KLINE_INTERVAL_6HOUR: '6h',
        kl.KLINE_INTERVAL_8HOUR: '8h',
        kl.KLINE_INTERVAL_12HOUR: '12h',
        kl.KLINE_INTERVAL_1DAY: '1d',
        kl.KLINE_INTERVAL_3DAY: '3d',
        kl.KLINE_INTERVAL_1WEEK: '1w',
        kl.KLINE_INTERVAL_1MONTH: '1M',
    }

    ex_sides = {
        common.SIDE_BUY: 'BUY',
        common.SIDE_SELL: 'SELL',
    }

    ex_order_types = {
        order.ORDER_TYPE_LIMIT: 'LIMIT',
        order.ORDER_TYPE_MARKET: 'MARKET',
        #ORDER_TYPE_STOP_LOSS = 'STOP_LOSS'
        #ORDER_TYPE_STOP_LOSS_LIMIT = 'STOP_LOSS_LIMIT'
        #ORDER_TYPE_TAKE_PROFIT = 'TAKE_PROFIT'
        #ORDER_TYPE_TAKE_PROFIT_LIMIT = 'TAKE_PROFIT_LIMIT'
        #ORDER_TYPE_LIMIT_MAKER = 'LIMIT_MAKER'
    }

    TIME_IN_FORCE_GTC = 'GTC'  # Good till cancelled
    TIME_IN_FORCE_IOC = 'IOC'  # Immediate or cancel
    TIME_IN_FORCE_FOK = 'FOK'  # Fill or kill

    ORDER_RESP_TYPE_ACK = 'ACK'
    ORDER_RESP_TYPE_RESULT = 'RESULT'
    ORDER_RESP_TYPE_FULL = 'FULL'

    def _get_coinkey(self, coin):
        return coin.upper()

    def get_time_from_data_ts(self, ts):
        return datetime.fromtimestamp(ts / 1000)

    def get_data_ts_from_time(self, t):
        return int(t.timestamp()) * 1000

    def get_timestamp(self):
        return int(time.time() * 1000)

    def _get_open_order_ids(self, exchange_symbol):
        orders = self._get_open_orders(symbol)
        return [order["orderId"] for order in orders]

    def _order_status_is_close(self, exchange_symbol, order_id):
        order = self._get_order(exchange_symbol, order_id)
        if order['status'] in [ORDER_STATUS_FILLED, ORDER_STATUS_CANCELED, ORDER_STATUS_REJECTED, ORDER_STATUS_EXPIRED]:
            return True
        return False
