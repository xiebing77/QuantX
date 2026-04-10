import sys
sys.path.append('../')
import os
import argparse
import time
from datetime import datetime
from dateutil.relativedelta import relativedelta
from exchange.exchange_factory import create_exchange
from contextlib import closing
from data import get_tq, contractes
import pandas as pd


def tq_download_his_data(api, product, code, sec):
    if args.sec == 0:
        tt = 'tick'
    elif args.sec < 60:
        tt = f'{args.sec}s'
    elif args.sec == 60:
        tt = '1m'
    elif args.sec == 300:
        tt = '5m'
    elif args.sec == 900:
        tt = '15m'
    elif args.sec == 3600:
        tt = '1h'
    elif args.sec == 24*60*60:
        tt = '1d'

    e_name, p_name = product.split('.')
    if e_name == 'CZCE' and len(code) == 4:
        symbol = product + code[1:]
    else:
        symbol = product + code
    csv_file_name = '{}_{}.csv'.format(symbol, tt)
    if os.path.exists(csv_file_name):
        print(f'{csv_file_name} already exists!')
        return None, None

    main_mouths = contractes[e_name][p_name][-1]
    print('{} {}   {}'.format(sec ,csv_file_name, main_mouths))

    if len(code) == 4:
        y = int('20'+code[:2])
    else:
        y = int('202'+code[:1])
    m = int(code[2:])
    #print(y,m)

    try:
        m_i = main_mouths.index(m)
    except ValueError:
        print(f'not main month({m})!!! ')
        return None, None

    if m_i == 0:
        y_start = y - 1
        pre_m = main_mouths[-1]
    else:
        y_start = y
        pre_m = main_mouths[m_i - 1]

    head_mouths = 3
    m_start = pre_m - head_mouths
    if m_start <= 0:
        y_start = y_start - 1
        m_start = m_start + 12

    if m == 1:
        y_end = y - 1
        m_end = 12
    else:
        y_end = y
        m_end = m - 1

    start_time = datetime(y_start, m_start, 15, 16, 0 ,0)
    end_time   = datetime(  y_end,   m_end, 28, 16, 0 ,0)
    print(f'**********  time range:    ({start_time}  ~~~  {end_time}) *****************')
    kd = DataDownloader(api, symbol_list=symbol, dur_sec=sec,
                        start_dt=start_time, end_dt=end_time,
                        csv_file_name=csv_file_name)

    return kd, csv_file_name

def unique_array(arr):
    return list(set(arr))

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
    codes= unique_array(codes)
    codes.sort()
    print(codes)

    name, password = get_tq(args.broker)
    from tqsdk import TqApi, TqAuth
    from tqsdk.tools import DataDownloader
    api = TqApi(auth=TqAuth(name, password))

    download_tasks = {}
    csv_files = []
    for code in codes:
        kd, csv_file_name = tq_download_his_data(api, args.product, code, args.sec)
        if not kd:
            continue
        download_tasks[code] = kd
        csv_files.append(csv_file_name)

    # 使用with closing机制确保下载完成后释放对应的资源
    with closing(api):
        while not all([v.is_finished() for v in download_tasks.values()]):
            api.wait_update()
            sys.stdout.flush()
            info = { k:("%.2f%%" % v.get_progress()) for k,v in download_tasks.items() }
            sys.stdout.write("\rprogress: %s" % info)
        sys.stdout.write('\n')

    #去除不完整日的tick
    exchange = create_exchange('kuaiqi_futures')
    for csv_file_name in csv_files:
        print('read file: ', csv_file_name)
        cost_start = datetime.now()
        df = pd.read_csv(csv_file_name)
        print('  cost: %s'%(datetime.now()-cost_start))

        df['last_time'] = df['datetime_nano'].apply(exchange.get_time_from_data_ts)
        k = df.iloc[0]
        k_time = k.last_time
        start_time = datetime(year=k_time.year, month=k_time.month, day=k_time.day,
                            hour=16, minute=0, second=0)
        df = df[df['last_time'] > start_time]
        del df['last_time']

        df.rename(columns={'datetime': 'datetime_str', 'datetime_nano': 'datetime'}, inplace=True)
        index = csv_file_name.find('_')
        prefix = csv_file_name[:index] + '.'
        df.columns = df.columns.str.replace(prefix, '')
        print(df)
        df.to_csv(csv_file_name, encoding='utf-8', index=False)


    '''
    # 使用with closing机制确保下载完成后释放对应的资源
    with closing(api):
        while not kd.is_finished(): #or not td.is_finished():
            api.wait_update()
            sys.stdout.flush()
            sys.stdout.write("\rprogress: kline: %.2f%%" % (kd.get_progress()))
    sys.stdout.write('\n')
    '''
