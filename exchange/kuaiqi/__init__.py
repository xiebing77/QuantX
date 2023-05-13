#!/usr/bin/python
import os
import time
from datetime import datetime
import common.kline as kl
from exchange import Exchange
import common


class Kuaiqi(Exchange):
    name = 'kuaiqi'
    unit = 'ns'
    min_value = 10

    currency = 'CNY'

    tick_key_close_time = 'datetime'
    tick_key_close      = 'last_price'
    tick_key_volume     = 'volume'

    book_key_bid        = 'bid_price1'
    book_key_bid_size   = 'bid_volume1'
    book_key_ask        = 'ask_price1'
    book_key_ask_size   = 'ask_volume1'

    kl_bt_accuracy = kl.KLINE_INTERVAL_1MINUTE

    kline_data_type = kl.KLINE_DATA_TYPE_LIST

    kline_key_open_time  = 'datetime'
    kline_key_close_time = kl.KLINE_KEY_CLOSE_TIME
    kline_key_open       = kl.KLINE_KEY_OPEN
    kline_key_close      = kl.KLINE_KEY_CLOSE
    kline_key_high       = kl.KLINE_KEY_HIGH
    kline_key_low        = kl.KLINE_KEY_LOW
    kline_key_volume     = kl.KLINE_KEY_VOLUME
    kline_key_oi         = 'close_oi' # 'open_interest'

    kline_column_names = [kline_key_open_time,
                          kline_key_open,
                          kline_key_close,
                          kline_key_high,
                          kline_key_low,
                          kline_key_volume,
                          kline_key_oi]

    '''
    kline_idx_open_time   = kl.get_kline_index(kl.KLINE_KEY_OPEN_TIME, kline_column_names)
    kline_idx_close_time  = kl.get_kline_index(kl.KLINE_KEY_CLOSE_TIME, kline_column_names)
    kline_idx_open        = kl.get_kline_index(kl.KLINE_KEY_OPEN, kline_column_names)
    kline_idx_close       = kl.get_kline_index(kl.KLINE_KEY_CLOSE, kline_column_names)
    kline_idx_high        = kl.get_kline_index(kl.KLINE_KEY_HIGH, kline_column_names)
    kline_idx_low         = kl.get_kline_index(kl.KLINE_KEY_LOW, kline_column_names)
    kline_idx_volume      = kl.get_kline_index(kl.KLINE_KEY_VOLUME, kline_column_names)
    max_count_of_single_download_kl = 1000

    BALANCE_ASSET_KEY  = 'coinName'
    BALANCE_FREE_KEY   = 'available'
    BALANCE_LOCKED_KEY = 'lock'


    '''
    OC_OPEN       = 'OPEN'
    OC_CLOSE      = 'CLOSE'
    OC_CLOSETODAY = 'CLOSETODAY'

    SIDE_BUY  = 'BUY'
    SIDE_SELL = 'SELL'
    Order_Id_Key = 'order_id'
    Order_Time_Key = 'insert_date_time'

    Order_Key_Type = 'price_type'
    Order_Key_Side = 'direction'

    Order_Key_Price = 'limit_price'
    Order_Key_OrigQty = 'volume_orign'
    Order_Key_trade_Price = 'trade_price'
    #Order_Key_ExecutedQty = 'fillQuantity'
    #Order_Key_CummulativeQuoteQty = 'fillTotalAmount'

    ORDER_STATUS_KEY = 'status'
    ORDER_STATUS_NEW = 'ALIVE'
    ORDER_STATUS_FILLED = 'FINISHED'

    '''
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
        #kl.KLINE_INTERVAL_8HOUR: '8h',
        kl.KLINE_INTERVAL_12HOUR: '12h',
        kl.KLINE_INTERVAL_1DAY: '1d',
        #kl.KLINE_INTERVAL_3DAY: '3d',
        kl.KLINE_INTERVAL_1WEEK: '1w',
        kl.KLINE_INTERVAL_1MONTH: '1M',
    }

    ex_order_types = {
        common.ORDER_TYPE_LIMIT: 'limit',
        common.ORDER_TYPE_MARKET: 'market',
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
    '''

    #Trade_Key_CommissionQty = 'commission'
    #Trade_Key_CommissionAsset = 'feeCcy'
    Trade_Key_Qty = 'volume'
    Trade_Key_Price = 'price'
    Trade_Key_Time = 'trade_date_time'


    TRADE_ORDER_ID_KEY = 'order_id'

    def __init__(self, debug=False):
        return

    def _trans_symbol(self, symbol):
        return symbol

    _unit = 1e9
    @staticmethod
    def get_time_from_data_ts(ts):
        return datetime.fromtimestamp(int(ts) / Kuaiqi._unit)

    def get_data_ts_from_time(self, t):
        return int(t.timestamp() * Kuaiqi._unit)

    def get_timestamp(self):
        return int(time.time() * Kuaiqi._unit)

    def get_time_from_trade_data(self, trade):
        ts = trade[self.Trade_Key_Time]
        return datetime.fromtimestamp(int(ts) / Kuaiqi._unit)

    def get_order_exec_qty(self, order):
        return order[self.Order_Key_OrigQty] - order['volume_left']

    def get_order_exec_quote_qty(self, order):
        return self.get_order_exec_qty(order) * order[self.Order_Key_trade_Price]

    def get_order_deal_price(self, order):
        return order[self.Order_Key_trade_Price]

    def check_status_is_close(self, order):
        order_status = order[self.ORDER_STATUS_KEY]
        close_statuses = [self.ORDER_STATUS_FILLED]
        if order_status not in close_statuses:
            return False
        if self.get_order_exec_qty(order) > 0:
            if not order[self.Order_Key_trade_Price]:
                return False
        return True
    '''

    def _order_status_is_close(self, exchange_symbol, order_id):
        order = self._get_order(exchange_symbol, order_id)
        return self.check_status_is_close(order)

    def isBuyerMaker(self, trade):
        return not trade['side'] == self.SIDE_BUY

    def mytrade_is_buyer(self, mytrade):
        return mytrade['side'] == self.SIDE_BUY

    def mytrade_check_symbol(self, symbol, mytrade):
        return mytrade['symbol'] == self._trans_symbol(symbol)
    '''

