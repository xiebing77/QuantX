import talib

def calc_tick_indicators(quoter, config, df, calc_all=False):
    key_xs = []

    key_high = None
    key_close = quoter.tick_key_close
    key_volume = quoter.tick_key_volume
    key_bid_size = quoter.tick_key_bid_size
    key_ask_size = quoter.tick_key_ask_size
    key_ask = quoter.tick_key_ask
    key_bid = quoter.tick_key_bid

    name = 'size.imb'
    if self.is_tick and (calc_all or name in config):
        key_x = '%s' % (name)
        df[key_x] = (df[key_bid_size]-df[key_ask_size])/(df[key_bid_size]+df[key_ask_size])/df[key_ask]-(df[key_bid])/(df[key_bid]+df[key_ask])*2
        key_xs.append(key_x)

    return key_xs
