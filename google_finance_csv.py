#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os
import csv
import argparse
import datetime

cached = {}

def get_rows(exchange, code):
    path = os.path.join(exchange, code) + '.csv'
    if path not in cached:
        cached[path] = []
        with open(path, newline='') as fd:
            rows = csv.DictReader(fd)
            for row in rows:
                cached[path].append(row)
    return cached[path]

def get_sma(exchange, code, date, days):
    total = 0
    cnt = 0
    rows = get_rows(exchange, code)
    for row in reversed(rows):
        d = datetime.datetime.strptime(row['Date'], '%Y/%m/%d').date()
        if d <= date:
            total += float(row['Close'])
            cnt += 1
            if cnt >= days:
                break

    return total / cnt if cnt else 0

def get_price(exchange, code, date):
    pz = None
    rows = get_rows(exchange, code)
    for row in reversed(rows):
        d = datetime.datetime.strptime(row['Date'], '%Y/%m/%d').date()
        if d <= date:
            pz = float(row['Close'])
            break
    return pz
     
def main():

    parser = argparse.ArgumentParser()
    parser.add_argument('-e', '--exchange', default='TPE')
    parser.add_argument('-c', '--code', default='0050')
    parser.add_argument('-s', '--sma', type=int, default=90)
    parser.add_argument('-d', '--date', default='20200101')
    args, unparsed = parser.parse_known_args()

    date = datetime.datetime.strptime(args.date, '%Y%m%d').date()
    pz = get_price(args.exchange, args.code, date)
    sma = get_sma(args.exchange, args.code, date, args.sma)
    print('{}:{}: pz {}, sma {}'.format(args.exchange, args.code, pz, sma))
    return

if __name__ == '__main__':
    main()
