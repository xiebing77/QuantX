
from db.mongodb import get_mongodb
import setup


def stat_trades(quoter, trades):
    maker_buyer = {
        'count': 0,
        'qty': 0,
        'asset': 0
    }
    maker_seller = {
        'count': 0,
        'qty': 0,
        'asset': 0
    }
    for trade in trades:
        qty = float(trade[quoter.Trade_Key_Qty])
        asset = qty * float(trade[quoter.Trade_Key_Price])
        if quoter.isBuyerMaker(trade):
            maker_buyer['count'] += 1
            maker_buyer['qty'] += qty
            maker_buyer['asset'] += asset
        else:
            maker_seller['count'] += 1
            maker_seller['qty'] += qty
            maker_seller['asset'] += asset
    return maker_buyer, maker_seller


class QuoteEngine(object):
    def __init__(self, quoter):
        self.quoter = quoter
        self._db = get_mongodb(quoter.name)
        return

    def get_original_klines(self, collection, s_time, e_time):
        #print(collection, s_time, e_time, self.quoter.kline_key_open_time)
        """ 获取k线 """
        ks = self._db.find(
            collection,
            {
                self.quoter.kline_key_open_time: {
                    "$gte": self.quoter.get_data_ts_from_time(s_time),
                    "$lt": self.quoter.get_data_ts_from_time(e_time),
                }
            },
            {"_id":0},
        )
        return ks

