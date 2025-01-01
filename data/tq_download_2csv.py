import sys
import os
import argparse
import time
from datetime import datetime
from dateutil.relativedelta import relativedelta
from contextlib import closing
from data import get_tq


def tq_download_his_data(api, product, code, sec):
    if args.sec == 300:
        tt = '5m'
    elif args.sec == 24*60*60:
        tt = '1d'

    symbol = product + code
    csv_file_name = '{}_{}.csv'.format(symbol, tt)
    if os.path.exists(csv_file_name):
        print(f'{csv_file_name} already exists!')
        return None

    print('{} {}'.format(sec ,csv_file_name))

    y = int('20'+code[:2])
    m = int(code[2:])
    #print(y,m)
    y_start = y - 1
    y_end   = y
    m_start = m
    if m < 12:
        m_end = m + 1
    else:
        y_end += 1
        m_end = 1

    kd = DataDownloader(api, symbol_list=symbol, dur_sec=sec,
                        start_dt=datetime(y_start, m_start, 1, 1, 0 ,0),
                        end_dt=datetime(y_end, m_end, 1, 1, 0 ,0),
                        csv_file_name=csv_file_name)

    return kd


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='klines print or check')
    parser.add_argument('-product', required=True, help='')
    parser.add_argument('-sec', type=int, default=86400, help='')
    parser.add_argument('-codes', nargs='*', help='egg: 1605')
    parser.add_argument('--broker', help='')
    args = parser.parse_args()

    if args.codes:
        codes = args.codes
    else:
        from data import get_main_codes
        codes = get_main_codes(args.product)
    print(codes)

    name, password = get_tq(args.broker)
    from tqsdk import TqApi, TqAuth
    from tqsdk.tools import DataDownloader
    api = TqApi(auth=TqAuth(name, password))

    download_tasks = {}
    for code in codes:
        kd = tq_download_his_data(api, args.product, code, args.sec)
        if not kd:
            continue
        download_tasks[code] = kd

    # 使用with closing机制确保下载完成后释放对应的资源
    with closing(api):
        while not all([v.is_finished() for v in download_tasks.values()]):
            api.wait_update()
            sys.stdout.flush()
            info = { k:("%.2f%%" % v.get_progress()) for k,v in download_tasks.items() }
            sys.stdout.write("\rprogress: %s" % info)
    sys.stdout.write('\n')
    '''
    # 使用with closing机制确保下载完成后释放对应的资源
    with closing(api):
        while not kd.is_finished(): #or not td.is_finished():
            api.wait_update()
            sys.stdout.flush()
            sys.stdout.write("\rprogress: kline: %.2f%%" % (kd.get_progress()))
    sys.stdout.write('\n')
    '''
