import sys
import argparse
from datetime import datetime
from dateutil.relativedelta import relativedelta
from contextlib import closing
from tqsdk import TqApi, TqAuth
from tqsdk.tools import DataDownloader

symtem_start_dt = datetime(2016, 1, 1, 6, 0, 0)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='klines print or check')
    parser.add_argument('-symbol', required=True, help='')
    parser.add_argument('-sec', type=int, default=0, help='')
    parser.add_argument('-code', required=True, help='')
    args = parser.parse_args()

    if args.sec == 300:
        tt = '5m'
    elif args.sec == 24*60*60:
        tt = '1d'

    symbol = args.symbol + args.code
    csv_file_name = '{}_{}.csv'.format(symbol, tt)
    print('{} {}'.format(args.sec ,csv_file_name))

    y = int('20'+args.code[:2])
    m = int(args.code[2:])
    print(y,m)

    api = TqApi(auth=TqAuth("xj2024", "G267cp_SPsYge"))
    kd = DataDownloader(api, symbol_list=symbol, dur_sec=args.sec,
                        start_dt=datetime(y-1, m, 1, 1, 0 ,0),
                        end_dt=datetime(y, m+1, 1, 1, 0 ,0),
                        csv_file_name=csv_file_name)

    # 使用with closing机制确保下载完成后释放对应的资源
    with closing(api):
        while not kd.is_finished(): #or not td.is_finished():
            api.wait_update()
            sys.stdout.flush()
            sys.stdout.write("\rprogress: kline: %.2f%%" % (kd.get_progress()))
    sys.stdout.write('\n')
