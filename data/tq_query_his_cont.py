import sys
import argparse
from datetime import datetime
import pandas as pd
from tqsdk import TqApi, TqAuth
from data import get_tq


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='klines print or check')
    parser.add_argument('-symbol', required=True, nargs='*', help='')
    parser.add_argument('-n', type=int, default=200, help='')
    parser.add_argument('--broker', help='')
    args = parser.parse_args()

    pd.set_option('display.max_rows', None)
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', 1000)

    name, password = get_tq(args.broker)
    api = TqApi(auth=TqAuth(name, password))

    conts = api.query_his_cont_quotes(symbol=args.symbol, n=args.n)
    print(conts)

    api.close()
