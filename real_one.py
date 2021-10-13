import argparse
import common
from exchange.exchange_factory import get_exchange_names, create_exchange




if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='real run one')
    parser.add_argument('-exchange', required=True, help='exchange')
    parser.add_argument('-config', required=True, help='config')
    args = parser.parse_args()

    config = common.get_json_config(args.config)
    #print(config)

    exchange = create_exchange(args.exchange)
    if not exchange:
        print("exchange name error!")
        exit(1)
    exchange.connect()
    exchange.ping()

    module_name = config["module_name"].replace("/", ".")
    class_name = config["class_name"]
    strategy = common.createInstance(module_name, class_name, config, exchange, exchange)
    strategy.run_one()

