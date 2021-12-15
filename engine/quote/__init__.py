
from db.mongodb import get_mongodb


class QuoteEngine(object):
    def __init__(self, quoter):
        self.quoter = quoter
        self._db = get_mongodb(quoter.name)
        return


class DBQuoteEngine(QuoteEngine):
    def __init__(self, quoter):
        super().__init__(quoter)
        return

    def get_original_klines(self, collection, s_time, e_time):
        print(collection, s_time, e_time, self.quoter.kline_key_open_time)
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

