import asyncio
import websockets
import json
from datetime import datetime
import logging

logger = None


def trans_ts(ts):
    return datetime.fromtimestamp(int(ts)/1000)


def compare_ask(ask, update_ask):
    return update_ask <= ask

def compare_bid(bid, update_bid):
    return update_bid >= bid

def merge_level(name, levels, update_levels, compare):
    add_qty = 0
    sub_qty = 0
    index_level = 0
    for update_level in update_levels:
        search_levels = levels[index_level:]
        for level in search_levels:
            if compare(float(level[0]), float(update_level[0])):
                break
            index_level += 1

        if float(update_level[0]) == float(level[0]):
            if float(update_level[1]) == 0:
                sub_qty += float(level[1])
                levels.remove(level)
                #logger.info('remove {} {}'.format(name, level))
                continue

            diff_qty = float(update_level[1]) - float(level[1])
            #logger.info('diff   {} ({}, {:8.3f})'.format(name, level[0], round(diff_qty, 3)))
            level[1] = update_level[1]
            if diff_qty > 0:
                add_qty += diff_qty
            else:
                sub_qty += abs(diff_qty)
        else:
            new_ask = [update_level[0], update_level[1]]
            levels.insert(index_level, new_ask)
            #logger.info('new    {} {}'.format(name, new_ask))
            add_qty += float(update_level[1])
        index_level += 1

    return add_qty, sub_qty


def stat_level(levels):
    sum_qty = 0
    for level in levels:
        sum_qty += float(level[1])
    return sum_qty


def isMakingBuyer(trade):
    return trade[3] == 'sell'


def match_level_trade(levels, trades):
    qty = 0
    for level in levels:
        level_price = level[1]
        for trade in trades:
            if level_price == trade[0]:
                qty += float(trade[1])
    return qty


def stat_update_book(update_book, trades):
    update_t = trans_ts(update_book['ts'])
    making_buyer_trades = []
    making_seller_trades = []
    for trade in trades:
        trade_t = trans_ts(trade[0])
        if (update_t - trade_t).total_seconds() > 5:
            break
        if isMakingBuyer(trade):
            making_buyer_trades.append(trade)
        else:
            making_seller_trades.append(trade)

    ask_new_trade_qty = match_level_trade(update_book['asks'], making_seller_trades)
    bid_new_trade_qty = match_level_trade(update_book['bids'], making_buyer_trades)
    return ask_new_trade_qty, bid_new_trade_qty


pre_update_t = None
snapshot_info = {}
update_book_infos = []
sum_ask_new_order_qty = 0
sum_ask_cancel_order_qty = 0
sum_ask_new_trade_qty = 0
sum_bid_new_order_qty = 0
sum_bid_cancel_order_qty = 0
sum_bid_new_trade_qty = 0


def handle_book(order_book, update_book, trades):
    update_t = trans_ts(update_book['ts'])
    logger.info('update book time: {}'.format(update_t))

    ask_qty = stat_level(order_book['asks'])
    bid_qty = stat_level(order_book['bids'])

    ask_new_trade_qty, bid_new_trade_qty = stat_update_book(update_book, trades)
    ask_add_qty, ask_sub_qty = merge_level('ask', order_book['asks'], update_book['asks'], compare_ask)
    bid_add_qty, bid_sub_qty = merge_level('bid', order_book['bids'], update_book['bids'], compare_bid)

    ask_cancel_order_qty = ask_sub_qty - ask_new_trade_qty
    bid_cancel_order_qty = bid_sub_qty - bid_new_trade_qty

    if ask_add_qty + ask_sub_qty > 0:
        ask_cancel_radio = ask_cancel_order_qty / (ask_add_qty + ask_sub_qty)
    if bid_add_qty + bid_sub_qty > 0:
        bid_cancel_radio = bid_cancel_order_qty / (bid_add_qty + bid_sub_qty)

    global snapshot_info
    global sum_ask_new_order_qty
    global sum_ask_cancel_order_qty
    global sum_ask_new_trade_qty
    global sum_bid_new_order_qty
    global sum_bid_cancel_order_qty
    global sum_bid_new_trade_qty
    for info in update_book_infos[:]:
        #logger.info(info)
        if (update_t - info['time']).total_seconds() < 30:
            break

        snapshot_info = info
        sum_ask_new_order_qty -= info['ask']['new_order_qty']
        sum_ask_cancel_order_qty -= info['ask']['cancel_order_qty']
        sum_ask_new_trade_qty -= info['ask']['new_trade_qty']

        sum_bid_new_order_qty -= info['bid']['new_order_qty']
        sum_bid_cancel_order_qty -= info['bid']['cancel_order_qty']
        sum_bid_new_trade_qty -= info['bid']['new_trade_qty']
        update_book_infos.pop(0)

    snapshot_t = snapshot_info['time']
    snapshot_update_td = (update_t - snapshot_t).total_seconds()

    update_book_infos.append({
        'time': update_t,
        'ask': {
            "qty": ask_qty,
            "new_order_qty": ask_add_qty,
            "cancel_order_qty": ask_cancel_order_qty,
            "new_trade_qty": ask_new_trade_qty,
        },
        'bid': {
            "qty": bid_qty,
            "new_order_qty": bid_add_qty,
            "cancel_order_qty": bid_cancel_order_qty,
            "new_trade_qty": bid_new_trade_qty,
        }
    })
    sum_ask_new_order_qty += ask_add_qty
    sum_ask_cancel_order_qty += ask_cancel_order_qty
    sum_ask_new_trade_qty += ask_new_trade_qty
    sum_bid_new_order_qty += bid_add_qty
    sum_bid_cancel_order_qty += bid_cancel_order_qty
    sum_bid_new_trade_qty += bid_new_trade_qty
    sum_ask_cancel_radio = sum_ask_cancel_order_qty / (
        sum_ask_new_order_qty + sum_ask_cancel_order_qty + sum_ask_new_trade_qty)
    sum_bid_cancel_radio = sum_bid_cancel_order_qty / (
        sum_bid_new_order_qty + sum_bid_cancel_order_qty + sum_bid_new_trade_qty)

    global pre_update_t
    update_td = (update_t - pre_update_t).total_seconds()
    pre_update_t = update_t

    qty_prec = 3
    fmt = '{:>5} {:>8} {:12.2%} {:18.4f} {:18.4f} {:>12} {:>12}'
    logger.info('{:>5} {:>8} {:>12s} {:>18s} {:>18s} {:>12s} {:>12s}'.format(
        'qty', 'second', 'cancel radio', 'cancel order', 'new order', 'new trade', 'snapshot'))
    logger.info(fmt.format('ask', update_td,
        ask_cancel_radio,
        round(ask_cancel_order_qty, qty_prec),
        round(ask_add_qty, qty_prec),
        round(ask_new_trade_qty, qty_prec),
        round(ask_qty, qty_prec)))
    logger.info(fmt.format('bid', update_td,
        bid_cancel_radio,
        round(bid_cancel_order_qty, qty_prec),
        round(bid_add_qty, qty_prec),
        round(bid_new_trade_qty, qty_prec),
        round(bid_qty, qty_prec)))

    logger.info(fmt.format('ask', snapshot_update_td,
        sum_ask_cancel_radio,
        round(sum_ask_cancel_order_qty, qty_prec),
        round(sum_ask_new_order_qty, qty_prec),
        '',
        round(snapshot_info['ask']['qty'], qty_prec) if 'ask' in snapshot_info else '' ))
    logger.info(fmt.format('bid', snapshot_update_td,
        sum_bid_cancel_radio,
        round(sum_bid_cancel_order_qty, qty_prec),
        round(sum_bid_new_order_qty, qty_prec),
        '',
        round(snapshot_info['bid']['qty'], qty_prec) if 'bid' in snapshot_info else ''))


async def main():
    depth_url = 'wss://ws.bitget.com/spot/v1/stream'
    ws_handler = await websockets.connect(depth_url)

    symbol = 'AURORAUSDT'
    book_arg = {
        "instType": "SP",
        "channel": "books",
        "instId": symbol
    }
    trade_arg = {
        "instType": "SP",
        "channel": "trade",
        "instId": symbol
    }
    ticker_arg = {
        "instType": "SP",
        "channel": "ticker",
        "instId": symbol
    }
    rq_parm = {
        "op": "subscribe",
        "args": [book_arg, trade_arg, ticker_arg]
    }
    await ws_handler.send(json.dumps(rq_parm))

    t_prev = datetime.now()
    while True:
        response = await ws_handler.recv()
        #logger.info(response)

        if response == 'pong':
            continue
        try:
            response = json.loads(response)
        except Exception as ept:
            print(response)
            logger.critical(ept)
        if 'event' in response:
            continue

        resp_arg_channel = response['arg']['channel']
        resp_action = response['action']
        resp_data = response['data']

        if resp_arg_channel == 'books':
            if resp_action == 'snapshot':
                order_book = resp_data[0]
                global pre_update_t
                snapshot_info['time'] = pre_update_t = trans_ts(order_book['ts'])
            elif resp_action == 'update':
                for update_book in resp_data:
                    handle_book(order_book, update_book, trades)

            idxs = range(3)
            for idx in reversed(idxs):
                logger.info('ask {}: {}'.format(idx, order_book['asks'][idx]))
            for idx in idxs:
                logger.info('bid {}: {}'.format(idx, order_book['bids'][idx]))

        elif resp_arg_channel == 'trade':
            if resp_action == 'snapshot':
                trades = resp_data
                logger.info('snapshot trade len: {}'.format(len(trades)))
            elif resp_action == 'update':
                update_trades = resp_data
                trades = update_trades + trades
                logger.info('update trade len: {}'.format(len(update_trades)))
                for trade in update_trades:
                    trade_ts = datetime.fromtimestamp(int(trade[0])/1000)
                    trade_price = float(trade[1])
                    if trade_price > float(order_book['asks'][0][0]):
                        info = ' > ask 0'
                    elif trade_price < float(order_book['bids'][0][0]):
                        info = ' < bid 0'
                    else:
                        info = ''
                    logger.info('new trade {}:  {}  {}'.format(info, trade_ts, trade))

        elif resp_arg_channel == 'ticker':
            for info_ticker in resp_data:
                ts_ticker = datetime.fromtimestamp(int(info_ticker['ts'])/1000)
                logger.info('ticker time: {}'.format(ts_ticker))
                logger.info('bestAsk: {}'.format(info_ticker['bestAsk']))
                logger.info('last   : {}'.format(info_ticker['last']))
                logger.info('bestBid: {}'.format(info_ticker['bestBid']))

        t_now = datetime.now()
        if (t_now - t_prev).total_seconds() > 25:
            await ws_handler.send('ping')
            t_prev = t_now


if __name__ == '__main__':
    logger = logging.getLogger('ws ')
    logger.setLevel(logging.DEBUG)

    logfilename = 'bitget_aurora_ws_data' + ".log"
    logging.basicConfig(level=logging.NOTSET, filename=logfilename)

    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())

