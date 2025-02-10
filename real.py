import argparse
import time
from datetime import datetime, timedelta
import os
import common
import common.log as log
from common import SIDE_KEY, SIDE_BUY, SIDE_SELL, OC_KEY, OC_OPEN, OC_CLOSE
from common import ORDER_TYPE_LIMIT
from common.cell import cell_statuses, add_cell, delete_cell, update_cell
from common.cell import get_cells, get_cell, get_cell_info, get_cell_broker
from exchange.exchange_factory import get_exchange_names, create_exchange
from engine.quote import QuoteEngine
import engine.trade as trade
from engine.trade.exchange import ExchangeTradeEngine
from db.mongodb import get_mongodb
import setup


def real_run(args):
    cell_id = args.iid
    cell = get_cell(cell_id)
    if not cell:
        print('%s not exist' % (cell_id))
        exit(1)

    symbol = cell['symbol']
    exchange_name = cell['exchange']
    config_path = cell["config_path"]
    config = common.get_json_config(config_path)
    module_name = config["module_name"].replace("/", ".")
    class_name = config["class_name"]

    if args.print:
        log.print_switch = True
    if args.log:
        log.log_switch = True
        logfilename = cell_id + ".log"
        print(logfilename)
        log.init('real', logfilename)

    #log.info("strategy name: %s;  config: %s" % (class_name, config))
    log.info('cell_id: %s,  exchange_name: %s' % (cell_id, exchange_name))

    broker_path, broker = get_cell_broker(cell)
    exchange = create_exchange(exchange_name, broker)
    if not exchange:
        print("exchange name error!")
        exit(1)
    exchange.connect()
    exchange.ping()
    quote_engine = QuoteEngine(exchange)
    trade_engine = ExchangeTradeEngine(config)
    cfg_commission = cell['commission']
    trade_engine.set_cell(cell_id, exchange, *get_cell_info(cell))

    strategy = common.createInstance(module_name, class_name, config, quote_engine, trade_engine)

    if hasattr(strategy, 'trainning'):
        strategy.trainning()

    if not args.loop:
        strategy.polling()
        exit(1)

    while(True):
        if args.debug:
            delay_seconds = strategy.polling()
        else:
            try:
                delay_seconds = strategy.polling()
            except Exception as ept:
                delay_seconds = timedelta(seconds=config['loop_sec']).total_seconds()
                log.critical(ept)
        time.sleep(delay_seconds)


def real_hand(args):
    cell_id = args.iid
    cell = get_cell(cell_id)
    if not cell:
        print('%s not exist' % (cell_id))
        exit(1)

    exchange_name = cell['exchange']
    if args.print:
        log.print_switch = True
    if args.log:
        log.log_switch = True
        logfilename = cell_id + ".log"
        print(logfilename)
        log.init('real', logfilename)
        info = 'cell_id: %s,  exchange_name: %s' % (cell_id, exchange_name)
        log.info("%s" % (info))

    broker_path, broker = get_cell_broker(cell)
    exchange = create_exchange(exchange_name, broker)
    if not exchange:
        print("exchange name error!")
        exit(1)

    config_path = cell["config_path"]
    if config_path:
        config = common.get_json_config(config_path)
    else:
        config = None

    trade_engine = ExchangeTradeEngine(config)
    cfg_commission = cell['commission']
    trade_engine.set_cell(cell_id, exchange, *get_cell_info(cell))
    trade_engine.now_time = datetime.now()

    pst = trade_engine.get_position(cell_id)
    pst_base_qty = trade.get_pst_qty(pst)
    if pst_base_qty:
        symbol = trade.get_pst_symbol(pst)
        multiplier = trade.get_pst_multiplier(pst)
    else:
        from common.contract import get_multiplier_by_symbol
        if config:
            if 'contract_code' in config:
                code = config['contract_code']
                symbol, multiplier = trade_engine.get_symbol_by_code(code)
            else:
                symbol = config['symbol']
                multiplier = get_multiplier_by_symbol(symbol)
        else:
            symbol = cell['symbol']
            multiplier = get_multiplier_by_symbol(symbol)


    side = args.side
    oc = args.oc
    pst = trade_engine.get_position(cell_id)
    print("pst: {}".format(pst))
    from strategy import check_pst
    if not check_pst(pst, oc, side):
        print("oc: {} error!".format(oc))
        exchange.close()
        exit(1)

    qty = args.qty
    pst_base_qty = trade.get_pst_qty(pst)
    if oc == OC_CLOSE and qty > abs(pst_base_qty):
        print("qty: cmd {} > pst {}".format(qty, pst_base_qty))
        exchange._get_ex_pst(symbol)
        exchange.close()
        exit(1)

    params = {
        "cell_id": cell_id,
        'side': side,
        'symbol': symbol,
        'multiplier': multiplier,
        'price': args.price,
        'qty': qty
    }
    if oc:
        params['oc'] = oc
    print('real hand params: ', params)
    ret = trade_engine.new_limit_bill(**params)
    print('send order ok!  {}'.format(ret))

    exchange.close()


def round_commission(commission):
    for coin in commission:
        commission[coin] = round(commission[coin], 8)
    return commission


exchanges = {}
def get_exchange_key(exchange_name, broker_path):
    return '{}_{}'.format(exchange_name, broker_path)

def init_exchanges(cells):
    for cell in cells:
        exchange_name = cell["exchange"]
        broker_path, broker = get_cell_broker(cell)
        exchange_key = get_exchange_key(exchange_name, broker_path)
        if exchange_key in exchanges:
            continue
        try:
            exchange = create_exchange(exchange_name, broker)
            if not exchange:
                print("exchange name error!")
                exit(1)
            exchange.connect()
            exchange.ping()
            exchanges[exchange_key] = exchange
        except Exception as ept:
            log.critical(ept)
            print(ept)


def get_exchange(exchange_name, broker_path):
    exchange_key = get_exchange_key(exchange_name, broker_path)
    return exchanges[exchange_key] if exchange_key in exchanges else None

def close_all_exchange():
    for exchange in exchanges.values():
        exchange.close()


def real_list(args):
    query = {"user": args.user}
    if args.status:
        query["status"] = args.status
    cells = get_cells(query)
    all_asset_stat = {}

    init_exchanges(cells)

    title_head_fmt = "%-25s  %12s  %18s  %16s  %36s"
    head_fmt       = "%-25s  %12s  %7.2f%% (%3d/%3d)  %8.1f(%6.2f%%) (%6.2f%%, %6.2f%%, %6.2f%%, %6.2f%%)"

    title_pst_fmt = "%16s  %16s  %16s  %14s  %14s  %32s  %32s  %11s"
    pst_fmt       = title_pst_fmt#"%18s  %18f  %18f  %12f"

    title_tail_fmt = "  %10s  %10s  %13s  %68s  %-20s  %-6s  %-30s  %-s"

    print(title_head_fmt % (common.BILL_KEY_CELL_ID, "symbol", "win_rate", 'max retrace', 'rate') +
        title_pst_fmt % ('pst_base_qty', 'pst_quote_qty', 'deal_quote_qty', "float_profit", "total_profit", "commission", 'cfg_commission', 'order_count') +
        title_tail_fmt % ('value', 'amount', 'slippage_rate', 'threshold', "exchange", "status", "broker_path", "config_path"))
    for cell in cells:
        cell_id = cell[common.BILL_KEY_CELL_ID]
        exchange_name = cell["exchange"]
        if "status" in cell:
            status = cell["status"]
        else:
            status = ""
        #if status != args.status and status != "":
        #    continue

        config_path = cell["config_path"]
        if config_path:
            config = common.get_json_config(config_path)
        else:
            config = None

        broker_path, broker = get_cell_broker(cell)

        #all_value += value
        profit_info = ""
        exchange = get_exchange(exchange_name, broker_path)
        if not exchange:
            continue

        trade_engine = ExchangeTradeEngine(config)
        cfg_commission = cell['commission']
        trade_engine.set_cell(cell_id, exchange, *get_cell_info(cell))
        trade_engine.now_time = datetime.now()
        pst = trade_engine.get_position(cell_id)
        pst_base_qty = trade.get_pst_qty(pst)
        deal_quote_qty = pst[trade.POSITION_DEAL_QUOTE_QTY_KEY]

        symbol = trade.get_pst_symbol(pst)
        if symbol:
            if pst_base_qty:
                ticker_price = exchange.ticker_price(symbol)
                #print(symbol, ticker_price)
            else:
                ticker_price = None
            float_profit, total_profit = trade.get_gross_profit(pst, ticker_price)
        else:
            float_profit, total_profit = 0, 0
            if config:
                if 'contract_code' in config:
                    code = config['contract_code']
                    symbol, multiplier= trade_engine.get_symbol_by_code(code)
                else:
                    symbol = config['symbol']
            else:
                symbol = cell['symbol']

        bills = trade_engine.get_bills(cell_id)
        oc_count = 0
        win_count = 0
        pst_qty = 0
        pst_quote_qty = 0
        his_gross_profit = 0
        max_total_profit = 0
        max_retrace_profit = 0
        max_profit_rate = 0
        min_total_profit_b = 0
        min_profit_rate_b  = 0
        min_total_profit_a = 0
        min_profit_rate_a  = 0
        max_profit_rr = 0
        sum_deal_num   = 0
        sum_deal_value = 0
        arg_deal_value = 0
        for bill in bills:
            deal_qty, deal_price = trade_engine.get_bill_deal_info(bill)
            oc = bill[OC_KEY]
            side = bill[SIDE_KEY]
            if oc == OC_OPEN:
                open_price = deal_price
            else:
                oc_count += 1
                close_price = deal_price
                if ((side == SIDE_SELL and close_price > open_price) or
                    (side == SIDE_BUY  and close_price < open_price)):
                    win_count += 1

            m = bill[common.BILL_MULTIPLIER_KEY]
            deal_value = deal_qty * deal_price * m
            if side == SIDE_BUY:
                pst_qty += deal_qty
                pst_quote_qty -= deal_value
            else:
                pst_qty -= deal_qty
                pst_quote_qty += deal_value

            if pst_qty == 0:
                gross_profit = pst_quote_qty
                pst_quote_qty = 0
            else:
                if deal_price:
                    gross_profit = pst_quote_qty + pst_qty * deal_price * m
                else:
                    gross_profit = 0
            total_gross_profit = gross_profit + his_gross_profit
            if pst_qty == 0:
                his_gross_profit += gross_profit

            if deal_value and oc == OC_OPEN:
                sum_deal_num   += 1
                sum_deal_value += deal_value
                arg_deal_value = sum_deal_value / sum_deal_num

            if total_gross_profit > max_total_profit:
                max_total_profit = total_gross_profit
                max_profit_rate = max_total_profit / arg_deal_value
                if min_total_profit_b > min_total_profit_a:
                    min_total_profit_b = min_total_profit_a
                    min_profit_rate_b  = min_profit_rate_a
                min_total_profit_a = max_total_profit
                min_profit_rate_a  = max_profit_rate
            elif total_gross_profit < min_total_profit_a:
                #print(total_gross_profit, sum_deal_num, sum_deal_value, sum_deal_value / sum_deal_num)
                min_total_profit_a = total_gross_profit
                min_profit_rate_a = min_total_profit_a / arg_deal_value

            retrace_profit = total_gross_profit - max_total_profit
            if arg_deal_value:
                retrace_rate = retrace_profit / arg_deal_value
            else:
                retrace_rate = 0
            if retrace_rate < max_profit_rr:
                max_retrace_profit = retrace_profit
                max_profit_rr = retrace_rate

        if oc_count:
            win_count_rate = win_count / oc_count
        else:
            win_count_rate = 0

        if sum_deal_num:
            cur_profit_rate = total_profit / arg_deal_value
        else:
            cur_profit_rate = 0

        commission = trade.get_pst_commission(pst)
        trader = trade_engine.get_cell_trader(cell_id)
        if hasattr(trader, 'currency'):
            base_asset_name = None
            quote_asset_name = trader.currency
        else:
            base_asset_name, quote_asset_name = common.split_symbol_coins(symbol)
        if quote_asset_name not in all_asset_stat:
            all_asset_stat[quote_asset_name] = {
                trade.POSITION_QUOTE_QTY_KEY: 0,
                trade.POSITION_DEAL_QUOTE_QTY_KEY: 0,
                "float_profit": 0,
                "total_profit": 0,
                "commission": {}
            }

        asset_stat = all_asset_stat[quote_asset_name]
        asset_stat[trade.POSITION_QUOTE_QTY_KEY] += abs(pst_quote_qty)
        asset_stat[trade.POSITION_DEAL_QUOTE_QTY_KEY] += deal_quote_qty
        asset_stat['float_profit'] += float_profit
        asset_stat['total_profit'] += total_profit
        for coin in commission:
            if coin in asset_stat['commission']:
                asset_stat['commission'][coin] += commission[coin]
            else:
                asset_stat['commission'][coin] = commission[coin]

        profit_info = pst_fmt % (trade_engine.round_qty(pst_base_qty),
            trade_engine.round_price(pst_quote_qty),
            trade_engine.round_price(deal_quote_qty),
            trade_engine.round_price(float_profit),
            trade_engine.round_price(total_profit),
            round_commission(commission),
            cfg_commission,
            pst['order_count'])

        #except Exception as ept:
        #    profit_info = "error:  %s" % (ept)

        value, amount, slippage_rate, commission_rate, commission_prec = get_cell_info(cell)
        value_info  = '%s' % value if value else ''
        amount_info = '%s' % amount if amount else ''
        sr_info     = '%s' % slippage_rate if slippage_rate else ''
        threshold_info = '%s' % cell['threshold'] if 'threshold' in cell else ''

        print(head_fmt % (cell_id, symbol, win_count_rate*100, win_count, oc_count,
                          max_retrace_profit, max_profit_rr*100, min_profit_rate_b*100, max_profit_rate*100, min_profit_rate_a*100, cur_profit_rate*100) +
            profit_info +
            title_tail_fmt % (value_info, amount_info, sr_info, threshold_info, exchange_name, status, broker_path, config_path))
    close_all_exchange()

    if args.stat:
        print('assert stat:')
        for coin_name in all_asset_stat:
            asset_stat = all_asset_stat[coin_name]
            print(title_head_fmt % (coin_name, "", '', '', '') +
                title_pst_fmt % ('',
                trade_engine.round_price(asset_stat[trade.POSITION_QUOTE_QTY_KEY]),
                trade_engine.round_price(asset_stat[trade.POSITION_DEAL_QUOTE_QTY_KEY]),
                trade_engine.round_price(asset_stat['float_profit']),
                trade_engine.round_price(asset_stat['total_profit']),
                round_commission(asset_stat['commission']),
                '',
                ''))


def real_add(args):
    add_cell({
        "user": args.user,
        common.BILL_KEY_CELL_ID: args.iid,
        "symbol": args.symbol,
        "config_path": args.config_path,
        "exchange": args.exchange,
        "status": args.status,
    })


def real_delete(args):
    delete_cell(args.iid)


def real_update(args):
    record = {}
    if args.user:
        record["user"] = args.user
    if args.new_iid:
        record[common.BILL_KEY_CELL_ID] = args.new_iid
    if args.symbol:
        record["symbol"] = args.symbol
    if args.config_path:
        record["config_path"] = args.config_path
    if args.exchange:
        record["exchange"] = args.exchange
    if args.status:
        record["status"] = args.status
    if args.value:
        record["value"] = args.value
    if args.amount:
        record["amount"] = args.amount
    if args.slippage_rate:
        record["slippage_rate"] = args.slippage_rate
    if args.threshold:
        record["threshold"] = args.threshold
    if args.broker:
        record["broker"] = args.broker

    if record:
        update_cell(args.iid, record)


def real_analyze(args):
    if args.print:
        log.print_switch = True

    cell_id = args.iid
    cell = get_cell(cell_id)
    if not cell:
        print('%s not exist' % (cell_id))
        exit(1)

    config_path = cell["config_path"]
    if config_path:
        config = common.get_json_config(config_path)
    else:
        config = None

    exchange_name = cell['exchange']
    broker_path, broker = get_cell_broker(cell)
    exchange = create_exchange(exchange_name, broker)
    if not exchange:
        print("exchange name error!")
        exit(1)

    trade_engine = ExchangeTradeEngine(config)
    trade_engine.set_cell(cell_id, exchange, *get_cell_info(cell))
    trader = trade_engine.get_cell_trader(cell_id)
    trade_engine.handle_open_bills(cell_id)
    bills = trade_engine.get_all_bills(cell_id)
    oc_count = 0
    win_count = 0
    win_count_rate = 0
    his_gross_profit = 0
    total_gross_profit = 0
    max_total_profit = 0
    total_commission = {}
    pst_qty = 0
    pst_quote_qty = 0
    cb_fmt = '%26s  %14s  %10s  %18s  %20s  %5s  %5s  %10s  %12s  %10s  %12s  %18s  %15s  %15s  %18s  %30s  %12s  %12s  %7s  %12s'
    cb_title = ('create_time', 'symbol', 'multiplier', 'win_rate', 'retrace', 'oc', 'side', 'qty', 'limit_price', 'deal_qty', 'deal_price', 'profit', 'total_profit', 'commission', 'total_commission', 'rmk', 'pst_qty', 'pst_cost', 'status', 'order_id')
    print(cb_fmt % (cb_title))
    for cb in bills:
        #print(cb)
        order_id = cb['order_id']
        #print(order)
        commission = trade_engine.get_bill_commission(cb)
        trade.stat_commission(total_commission, commission)

        deal_qty, deal_price = trade_engine.get_bill_deal_info(cb)

        m = cb[common.BILL_MULTIPLIER_KEY]
        deal_value = deal_qty * deal_price * m

        oc = cb['oc']
        side = cb['side']

        if oc == OC_OPEN:
            open_price = deal_price
        else:
            oc_count += 1
            close_price = deal_price
            if ((side == SIDE_SELL and close_price > open_price) or
                (side == SIDE_BUY  and close_price < open_price)):
                win_count += 1
            win_count_rate = win_count / oc_count

        if side == SIDE_BUY:
            pst_qty += deal_qty
            pst_quote_qty -= deal_qty * deal_price * m
        else:
            pst_qty -= deal_qty
            pst_quote_qty += deal_qty * deal_price * m
        if pst_qty > 0:
            pst_cost = abs(pst_quote_qty / pst_qty / m)
        else:
            pst_cost = 0

        if pst_qty == 0:
            gross_profit = pst_quote_qty
            if deal_value:
                gross_profit_rate = gross_profit / deal_value
            else:
                gross_profit_rate = 0
            pst_quote_qty = 0
        else:
            if deal_price:
                gross_profit = pst_quote_qty + pst_qty * deal_price * m
            else:
                gross_profit = 0
            gross_profit_rate = 0
        total_gross_profit = gross_profit + his_gross_profit
        if pst_qty == 0:
            his_gross_profit += gross_profit

        if total_gross_profit > max_total_profit:
            max_total_profit = total_gross_profit

        symbol = cb[common.BILL_SYMBOL_KEY]
        multiplier = cb[common.BILL_MULTIPLIER_KEY]

        print(cb_fmt % (cb['create_time'], symbol, multiplier,
            '{:7.2%} ({:3d}/{:3d})'.format(win_count_rate, win_count, oc_count),
            '{:.2f}'.format(total_gross_profit-max_total_profit),
            oc, side,
            cb['qty'], cb['price'], deal_qty, trade_engine.round_price(deal_price),
            '{} ({:3.2%})'.format(round(gross_profit, 2), gross_profit_rate) if gross_profit else '',
            round(total_gross_profit, 2),
            round_commission(commission), round_commission(total_commission),
            cb['rmk'],
            trade_engine.round_qty(pst_qty), trade_engine.round_price(pst_cost), cb['status'], cb['order_id']))
    #print(symbol, exchange._get_ex_pst(symbol))
    exchange.close()


def real():
    parser = argparse.ArgumentParser(description='real run one')
    subparsers = parser.add_subparsers(help='sub-command help')

    parser_run = subparsers.add_parser('run', help='run cell')
    parser_run.add_argument('-iid', required=True, help='cell id')
    parser_run.add_argument('-loop', action="store_true", help='run loop')
    parser_run.add_argument('-debug', action="store_true", help='run debug')
    parser_run.add_argument('--log', action="store_true", help='log info')
    parser_run.add_argument('--print', action="store_true", help='print info')
    parser_run.set_defaults(func=real_run)

    parser_hand = subparsers.add_parser('hand', help='handmade cell')
    parser_hand.add_argument('-iid', required=True, help='cell id')
    parser_hand.add_argument('-oc', choices=[OC_OPEN, OC_CLOSE], help='')
    parser_hand.add_argument('-side', required=True, choices=[SIDE_BUY, SIDE_SELL], help='')
    parser_hand.add_argument('-price', required=True, type=float, help='price')
    parser_hand.add_argument('-qty', required=True, type=float, help='quantity')
    parser_hand.add_argument('--log', action="store_true", help='log info')
    parser_hand.add_argument('--print', action="store_true", help='print info')
    parser_hand.set_defaults(func=real_hand)


    parser_list = subparsers.add_parser('list', help='list of cell')
    parser_list.add_argument('-user', help='user name')
    parser_list.add_argument('--status', choices=cell_statuses, help='cell status')
    parser_list.add_argument('--stat', help='stat all', action="store_true")
    parser_list.set_defaults(func=real_list)

    parser_add = subparsers.add_parser('add', help='add new cell')
    parser_add.add_argument('-user', required=True, help='user name')
    parser_add.add_argument('-exchange', required=True, choices=get_exchange_names(), help='exchange name')
    parser_add.add_argument('-iid', required=True, help='cell id')
    parser_add.add_argument('-symbol', help='symbol')
    parser_add.add_argument('-config_path', help='config path')
    parser_add.add_argument('-status', choices=cell_statuses, default=cell_statuses[0], help='cell status')
    parser_add.set_defaults(func=real_add)

    parser_delete = subparsers.add_parser('delete', help='delete cell')
    parser_delete.add_argument('-iid', required=True, help='cell id')
    parser_delete.set_defaults(func=real_delete)

    parser_update = subparsers.add_parser('update', help='update cell')
    parser_update.add_argument('-iid', required=True, help='cell id')
    parser_update.add_argument('--user', help='user name')
    parser_update.add_argument('--new_iid', help='new cell id')
    parser_update.add_argument('--symbol', help='symbol')
    parser_update.add_argument('--config_path', help='config path')
    parser_update.add_argument('--exchange', help='cell exchange')
    parser_update.add_argument('--status', choices=cell_statuses, help='cell status')
    parser_update.add_argument('--value', type=int, help='value')
    parser_update.add_argument('--amount', type=int, help='amount')
    parser_update.add_argument('--slippage_rate', type=float, help='value')
    parser_update.add_argument('--threshold', type=float, nargs=2, help='y threshold for open and close, eg: 0.001 -0.001')
    parser_update.add_argument('--broker', help='broker path')
    parser_update.set_defaults(func=real_update)

    parser_analyze = subparsers.add_parser('analyze', help='analyze cell')
    parser_analyze.add_argument('-iid', required=True, help='cell id')
    parser_analyze.add_argument('--print', action="store_true", help='print info')
    parser_analyze.set_defaults(func=real_analyze)

    args = parser.parse_args()

    if hasattr(args, 'func'):
        args.func(args)


if __name__ == "__main__":
    real()

