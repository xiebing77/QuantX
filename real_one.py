import argparse
import common
from exchange.exchange_factory import get_exchange_names, create_exchange
from engine.trade_engine import TradeEngine


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='real run one')
    parser.add_argument('-exchange', choices=get_exchange_names(), help='exchange name')
    parser.add_argument('-config', required=True, help='config')
    parser.add_argument('-iid', required=True, help='instance id')
    args = parser.parse_args()

    instance_id = args.iid
    config = common.get_json_config(args.config)
    #print(config)

    exchange_name = args.exchange
    exchange = create_exchange(exchange_name)
    if not exchange:
        print("exchange name error!")
        exit(1)
    exchange.connect()
    exchange.ping()
    trade_engine = TradeEngine(instance_id, exchange)

    module_name = config["module_name"].replace("/", ".")
    class_name = config["class_name"]
    strategy = common.createInstance(module_name, class_name, instance_id, config, exchange, trade_engine)
    strategy.run_one()

