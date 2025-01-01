import common
from common import SIDE_KEY, SIDE_BUY, SIDE_SELL, OC_OPEN, OC_CLOSE

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


def init_retrace():
    return {
        "max_total_profit": 0,
        "retraces": [0]
    }

def calc_retrace(r, total_profit):
    if total_profit < r['max_total_profit']:
        retrace = total_profit - r['max_total_profit']
        if retrace < r['retraces'][-1]:
            r['retraces'][-1] = retrace
        return retrace
    elif total_profit > r['max_total_profit']:
        r['max_total_profit'] = total_profit
        if r['retraces'][-1] < 0:
            r['retraces'].append(0)
        return 0

def get_r_list(r):
    return r['retraces']

def get_rts(r, value):
    if value:
        rr = [rt/value for rt in get_r_list(r)]
    else:
        rr = get_r_list(r)
    return rr

def get_win_loss(bills, value=None):
    r = init_retrace()
    total_profit = 0

    wins = []
    losses = []
    for b in bills:
        pst = b['position']
        if pst[POSITION_BASE_QTY_KEY] == 0:
            p = pst[POSITION_QUOTE_QTY_KEY]

            total_profit += p
            calc_retrace(r, total_profit)

            if value:
                p /= value
            if p > 0:
                #win
                wins.append(p)
            else:
                #loss
                losses.append(p)
    return wins, losses, get_rts(r, value)


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


def stat_commission(total_commission, commission):
    for coin_name, n in commission.items():
        if coin_name in total_commission:
            total_commission[coin_name] += n
        else:
            total_commission[coin_name] = n

def round_commission(commission):
    for coin in commission:
        commission[coin] = round(commission[coin], 8)
    return commission


#from common.contract import get_contractes, get_contract, CONTRACT_CODE, CONTRACT_MAIN, CONTRACT_MULTIPLIER
class TradeEngine(object):
    def __init__(self):
        self._multiplieres = {}
        '''
        for contract in get_contractes():
            code = contract[CONTRACT_CODE]
            self.update_symbol(code, contract)
        #print(self._multiplieres)

    def update_symbol(self, code, contract):
        multiplier = contract[CONTRACT_MULTIPLIER]
        symbol = '{}{}'.format(code, int(contract[CONTRACT_MAIN]))
        #self._multiplieres[code]   = multiplier
        self._multiplieres[symbol] = int(multiplier)
        return symbol
        '''

    def get_symbol_by_code(self, code):
        '''
        contract = get_contract(code)
        symbol = self.update_symbol(code, contract)
        return symbol
        '''

        from common.contract import get_contract_main
        symbol, multiplier = get_contract_main(self.now_time, code)
        self._multiplieres[symbol] = multiplier
        return symbol

    def get_multiplier_by_symbol(self, symbol):
        if symbol in self._multiplieres:
            return self._multiplieres[symbol]
        return 1

    def get_multiplier_by_bill(self, bill):
        if common.BILL_MULTIPLIER_KEY in bill:
            return bill[common.BILL_MULTIPLIER_KEY]
        return self.get_multiplier_by_symbol(bill[common.BILL_SYMBOL_KEY])


    def print_bills(self, cell_id,
                    show_rmk=True,
                    show_multiplier=True,
                    show_win_rate=True,
                    show_qp=True,
                    show_deal=True,
                    show_profit=True,
                    show_total_profit=True,
                    show_retrace=True,
                    show_commission=True,
                    show_status=True,
                    show_order=True):
        fmt_start          = '%19s  %14s  %5s  %5s'
        fmt_rmk            = '  %24s'
        fmt_multiplier     = '  %10s'
        fmt_qp             = '  %10s  %12s'
        fmt_deal           = '  %10s  %12s  %18s'
        fmt_win_rate       = '  %18s'
        fmt_profit         = '  %20s'
        fmt_total_profit   = '  %20s'
        fmt_retrace        = '  %18s'
        fmt_commission     = '  %15s  %18s'
        fmt_status         = '  %7s'
        fmt_order          = '  %12s'

        title = fmt_start % ('create_time', 'symbol', 'oc', 'side')
        if show_rmk:
            title += fmt_rmk % ('rmk')
        if show_multiplier:
            title += fmt_multiplier % (common.BILL_MULTIPLIER_KEY)
        if show_win_rate:
            title += fmt_win_rate % ('win_rate')
        if show_qp:
            title += fmt_qp % ('qty', 'price')
        if show_deal:
            title += fmt_deal % ('deal_qty', 'deal_price', 'dear_value')
        if show_profit:
            title += fmt_profit % ('profit')
        if show_total_profit:
            title += fmt_total_profit % ('total_profit')
        if show_retrace:
            title += fmt_retrace % ('retrace')
        if show_commission:
            title += fmt_commission % ('commission', 'total_commission')
        if show_status:
            title += fmt_status % ('status')
        if show_order:
            title += fmt_order % ('order_id')
        print(title)

        cell_value  = self.get_cell_value(cell_id)

        oc_count = 0
        win_count = 0
        win_count_rate = 0
        his_gross_profit = 0
        total_gross_profit = 0
        max_total_profit = 0
        total_commission = {}
        pst_qty = 0
        pst_quote_qty = 0

        bills = self.get_all_bills(cell_id)
        for b in bills:
            oc = b['oc']
            side = b['side']
            info = fmt_start % (b['create_time'], b['symbol'], oc, side)

            if show_rmk:
                info += fmt_rmk % (b['rmk'])

            m = b[common.BILL_MULTIPLIER_KEY]
            if show_multiplier:
                info += fmt_multiplier % (m)

            deal_qty, deal_price = self.get_bill_deal_info(b)
            deal_value = deal_qty * deal_price * m

            if oc == OC_OPEN:
                open_price = deal_price
                deal_value_open = deal_value
            else:
                oc_count += 1
                close_price = deal_price
                deal_value_close = deal_value
                if ((side == SIDE_SELL and close_price > open_price) or
                    (side == SIDE_BUY  and close_price < open_price)):
                    win_count += 1
                win_count_rate = win_count / oc_count
            if show_win_rate:
                info += fmt_win_rate % '{:7.2%} ({:3d}/{:3d})'.format(win_count_rate, win_count, oc_count)

            if show_qp:
                info += fmt_qp % (b['qty'], b['price'])

            if show_deal:
                info += fmt_deal % (deal_qty, deal_price, deal_value)

            if side == SIDE_BUY:
                pst_qty += deal_qty
                pst_quote_qty -= deal_value
            else:
                pst_qty -= deal_qty
                pst_quote_qty += deal_value
            if pst_qty == 0:
                gross_profit = pst_quote_qty
                if deal_value:
                    gross_profit_rate = gross_profit / deal_value_open
                else:
                    gross_profit_rate = 0
                pst_quote_qty = 0
            else:
                if deal_price:
                    gross_profit = pst_quote_qty + pst_qty * deal_price * m
                else:
                    gross_profit = 0
                gross_profit_rate = 0
            if show_profit:
                info += fmt_profit % '{} ({:3.2%})'.format(round(gross_profit, 2), gross_profit_rate) if oc==OC_CLOSE else ''

            total_gross_profit = gross_profit + his_gross_profit
            if pst_qty == 0:
                his_gross_profit += gross_profit

            if total_gross_profit > max_total_profit:
                max_total_profit = total_gross_profit
            retrace = total_gross_profit-max_total_profit

            if cell_value:
                total_profit_rate = total_gross_profit / cell_value
                retrace_rate = retrace / cell_value
            else:
                total_profit_rate = 0
                retrace_rate = 0

            if show_total_profit:
                info += fmt_total_profit % '{} ({:3.2%})'.format(round(total_gross_profit, 2), total_profit_rate) if oc==OC_CLOSE else ''

            if show_retrace:
                info += fmt_retrace % ('{} ({:3.2%})'.format(round(retrace, 2), retrace_rate) if oc==OC_CLOSE else '')

            commission = self.get_bill_commission(b)
            stat_commission(total_commission, commission)
            if show_commission:
                info += fmt_commission % (round_commission(commission), round_commission(total_commission))

            if show_status:
                info += fmt_status % (b['status'])
            if show_order:
                info += fmt_order % (b['order_id'])
            print(info)
