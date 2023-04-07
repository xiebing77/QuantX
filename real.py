import argparse
import time
from datetime import timedelta
import os
import common
import common.log as log
from common import SIDE_BUY, SIDE_SELL, OC_OPEN, OC_CLOSE
from common import ORDER_TYPE_LIMIT
from common.instance import INSTANCE_COLLECTION_NAME, INSTANCE_STATUS_START, INSTANCE_STATUS_STOP, instance_statuses, add_instance, delete_instance, update_instance
from exchange.exchange_factory import get_exchange_names, create_exchange
from engine.quote import QuoteEngine
import engine.trade as trade
from engine.trade.exchange import ExchangeTradeEngine, get_commission_from_trades
from db.mongodb import get_mongodb
import setup


td_db = get_mongodb(setup.trade_db_name)


def real_run(args):
    instance_id = args.iid
    ss = td_db.find(INSTANCE_COLLECTION_NAME, {"instance_id": instance_id})
    if not ss:
        print('%s not exist' % (instance_id))
        exit(1)
    s = ss[0]
    symbol = s['symbol']
    exchange_name = s['exchange']
    config_path = s["config_path"]
    config = common.get_json_config(config_path)
    module_name = config["module_name"].replace("/", ".")
    class_name = config["class_name"]

    if args.print:
        log.print_switch = True
    if args.log:
        log.log_switch = True
        logfilename = instance_id + ".log"
        print(logfilename)
        log.init('real', logfilename)

    #log.info("strategy name: %s;  config: %s" % (class_name, config))
    log.info('instance_id: %s,  exchange_name: %s' % (instance_id, exchange_name))

    exchange = create_exchange(exchange_name)
    if not exchange:
        print("exchange name error!")
        exit(1)
    exchange.connect()
    exchange.ping()
    quote_engine = QuoteEngine(exchange)
    trade_engine = ExchangeTradeEngine(instance_id, exchange)

    strategy = common.createInstance(module_name, class_name, instance_id, config, quote_engine, trade_engine)

    if hasattr(strategy, 'set_value'):
        strategy.set_value(s['value'])
    if hasattr(strategy, 'set_slippage_rate'):
        strategy.set_slippage_rate(s['slippage_rate'])
    if hasattr(strategy, 'load_model'):
        strategy.load_train()
        strategy.load_model()

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
    instance_id = args.iid
    ss = td_db.find(INSTANCE_COLLECTION_NAME, {"instance_id": instance_id})
    if not ss:
        print('%s not exist' % (instance_id))
        exit(1)
    s = ss[0]

    exchange_name = s['exchange']
    if args.print:
        log.print_switch = True
    if args.log:
        log.log_switch = True
        logfilename = instance_id + ".log"
        print(logfilename)
        log.init('real', logfilename)
        info = 'instance_id: %s,  exchange_name: %s' % (instance_id, exchange_name)
        log.info("%s" % (info))

    exchange = create_exchange(exchange_name)
    if not exchange:
        print("exchange name error!")
        exit(1)
    exchange.connect()
    exchange.ping()
    trade_engine = ExchangeTradeEngine(instance_id, exchange)

    config_path = s["config_path"]
    if config_path:
        config = common.get_json_config(config_path)
        if 'contract_code' in config:
            code = config['contract_code']
            symbol = trade_engine.get_symbol_by_code(code)
        else:
            symbol = config['symbol']
    else:
        symbol = s['symbol']

    params = {
        'side': args.side,
        'symbol': symbol,
        'multiplier': trade_engine.get_multiplier_by_symbol(symbol),
        'price': args.price,
        'qty': args.qty
    }
    if args.oc:
        params['oc'] = args.oc
    print('real hand params: ', params)
    order_id = trade_engine.new_limit_bill(**params)

    for i in range(5):
        time.sleep(1)
        buy_open_bills, sell_open_bills = trade_engine.handle_open_bills()
        if len(buy_open_bills)+len(sell_open_bills) == 0:
            break


def round_commission(commission):
    for coin in commission:
        commission[coin] = round(commission[coin], 8)
    return commission


exchanges = {}
def init_exchanges(exchange_names):
    for exchange_name in set(exchange_names):
        try:
            exchange = create_exchange(exchange_name)
            if not exchange:
                print("exchange name error!")
                exit(1)
            exchange.connect()
            exchange.ping()
            exchanges[exchange_name] = exchange
        except Exception as ept:
            log.critical(ept)
            print(ept)


def get_exchange(exchange_name):
    if exchange_name in exchanges:
        return exchanges[exchange_name]
    return None


def close_all_exchange():
    for exchange in exchanges.values():
        exchange.close()


def real_list(args):
    query = {"user": args.user}
    if args.status:
        query["status"] = args.status
    ss = td_db.find(INSTANCE_COLLECTION_NAME, query)
    #print(ss)
    all_asset_stat = {}

    exchange_names = [s["exchange"] for s in ss]
    init_exchanges(exchange_names)

    title_head_fmt = "%-25s  %12s"
    head_fmt       = "%-25s  %12s"

    title_pst_fmt = "%16s  %16s  %16s  %14s  %14s  %32s  %32s  %11s"
    pst_fmt       = title_pst_fmt#"%18s  %18f  %18f  %12f"

    title_tail_fmt = "  %10s  %10s  %13s  %20s  %-16s  %-6s  %-s"

    print(title_head_fmt % ("instance_id", "symbol") +
        title_pst_fmt % ('pst_base_qty', 'pst_quote_qty', 'deal_quote_qty', "float_profit", "total_profit", "commission", 'cfg_commission', 'order_count') +
        title_tail_fmt % ('value', 'amount', 'slippage_rate', 'threshold', "exchange", "status", "config_path"))
    for s in ss:
        instance_id = s["instance_id"]
        exchange_name = s["exchange"]
        if "status" in s:
            status = s["status"]
        else:
            status = ""
        #if status != args.status and status != "":
        #    continue

        config_path = s["config_path"]
        if config_path:
            config = common.get_json_config(config_path)
        else:
            config = None

        #all_value += value
        profit_info = ""
        exchange = get_exchange(exchange_name)
        if not exchange:
            continue

        trade_engine = ExchangeTradeEngine(instance_id, exchange)
        cfg_commission = s['commission']
        trade_engine.set_commission(cfg_commission['rate'], int(cfg_commission['prec']))
        pst = trade_engine.get_position()
        pst_base_qty = trade.get_pst_qty(pst)
        pst_quote_qty = pst[trade.POSITION_QUOTE_QTY_KEY]
        deal_quote_qty = pst[trade.POSITION_DEAL_QUOTE_QTY_KEY]

        symbol = trade.get_pst_symbol(pst)
        if symbol:
            ticker_price = exchange.ticker_price(symbol)
            float_profit, total_profit = trade.get_gross_profit(pst, ticker_price)
        else:
            float_profit, total_profit = 0, 0
            if config and 'contract_code' in config:
                code = config['contract_code']
                symbol = code # trade_engine.get_symbol_by_code(code)
            else:
                symbol = config['symbol']

        commission = trade.get_pst_commission(pst)
        trader = trade_engine.trader
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
        asset_stat[trade.POSITION_QUOTE_QTY_KEY] += pst_quote_qty
        asset_stat[trade.POSITION_DEAL_QUOTE_QTY_KEY] += deal_quote_qty
        asset_stat['float_profit'] += float_profit
        asset_stat['total_profit'] += total_profit
        for coin in commission:
            if coin in asset_stat['commission']:
                asset_stat['commission'][coin] += commission[coin]
            else:
                asset_stat['commission'][coin] = commission[coin]

        if config and 'prec' in config:
            prec_price = config['prec']['price']
            prec_qty   = config['prec']['qty']
        else:
            prec_qty, prec_price = trade_engine.get_symbol_prec(symbol)
        profit_info = pst_fmt % (round(pst_base_qty, prec_qty),
            round(pst_quote_qty, prec_price),
            round(deal_quote_qty, prec_price),
            round(float_profit, prec_price),
            round(total_profit, prec_price),
            round_commission(commission),
            cfg_commission,
            pst['order_count'])

        #except Exception as ept:
        #    profit_info = "error:  %s" % (ept)

        if 'value' in s:
            value_info = '%s'%s['value']
        else:
            value_info = ''

        if 'amount' in s:
            amount_info = '%s'%s['amount']
        else:
            amount_info = ''

        if 'slippage_rate' in s:
            sr_info = '%s'%s['slippage_rate']
        else:
            sr_info = ''

        if 'threshold' in s:
            threshold_info = '%s'%s['threshold']
        else:
            threshold_info = ''

        print(head_fmt % (instance_id, symbol) +
            profit_info +
            title_tail_fmt % (value_info, amount_info, sr_info, threshold_info, exchange_name, status, config_path))
    close_all_exchange()

    if args.stat:
        print('assert stat:')
        for coin_name in all_asset_stat:
            asset_stat = all_asset_stat[coin_name]
            print(title_head_fmt % (coin_name, "") +
                title_pst_fmt % ('',
                round(asset_stat[trade.POSITION_QUOTE_QTY_KEY], prec_price),
                round(asset_stat[trade.POSITION_DEAL_QUOTE_QTY_KEY], prec_price),
                round(asset_stat['float_profit'], prec_price),
                round(asset_stat['total_profit'], prec_price),
                round_commission(asset_stat['commission']),
                '',
                ''))


def real_add(args):
    add_instance({
        "user": args.user,
        "instance_id": args.iid,
        "symbol": args.symbol,
        "config_path": args.config_path,
        "exchange": args.exchange,
        "status": args.status,
    })


def real_delete(args):
    delete_instance({"instance_id": args.iid})


def real_update(args):
    record = {}
    if args.user:
        record["user"] = args.user
    if args.new_iid:
        record["instance_id"] = args.new_iid
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

    if record:
        update_instance({"instance_id": args.iid}, record)


def real_analyze(args):
    instance_id = args.iid
    ss = td_db.find(INSTANCE_COLLECTION_NAME, {"instance_id": instance_id})
    if not ss:
        print('%s not exist' % (instance_id))
        exit(1)
    s = ss[0]

    config_path = s["config_path"]
    if config_path:
        config = common.get_json_config(config_path)

    exchange_name = s['exchange']
    exchange = create_exchange(exchange_name)
    if not exchange:
        print("exchange name error!")
        exit(1)

    trade_engine = ExchangeTradeEngine(instance_id, exchange)
    trader = trade_engine.trader
    close_bills = trade_engine.get_bills(common.BILL_STATUS_CLOSE)
    pst_qty = 0
    pst_quote_qty = 0
    cb_fmt = '%26s  %14s  %10s  %5s  %5s  %10s  %12s  %12s  %12s  %15s  %30s  %12s  %12s  %7s  %12s'
    cb_title = ('create_time', 'symbol', 'multiplier', 'oc', 'side', 'qty', 'limit_price', 'deal_price', 'profit', 'commission', 'rmk', 'pst_qty', 'pst_cost', 'status', 'order_id')
    print(cb_fmt % (cb_title))
    for cb in close_bills:
        #print(cb)
        order_id = cb['order_id']
        order = trade_engine.get_order_from_db(cb['order_id'])
        #print(order)
        trades = trade_engine._get_trades_from_db([order_id])
        commission = get_commission_from_trades(trader, trades)

        deal_price = 0
        pst_cost = 0
        if order:
            executedQty = trader.get_order_exec_qty(order)
            if executedQty > 0:
                cummulativeQuoteQty = trader.get_order_exec_quote_qty(order)
                if exchange.order_is_buy(order):
                    pst_qty += executedQty
                    pst_quote_qty += cummulativeQuoteQty
                else:
                    pst_qty -= executedQty
                    pst_quote_qty -= cummulativeQuoteQty
                deal_price = cummulativeQuoteQty / executedQty
                if pst_qty != 0:
                    pst_cost = float(pst_quote_qty / pst_qty)

        oc = cb['oc']
        side = cb['side']
        if deal_price > 0:
            if oc == OC_OPEN:
                pre_deal_price = deal_price
                profit = 0
            else:
                diff_price = deal_price - pre_deal_price
                if side == SIDE_BUY:
                    diff_price = -diff_price
                profit = diff_price / pre_deal_price
        else:
            profit = 0

        symbol = cb[common.BILL_SYMBOL_KEY]
        multiplier = cb[common.BILL_MULTIPLIER_KEY]
        if 'prec' in config:
            prec_price = config['prec']['price']
            prec_qty   = config['prec']['qty']
        else:
            exchange.connect()
            prec_qty, prec_price = trade_engine.get_symbol_prec(symbol)
        print(cb_fmt % (cb['create_time'], symbol, multiplier, oc, side,
            cb['qty'], cb['price'], round(deal_price, prec_price), round(profit, 4), round_commission(commission),
            cb['rmk'],
            round(pst_qty, prec_qty), round(pst_cost, prec_price), cb['status'], cb['order_id']))


def real():
    parser = argparse.ArgumentParser(description='real run one')
    subparsers = parser.add_subparsers(help='sub-command help')

    parser_run = subparsers.add_parser('run', help='run instance')
    parser_run.add_argument('-iid', required=True, help='instance id')
    parser_run.add_argument('-loop', action="store_true", help='run loop')
    parser_run.add_argument('-debug', action="store_true", help='run debug')
    parser_run.add_argument('--log', action="store_true", help='log info')
    parser_run.add_argument('--print', action="store_true", help='print info')
    parser_run.set_defaults(func=real_run)

    parser_hand = subparsers.add_parser('hand', help='handmade instance')
    parser_hand.add_argument('-iid', required=True, help='instance id')
    parser_hand.add_argument('-oc', choices=[OC_OPEN, OC_CLOSE], help='')
    parser_hand.add_argument('-side', required=True, choices=[SIDE_BUY, SIDE_SELL], help='')
    parser_hand.add_argument('-price', required=True, type=float, help='price')
    parser_hand.add_argument('-qty', required=True, type=float, help='quantity')
    parser_hand.add_argument('--log', action="store_true", help='log info')
    parser_hand.add_argument('--print', action="store_true", help='print info')
    parser_hand.set_defaults(func=real_hand)


    parser_list = subparsers.add_parser('list', help='list of instance')
    parser_list.add_argument('-user', help='user name')
    parser_list.add_argument('--status', choices=instance_statuses, help='instance status')
    parser_list.add_argument('--stat', help='stat all', action="store_true")
    parser_list.set_defaults(func=real_list)

    parser_add = subparsers.add_parser('add', help='add new instance')
    parser_add.add_argument('-user', required=True, help='user name')
    parser_add.add_argument('-exchange', required=True, choices=get_exchange_names(), help='exchange name')
    parser_add.add_argument('-iid', required=True, help='instance id')
    parser_add.add_argument('-symbol', help='symbol')
    parser_add.add_argument('-config_path', help='config path')
    parser_add.add_argument('-status', choices=instance_statuses, default=INSTANCE_STATUS_START, help='instance status')
    parser_add.set_defaults(func=real_add)

    parser_delete = subparsers.add_parser('delete', help='delete instance')
    parser_delete.add_argument('-iid', required=True, help='instance id')
    parser_delete.set_defaults(func=real_delete)

    parser_update = subparsers.add_parser('update', help='update instance')
    parser_update.add_argument('-iid', required=True, help='instance id')
    parser_update.add_argument('--user', help='user name')
    parser_update.add_argument('--new_iid', help='new instance id')
    parser_update.add_argument('--symbol', help='symbol')
    parser_update.add_argument('--config_path', help='config path')
    parser_update.add_argument('--exchange', help='instance exchange')
    parser_update.add_argument('--status', choices=instance_statuses, help='instance status')
    parser_update.add_argument('--value', type=int, help='value')
    parser_update.add_argument('--amount', type=int, help='amount')
    parser_update.add_argument('--slippage_rate', type=float, help='value')
    parser_update.add_argument('--threshold', type=float, nargs=2, help='y threshold for open and close, eg: 0.001 -0.001')
    parser_update.set_defaults(func=real_update)

    parser_analyze = subparsers.add_parser('analyze', help='analyze instance')
    parser_analyze.add_argument('-iid', required=True, help='instance id')
    parser_analyze.set_defaults(func=real_analyze)

    args = parser.parse_args()

    if hasattr(args, 'func'):
        args.func(args)


if __name__ == "__main__":
    real()

