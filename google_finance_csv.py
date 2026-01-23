#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os
import csv
import argparse
import datetime
import pandas as pd
import numpy as np
from talib import abstract

cached = {}

class StockInfo:
    def __init__(self, date, open, high, low, close, volume):
        self.date = date
        self.open = open
        self.high = high
        self.low = low
        self.close = close
        self.volume = volume
        self.desc = []

def get_data(exchange, code):
    path = os.path.join(exchange, code) + '.csv'
    if path not in cached:
        new_names = ['date', 'open', 'high', 'low', 'close', 'volume']
        cached[path] = pd.read_csv(path, names=new_names, header=0, parse_dates=['date'])
    return cached[path]

def get_attrs(exchange, code, attr, date, days):
    vals = []
    data = get_data(exchange, code)
    for i, r in data[::-1].iterrows():
        if r['date'].date() <= date:
            vals.append(float(r[attr]))
            if len(vals) >= days:
                break
    vals.reverse()
    return vals

def get_attr(exchange, code, attr, date):
    vals = get_attrs(exchange, code, attr, date, 1)
    return vals[0] if vals else None

def get_ma(exchange, code, date, days):
    vals = get_attrs(exchange, code, "close", date, days)
    return sum(vals) / len(vals) if vals else 0

def get_infos(exchange, code, start, end, ma_list):
    infos = []
    data = get_data(exchange, code)
    for idx, row in data.iterrows():
        d = row['date'].date()
        if d < start:
            continue
        elif d > end:
            break
        else:
            infos.append(StockInfo(d, float(row['open']), float(row['high']), float(row['low']), float(row['close']), int(row['volume'])))

    df = pd.DataFrame([{'open':x.open, 'high':x.high, 'low':x.low, 'close':x.close, 'volume':x.volume} for x in infos])

    for ma in ma_list:
        result = abstract.SMA(df)
        for idx, val in enumerate(result):
            setattr(infos[idx], 'ma'+str(ma), val)

    names = ['HAMMER', 'MORNINGSTAR', 'ENGULFING', 'DOJI', 'SHOOTINGSTAR', 'EVENINGSTAR']
    for name in names:
        fun = getattr(abstract, 'CDL' + name)
        vals = fun(df)
        for idx, val in enumerate(vals):
            if val != 0:
                infos[idx].desc.append(name + '(' + str(val) + ')')

    return infos

def main():

    parser = argparse.ArgumentParser()
    parser.add_argument('-e', '--exchange', default='TPE')
    parser.add_argument('-c', '--code', default='2330')
    parser.add_argument('-a', '--ma', type=int, default=60)
    parser.add_argument('-d', '--date')
    args, unparsed = parser.parse_known_args()


    if not args.date:
        args.date = datetime.date.today().strftime('%Y%m%d')

    date = datetime.datetime.strptime(args.date, '%Y%m%d').date()
    pz = get_attr(args.exchange, args.code, 'close', date)
    ma = get_ma(args.exchange, args.code, date, args.ma)
    print('{}:{}: {} {} ma{} {:.2f}'.format(args.exchange, args.code, date, pz, args.ma, ma))

    return

if __name__ == '__main__':
    main()
