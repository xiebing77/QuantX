import common

POSITION_KEY = 'position'
POSITION_BASE_QTY_KEY = 'base_qty'
POSITION_QUOTE_QTY_KEY = 'quote_qty'
POSITION_HISTORY_QUOTE_QTY_KEY = 'history_quote_qty'
POSITION_DEAL_BASE_QTY_KEY = 'deal_base_qty'
POSITION_DEAL_QUOTE_QTY_KEY = 'deal_quote_qty'


def get_pst_info(pst):
    return '%15.8f  %15.8f  %15.8f  %20.8f  %20.8f' % (
        pst[POSITION_BASE_QTY_KEY],
        pst[POSITION_QUOTE_QTY_KEY],
        pst[POSITION_HISTORY_QUOTE_QTY_KEY],
        pst[POSITION_DEAL_BASE_QTY_KEY],
        pst[POSITION_DEAL_QUOTE_QTY_KEY])

def get_pst_qty(pst):
    return pst[POSITION_BASE_QTY_KEY]


def get_gross_profit(pst, price):
    if pst[POSITION_BASE_QTY_KEY] == 0:
        profit = pst[POSITION_QUOTE_QTY_KEY]
    else:
        profit = price * pst[POSITION_BASE_QTY_KEY] + pst[POSITION_QUOTE_QTY_KEY]
    return profit, pst[POSITION_HISTORY_QUOTE_QTY_KEY]


def calc_commission(pst, commission_rate):
    return pst[POSITION_DEAL_QUOTE_QTY_KEY] * commission_rate


def get_total_profit(pst, price, commission_rate):
    profit, hist_profit = get_gross_profit(pst, price)
    total_profit = profit + hist_profit - calc_commission(pst, commission_rate)
    return total_profit


def get_add_value(pst):
    add_value = pst[POSITION_HISTORY_QUOTE_QTY_KEY]
    if pst[POSITION_BASE_QTY_KEY] == 0:
        add_value += pst[POSITION_QUOTE_QTY_KEY]
    return add_value


def get_win_loss(bills, value):
    wins = []
    losses = []
    for b in bills:
        pst = b['position']
        if pst[POSITION_BASE_QTY_KEY] == 0:
            profit_rate = pst[POSITION_QUOTE_QTY_KEY] / value
            if profit_rate > 0:
                #win
                wins.append(profit_rate)
            else:
                #loss
                losses.append(profit_rate)
    return wins, losses


def init_position():
    return {
        POSITION_BASE_QTY_KEY: 0,
        POSITION_QUOTE_QTY_KEY: 0,
        POSITION_HISTORY_QUOTE_QTY_KEY: 0,
        POSITION_DEAL_BASE_QTY_KEY: 0,
        POSITION_DEAL_QUOTE_QTY_KEY: 0
    }


def get_limit_price(side, price, slippage_rate):
    if side == common.SIDE_BUY:
        limit_price = price * (1+slippage_rate)
    else:
        limit_price = price * (1-slippage_rate)
    return limit_price


class TradeEngine(object):
    def __init__(self):
        pass

