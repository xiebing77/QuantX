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


def update_bill_position(pst, bill):
    new_pst = pst.copy()
    if pst[POSITION_BASE_QTY_KEY]==0:
        new_pst[POSITION_HISTORY_QUOTE_QTY_KEY] += pst[POSITION_QUOTE_QTY_KEY]

    bill_base_qty = bill['qty']
    bill_quote_qty = bill['qty'] * bill['price']

    if new_pst[POSITION_BASE_QTY_KEY]==0:
        new_pst[POSITION_QUOTE_QTY_KEY] = 0

    if bill[common.SIDE_KEY] == common.SIDE_BUY:
        new_pst[POSITION_BASE_QTY_KEY] += bill_base_qty
        new_pst[POSITION_QUOTE_QTY_KEY] -= bill_quote_qty
    else:
        new_pst[POSITION_BASE_QTY_KEY] -= bill_base_qty
        new_pst[POSITION_QUOTE_QTY_KEY] += bill_quote_qty

    new_pst[POSITION_DEAL_BASE_QTY_KEY] += bill_base_qty
    new_pst[POSITION_DEAL_QUOTE_QTY_KEY] += bill_quote_qty

    bill[POSITION_KEY] = new_pst
    return


def init_positon():
    return {
        POSITION_BASE_QTY_KEY: 0,
        POSITION_QUOTE_QTY_KEY: 0,
        POSITION_HISTORY_QUOTE_QTY_KEY: 0,
        POSITION_DEAL_BASE_QTY_KEY: 0,
        POSITION_DEAL_QUOTE_QTY_KEY: 0
    }


def calc_position(bills):
    if len(bills) == 0:
        return init_positon()

    if POSITION_KEY in bills[-1]:
        pst = bills[-1][POSITION_KEY]
        return pst

    if len(bills)>=2 and POSITION_KEY in bills[-2]:
        update_bill_position(bills[-2][POSITION_KEY],bills[-1])
        pst = bills[-1][POSITION_KEY]
        return pst

    pst = init_positon()
    for bill in bills:
        update_bill_position(pst,bill)
        pst = bill[POSITION_KEY]
    return pst

