import argparse
import datetime, time
import os
import common
import common.log as log
from exchange.exchange_factory import get_exchange_names, create_exchange
from engine.trade_engine import TradeEngine


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='real run one')
    parser.add_argument('-exchange', choices=get_exchange_names(), help='exchange name')
    parser.add_argument('-config', required=True, help='config')
    parser.add_argument('-iid', required=True, help='instance id')
    parser.add_argument('-loop', action="store_true", help='run loop')
    parser.add_argument('-debug', action="store_true", help='run debug')
    parser.add_argument('--log', action="store_true", help='log info')
    parser.add_argument('--print', action="store_true", help='print info')
    args = parser.parse_args()

    instance_id = args.iid
    exchange_name = args.exchange

    config = common.get_json_config(args.config)
    module_name = config["module_name"].replace("/", ".")
    class_name = config["class_name"]
    #print(config)

    if args.print:
        log.print_switch = True

    if args.log:
        log.log_switch = True

        logfilename = instance_id + ".log"
        print(logfilename)

        log.init('real', logfilename)
        info = 'instance_id: %s,  exchange_name: %s' % (instance_id, exchange_name)
        log.info("%s" % (info))
        log.info("strategy name: %s;  config: %s" % (class_name, config))

    exchange = create_exchange(exchange_name)
    if not exchange:
        print("exchange name error!")
        exit(1)
    exchange.connect()
    exchange.ping()
    trade_engine = TradeEngine(instance_id, exchange)

    strategy = common.createInstance(module_name, class_name, instance_id, config, exchange, trade_engine)
    if not args.loop:
        strategy.on_tick()
        exit(1)

    prefix = '.'*10
    while(True):
        tick_start = datetime.datetime.now()
        log.info("%s  %s tick start  %s" % (prefix, tick_start, '.'*72))

        if args.debug:
            strategy.on_tick()
        else:
            try:
                strategy.on_tick()
            except Exception as ept:
                log.critical(ept)

        tick_end = datetime.datetime.now()
        log.info("%s  %s tick end, cost: %s\n\n" % (prefix, tick_end, tick_end - tick_start))

        time.sleep(config["loop_sec"])

