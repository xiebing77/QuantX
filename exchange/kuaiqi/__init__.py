#!/usr/bin/python
import os
import time
from datetime import datetime
import common.kline as kl
from exchange import Exchange
import common



class KuaiQi(Exchange):
    name = 'kuaiqi'
    unit = 'ms'
    min_value = 10

    tick_key_close_time = 'datetime_nano'
    tick_key_close      = 'last_price'
    tick_key_volume     = 'volume'
    tick_key_bid        = 'bid_price1'
    tick_key_bid_size   = 'bid_volume1'
    tick_key_ask        = 'ask_price1'
    tick_key_ask_size   = 'ask_volume1'

    kl_bt_accuracy = kl.KLINE_INTERVAL_1MINUTE

    kline_data_type = kl.KLINE_DATA_TYPE_LIST

    kline_key_open_time  = kl.KLINE_KEY_OPEN_TIME
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

    SIDE_BUY  = 'buy'
    SIDE_SELL = 'sell'

    Order_Id_Key = 'orderId'
    Order_Time_Key = 'cTime'

    Order_Key_Type = 'type'
    Order_Key_Side = 'side'

    Order_Key_Price = 'price'
    Order_Key_OrigQty = 'quantity'
    Order_Key_ExecutedQty = 'fillQuantity'
    Order_Key_CummulativeQuoteQty = 'fillTotalAmount'

    ORDER_STATUS_KEY = 'status'
    ORDER_STATUS_NEW = 'new'
    ORDER_STATUS_PARTIALLY_FILLED = 'partial_fill'
    ORDER_STATUS_FILLED = 'full_fill'
    ORDER_STATUS_CANCELED = 'cancelled'
    #ORDER_STATUS_PENDING_CANCEL = 'PENDING_CANCEL'
    #ORDER_STATUS_REJECTED = 'REJECTED'
    #ORDER_STATUS_EXPIRED = 'EXPIRED'

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

    Trade_Key_CommissionQty = 'fees'
    Trade_Key_CommissionAsset = 'feeCcy'
    Trade_Key_Qty = 'fillQuantity'
    Trade_Key_Price = 'fillPrice'
    Trade_Key_Value = 'fillTotalAmount'
    Trade_Key_Time = 'fillTime'


    TRADE_ORDER_ID_KEY = 'orderId'
    '''

    def __init__(self, debug=False):
        return

    '''
    def _get_coinkey(self, coin):
        return coin.upper()

    def _trans_symbol(self, symbol):
        target_coin, base_coin = common.split_symbol_coins(symbol)
        return '%s%s' % (self._get_coinkey(target_coin), self._get_coinkey(base_coin))
    '''

    def get_time_from_data_ts(self, ts):
        return datetime.fromtimestamp(int(ts) / 1000)

    def get_data_ts_from_time(self, t):
        return int(t.timestamp()) * 1000

    def get_timestamp(self):
        return int(time.time() * 1000)

    '''
    def get_time_from_trade_data(self, trade):
        ts = trade[self.Trade_Key_Time]
        return datetime.fromtimestamp(int(ts) / 1000)

    def check_status_is_close(self, order):
        #print(order)
        order_status = order[self.ORDER_STATUS_KEY]
        close_statuses = [self.ORDER_STATUS_FILLED, self.ORDER_STATUS_CANCELED]
        return order_status in close_statuses

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

