import common
from . import *


class SimulationQuoteeEngine(QuoteEngine):
    def __init__(self, quoter):
        super().__init__(quoter)

    def ticker_price(self, symbol):
        from analyze import load_from_csv
        import common.kline as kl
        quoter = self.quoter
        interval = self.intervals[0]
        csv_name = f'{symbol}_{interval}.csv'
        df = load_from_csv(csv_name)
        df['ot'] = df[quoter.kline_key_open_time].apply(quoter.get_time_from_data_ts)
        interval_timedelta = kl.get_interval_timedelta(interval)
        #print(df)
        #print(csv_name, self.now_time)
        df = df[self.now_time-interval_timedelta == df['ot']]
        #print(df)
        price = df.iloc[-1][quoter.kline_key_close]
        return price

