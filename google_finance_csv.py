#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os
import csv
import argparse
import datetime

cached = {}

class StockInfo:
    def __init__(self, date, open, high, low, close, volume):
        self.date = date
        self.open = open
        self.high = high
        self.low = low
        self.close = close
        self.volume = volume

class IntervalInfo:
    def __init__(self, high, low):
        self.high = high
        self.low = low

def get_rows(exchange, code):
    path = os.path.join(exchange, code) + '.csv'
    if path not in cached:
        cached[path] = []
        with open(path, newline='') as fd:
            rows = csv.DictReader(fd)
            for row in rows:
                cached[path].append(row)
    return cached[path]

def get_attrs(exchange, code, attr, date, days):
    vals = []
    rows = get_rows(exchange, code)
    for row in reversed(rows):
        d = datetime.datetime.strptime(row['Date'], '%Y/%m/%d').date()
        if d <= date:
            vals.append(float(row[attr]))
            if len(vals) >= days:
                break
    vals.reverse()
    return vals

def get_attr(exchange, code, attr, date):
    vals = get_attrs(exchange, code, attr, date, 1)
    return vals[0] if vals else None

def get_ma(exchange, code, date, days):
    vals = get_attrs(exchange, code, "Close", date, days)
    return sum(vals) / len(vals) if vals else 0

def get_mv(exchange, code, date, days):
    vals = get_attrs(exchange, code, "Volume", date, days)
    return sum(vals) / len(vals) if vals else 0

def get_infos(exchange, code, start, end, ma_list, mv_list, interval_list):
    infos = []
    rows = get_rows(exchange, code)
    len_rows = len(rows)
    for index, row in enumerate(rows):
        d = datetime.datetime.strptime(row['Date'], '%Y/%m/%d').date()
        if d < start:
            continue
        elif d > end:
            break
        else:
            info = StockInfo(d, float(row['Open']), float(row['High']), float(row['Low']), float(row['Close']), int(row['Volume']))
            for ma in ma_list:
                if index > ma:
                    vals = [float(x['Close']) for x in rows[index - ma : index]]
                    setattr(info, 'ma'+str(ma), sum(vals) / len(vals))
                else:
                    setattr(info, 'ma'+str(ma), None)
            for mv in mv_list:
                if index > mv:
                    vals = [int(x['Volume']) for x in rows[index - mv : index]]
                    setattr(info, 'mv'+str(mv), sum(vals) / len(vals))
                else:
                    setattr(info, 'mv'+str(mv), None)
            for interval in interval_list:
                if index > interval and index + interval < len_rows:
                    vals = [float(x['Close']) for x in rows[index - interval : index + interval]]
                    setattr(info, 'int'+str(interval), IntervalInfo(max(vals), min(vals)))
                else:
                    setattr(info, 'int'+str(interval), IntervalInfo(None, None))

            infos.append(info)
    return infos

def main():

    parser = argparse.ArgumentParser()
    parser.add_argument('-e', '--exchange', default='TPE')
    parser.add_argument('-c', '--code', default='0050')
    parser.add_argument('-a', '--ma', type=int, default=60)
    parser.add_argument('-v', '--mv', type=int, default=60)
    parser.add_argument('-d', '--date', default='20200101')
    args, unparsed = parser.parse_known_args()

    date = datetime.datetime.strptime(args.date, '%Y%m%d').date()
    pz = get_attr(args.exchange, args.code, 'Close', date)
    ma = get_ma(args.exchange, args.code, date, args.ma)
    mv = get_mv(args.exchange, args.code, date, args.mv)
    print('{}:{}: pz {} ma {:.2f} mv {:.2f}'.format(args.exchange, args.code, pz, ma, mv))
    return

if __name__ == '__main__':
    main()
