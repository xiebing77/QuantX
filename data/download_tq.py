import argparse
from datetime import datetime
from dateutil.relativedelta import relativedelta
from contextlib import closing
from tqsdk import TqApi, TqAuth
from tqsdk.tools import DataDownloader

symtem_start_dt = datetime(2016, 1, 1, 6, 0, 0)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='klines print or check')
    parser.add_argument('-product', required=True, help='')
    parser.add_argument('-window', help='')
    parser.add_argument('-date', required=True, help='')
    args = parser.parse_args()

    d = args.date
    month_window = int(args.window)
    symbol = args.product + d

    year = 2000 + int(d[:2])
    month = int(d[2:])
    end_dt   = datetime(year, month, 1, 0, 0, 0)
    start_dt = end_dt - relativedelta(months=month_window)
    if start_dt < symtem_start_dt:
        start_dt = symtem_start_dt
    print('{}  {} ~ {} '.format(symbol, start_dt, end_dt))

    api = TqApi(auth=TqAuth("xx2022", "2Fq.YNGZ9.w.JZF"))
    kd = DataDownloader(api, symbol_list=symbol, dur_sec=300,
                        start_dt=start_dt, end_dt=end_dt,
                        csv_file_name=symbol+".csv")

    # 使用with closing机制确保下载完成后释放对应的资源
    with closing(api):
        while not kd.is_finished(): #or not td.is_finished():
            api.wait_update()
            print("progress: kline: %.2f%%" % (kd.get_progress()))