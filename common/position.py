PST_TYPE_BASE_QTY = 0
PST_TYPE_QUOTE_QTY = 1

PST_QTY = "base_qty"
PST_QUOTE_QTY = "quote_qty"
PST_DEAL_QTY = "deal_base_qty"
PST_DEAL_QUOTE_QTY = "deal_quote_qty"


def init_position():
    return {
        "order_count": {},
        "base_qty": 0,
        "quote_qty": 0,
        "deal_base_qty": 0,
        "deal_quote_qty": 0
    }

def update_position_by_order(trader, symbol, position, order):
    pst = position
    order_status = order[trader.ORDER_STATUS_KEY]
    if order_status in pst['order_count']:
        pst['order_count'][order_status] += 1
    else:
        pst['order_count'][order_status] = 1

    executed_qty = float(order[trader.Order_Key_ExecutedQty])
    if executed_qty == 0:
        return
    value = float(order[trader.Order_Key_CummulativeQuoteQty])
    if trader.order_is_buy(order):
        pst['base_qty'] += executed_qty
        pst['quote_qty'] -= value
    else:
        pst['base_qty'] -= executed_qty
        pst['quote_qty'] += value
    pst['deal_base_qty'] += executed_qty
    pst['deal_quote_qty'] += value
    return
