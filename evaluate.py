#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os
import argparse
import datetime
import google_finance_csv

class Stock:
    def __init__(self, exchange, code):
        self.exchange = exchange
        self.code = code
        self.cost = 0
        self.qty = 0
        self.avg = 0

    def add_cost(self, pz, cost):
        self.cost += cost
        self.qty += cost / pz
        self.avg = self.cost / self.qty

    def get_price(self, date):
        return google_finance_csv.get_price(self.exchange, self.code, date)

    def get_sma(self, date, days):
        return google_finance_csv.get_sma(self.exchange, self.code, date, days)

    def get_gain(self, pz):
        if not self.cost:
            return (0, 0)
        gain = pz * self.qty - self.cost
        gain_percent = gain / self.cost
        return (gain, gain_percent)

def main():

    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--code', default='0050')
    parser.add_argument('-C', '--code2', default='00631L')
    parser.add_argument('-s', '--start', default='20200101')
    parser.add_argument('-e', '--end', default='20251231')
    parser.add_argument('-u', '--unit', type=int, default=1000)
    parser.add_argument('-d', '--day', type=int, default=15)
    parser.add_argument('-S', '--sma_days', type=int, default=60)
    parser.add_argument('-p', '--policy', type=int, default=0)
    args, unparsed = parser.parse_known_args()

    stock1 = Stock('TPE', args.code)
    stock2 = Stock('TPE', args.code2)

    if len(args.start) == 4:
        args.start = args.start + '0101'
    elif len(args.start) == 6:
        args.start = args.start + '01'
    if len(args.end) == 4:
        args.end = args.end + '1231'
    elif len(args.end) == 6:
        args.end = args.end + '31'

    start = datetime.datetime.strptime(args.start, '%Y%m%d').date()
    end = datetime.datetime.strptime(args.end, '%Y%m%d').date()

    for y in range(start.year, end.year + 1):
        mstart = 1
        if y == start.year:
            mstart = start.month if start.day <= args.day else start.month + 1
        for m in range(mstart, 13):
            d = datetime.date(y, m, args.day)
            pz = stock1.get_price(d)
            if not pz:
                continue

            pz2 = stock2.get_price(d)
            if pz2:
                sma2 = stock2.get_sma(d, args.sma_days)
                if args.policy == 2 or (args.policy == 0 and (sma2/pz2) >= 1.1):
                    cost2 = int(args.unit * sma2 / pz2) if (sma2/pz2) >= 1.1 else args.unit
                    stock2.add_cost(pz2, cost2)
                    gain2 = pz2 / stock2.avg - 1
                    print('{}: pz2 {} sma2 {:.2f} cost2 {} qty2 {:.2f} avg {:.2f} gain {:.2%}'.format(d, pz2, sma2, cost2, stock2.qty, stock2.avg, gain2))
                    continue

            sma = stock1.get_sma(d, args.sma_days)
            cost = int(args.unit * sma / pz) if (sma/pz) >= 1.1 else args.unit
            stock1.add_cost(pz, cost)
            gain = pz / stock1.avg - 1
            print('{}: pz {} sma {:.2f} cost {} qty {:.2f} avg {:.2f} gain {:.2%}'.format(d, pz, sma, cost, stock1.qty, stock1.avg, gain))

    pz = stock1.get_price(datetime.date.today())
    gain, gain_percent = stock1.get_gain(pz)

    pz2 = stock2.get_price(datetime.date.today())
    gain2, gain2_percent = stock2.get_gain(pz2)

    print('\n---')
    print('{}:{} cost {} qty {:.2f} avg {:.2f} gain {:.2f} ({:.2%})'.format(stock1.exchange, stock1.code, stock1.cost, stock1.qty, stock1.avg, gain, gain_percent))
    print('{}:{} cost {} qty {:.2f} avg {:.2f} gain {:.2f} ({:.2%})'.format(stock2.exchange, stock2.code, stock2.cost, stock2.qty, stock2.avg, gain2, gain2_percent))
    print('total gain {:.2f} ({:.2%})'.format(gain + gain2, (gain + gain2) / (stock1.cost + stock2.cost)))

    return

if __name__ == '__main__':
    main()
