import common

POSITION_KEY = 'position'
POSITION_BASE_QTY_KEY = 'base_qty'
POSITION_QUOTE_QTY_KEY = 'quote_qty'
POSITION_HISTORY_QUOTE_QTY_KEY = 'history_quote_qty'
POSITION_DEAL_BASE_QTY_KEY = 'deal_base_qty'
POSITION_DEAL_QUOTE_QTY_KEY = 'deal_quote_qty'
POSITION_KEY_COMMISSION = 'commission'

POSITION_KEY_SYMBOL     = 'symbol'
POSITION_KEY_MULTIPLIER = 'multiplier'


def get_pst_info(pst):
    return '%16s  %2d  %15.8f  %15.8f  %15.8f  %20.8f  %20.8f' % (
        pst[POSITION_KEY_SYMBOL],
        pst[POSITION_KEY_MULTIPLIER],
        pst[POSITION_BASE_QTY_KEY],
        pst[POSITION_QUOTE_QTY_KEY],
        pst[POSITION_HISTORY_QUOTE_QTY_KEY],
        pst[POSITION_DEAL_BASE_QTY_KEY],
        pst[POSITION_DEAL_QUOTE_QTY_KEY])

def get_pst_symbol(pst):
    return pst[POSITION_KEY_SYMBOL]

def get_pst_multiplier(pst):
    return pst[POSITION_KEY_MULTIPLIER]

def get_pst_qty(pst):
    return pst[POSITION_BASE_QTY_KEY]

def get_pst_quote_qty(pst):
    return pst[POSITION_QUOTE_QTY_KEY]

def get_pst_commission(pst):
    return pst[POSITION_KEY_COMMISSION]

def get_gross_profit(pst, price):
    total_profit = pst[POSITION_HISTORY_QUOTE_QTY_KEY]
    if pst[POSITION_BASE_QTY_KEY] == 0:
        float_profit = 0
        total_profit += pst[POSITION_QUOTE_QTY_KEY]
    else:
        float_profit = price * pst[POSITION_KEY_MULTIPLIER] * pst[POSITION_BASE_QTY_KEY] + pst[POSITION_QUOTE_QTY_KEY]
        total_profit += float_profit
    return float_profit, total_profit


def calc_commission(pst, commission_rate):
    return pst[POSITION_DEAL_QUOTE_QTY_KEY] * commission_rate


def get_add_value(pst):
    add_value = pst[POSITION_HISTORY_QUOTE_QTY_KEY]
    if pst[POSITION_BASE_QTY_KEY] == 0:
        add_value += pst[POSITION_QUOTE_QTY_KEY]
    return add_value


def get_win_loss(bills, value=None):
    wins = []
    losses = []
    for b in bills:
        pst = b['position']
        if pst[POSITION_BASE_QTY_KEY] == 0:
            p = pst[POSITION_QUOTE_QTY_KEY]
            if value:
                p /= value
            if p > 0:
                #win
                wins.append(p)
            else:
                #loss
                losses.append(p)
    return wins, losses, []


def init_position():
    return {
        POSITION_KEY_SYMBOL: '',
        POSITION_KEY_MULTIPLIER: 0,
        POSITION_BASE_QTY_KEY: 0,
        POSITION_QUOTE_QTY_KEY: 0,
        POSITION_HISTORY_QUOTE_QTY_KEY: 0,
        POSITION_DEAL_BASE_QTY_KEY: 0,
        POSITION_DEAL_QUOTE_QTY_KEY: 0,
        POSITION_KEY_COMMISSION: {}
    }


def update_position(pst, symbol, multiplier, side, base_qty, quote_qty, commission):
    if pst[POSITION_BASE_QTY_KEY] == 0:
        pst[POSITION_KEY_SYMBOL]     = symbol
        pst[POSITION_KEY_MULTIPLIER] = multiplier
        pst[POSITION_HISTORY_QUOTE_QTY_KEY] += pst[POSITION_QUOTE_QTY_KEY]
        pst[POSITION_QUOTE_QTY_KEY] = 0
    else:
        if symbol != pst[POSITION_KEY_SYMBOL]:
            return None

    if side == common.SIDE_BUY:
        pst[POSITION_BASE_QTY_KEY] += base_qty
        pst[POSITION_QUOTE_QTY_KEY] -= quote_qty
    else:
        pst[POSITION_BASE_QTY_KEY] -= base_qty
        pst[POSITION_QUOTE_QTY_KEY] += quote_qty

    pst[POSITION_DEAL_BASE_QTY_KEY] += base_qty
    pst[POSITION_DEAL_QUOTE_QTY_KEY] += quote_qty

    if not pst[POSITION_KEY_COMMISSION]:
        pst[POSITION_KEY_COMMISSION] = commission
    else:
        for coin, qty in commission.items():
            if coin not in pst[POSITION_KEY_COMMISSION]:
                pst[POSITION_KEY_COMMISSION][coin] = qty
            else:
                pst[POSITION_KEY_COMMISSION][coin] += qty
    return pst


def update_pst_commission(pst, commission):
    pst_commission = pst[POSITION_KEY_COMMISSION]
    for coin_name, n in commission.items():
        if coin_name in pst_commission:
            pst_commission[coin_name] += n
        else:
            pst_commission[coin_name] = n


from common.contract import get_contractes, get_contract, CONTRACT_CODE, CONTRACT_MAIN, CONTRACT_MULTIPLIER
class TradeEngine(object):
    def __init__(self):
        self._multiplieres = {}
        for contract in get_contractes():
            code = contract[CONTRACT_CODE]
            multiplier = contract[CONTRACT_MULTIPLIER]
            symbol = '{}{}'.format(code, int(contract[CONTRACT_MAIN]))
            #self._multiplieres[code]   = multiplier
            self._multiplieres[symbol] = int(multiplier)
        #print(self._multiplieres)

    def get_symbol_by_code(self, code):
        contract = get_contract(code)
        return '{}{}'.format(code, int(contract[CONTRACT_MAIN]))

    def get_multiplier_by_symbol(self, symbol):
        if symbol in self._multiplieres:
            return self._multiplieres[symbol]
        return 1

    def get_multiplier_by_bill(self, bill):
        if common.BILL_MULTIPLIER_KEY in bill:
            return bill[common.BILL_MULTIPLIER_KEY]
        return self.get_multiplier_by_symbol(bill[common.BILL_SYMBOL_KEY])
