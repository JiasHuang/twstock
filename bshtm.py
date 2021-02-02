#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import re
import glob
import time

from optparse import OptionParser

class defs:
    db_location = '/home/rd/Downloads/*/*.csv'

class broker:
    foreign = ['1360','1380','1440','1470','1480','1520','1560','1570','1590','1650','8440','8890','8900','8960']
    def __init__(self, stockno, bno, bname):
        self.stockno = stockno
        self.bno = bno
        self.bname = bname
        self.buy_cost = 0
        self.buy_qty = 0
        self.buy_avg = 0
        self.sell_cost = 0
        self.sell_qty = 0
        self.sell_avg = 0
    def update_avg(self):
        if self.buy_qty:
            self.buy_avg = self.buy_cost / self.buy_qty
        if self.sell_qty:
            self.sell_avg = self.sell_cost / self.sell_qty
    def show(self):
        text = ['-', '-', '-']
        if self.buy_qty:
            text[0] = '{:+8,} ${:6.2f}'.format(self.buy_qty, self.buy_avg)
        if self.sell_qty:
            text[1] = '{:+8,} ${:6.2f}'.format(-self.sell_qty, self.sell_avg)
        text[2] = '{:+,}'.format(self.buy_qty - self.sell_qty)
        print('%s%s: %16s | %16s | %8s' %('  ' * (4 - len(self.bname.decode('utf8'))), self.bname, text[0], text[1], text[2]))

def get_db_files():
    files = glob.glob(defs.db_location)
    if not files:
        return []
    sorted_files = sorted(files, key=lambda x: x[-8:-4], reverse=True)
    latest_date = sorted_files[0][-8:-4]
    for idx, f in enumerate(sorted_files):
        if f[-8:-4] != latest_date:
            return sorted_files[:idx]
    return sorted_files

def parse_csv(local):
    results = []
    curr = None
    fd = open(local)
    lines = fd.readlines()
    stockno = re.search(r',="(\w{4})"', lines[1]).group(1)
    for l in lines[4:]:
        m = re.search(r'^\d+,([^,]+),([0-9.]+),([0-9.]+),([0-9.]+)', l)
        if m:
            bno = m.group(1)[:4]
            bname = m.group(1)[4:].replace(' ', '').replace('　', '')
            pz = float(m.group(2))
            buy_qty = int(m.group(3)) / 1000
            sell_qty = int(m.group(4)) / 1000
            if not curr or curr.bno != bno:
                curr = broker(stockno, bno, bname)
                results.append(curr)
            if buy_qty:
                curr.buy_qty += buy_qty
                curr.buy_cost += buy_qty * pz
            if sell_qty:
                curr.sell_qty += sell_qty
                curr.sell_cost += sell_qty * pz

    # update avg
    for x in results:
        x.update_avg()

    return results

def show_results(results):

    divider = '-' * 22;
    stockno = results[0].stockno

    # top10 buy - sell
    print('\n{d} {n} 買超 TOP10 {d}'.format(d=divider, n=stockno));
    for x in sorted(results, key=lambda x: x.buy_qty - x.sell_qty, reverse=True)[:10]:
        x.show()

    # top10 sell - buy
    print('\n{d} {n} 賣超 TOP10 {d}'.format(d=divider, n=stockno));
    for x in sorted(results, key=lambda x: x.sell_qty - x.buy_qty, reverse=True)[:10]:
        x.show()

    # foreign
    print('\n{d} {n} 外資券商買超 {d}'.format(d=divider, n=stockno));
    for x in sorted(results, key=lambda x: x.buy_qty - x.sell_qty, reverse=True):
        if x.bno in broker.foreign and x.buy_qty > x.sell_qty:
            x.show()

    print('\n{d} {n} 外資券商賣超 {d}'.format(d=divider, n=stockno));
    for x in sorted(results, key=lambda x: x.sell_qty - x.buy_qty, reverse=True):
        if x.bno in broker.foreign and x.sell_qty > x.buy_qty:
            x.show()

    total_buy_qty = 0
    total_sell_qty = 0
    foreign_qty = 0
    for x in results:
        total_buy_qty += x.buy_qty
        total_sell_qty += x.sell_qty
        if x.bno in broker.foreign:
            foreign_qty += x.buy_qty - x.sell_qty

    total_qty = max(total_buy_qty, total_sell_qty)
    print('\n{d} {n} 統計 {d}'.format(d=divider, n=stockno))
    print('成交張數 {:10,}'.format(total_qty))
    print('外資券商 {:+10,} ({:.2f}%)'.format(foreign_qty, foreign_qty * 100 / total_qty))

    return

def get_db():
    all_results = []
    os.system('%s/csv-naming.py' %(os.path.dirname(os.path.abspath(__file__))))
    for orig in get_db_files():
        local = '/tmp/bshtm_%s.utf8' %(orig.replace('/','_'))
        os.system('iconv -f big5 -t utf8 -c \'%s\' > \'%s\'' %(orig, local))
        os.system('sed -i \'s/,,/\\n/g\' \'%s\'' %(local))
        results = parse_csv(local)
        all_results.extend(results)
    return all_results

def main():
    parser = OptionParser()
    parser.add_option("-i", "--input", dest="input", action="append")
    (options, args) = parser.parse_args()
    for orig in options.input or args:
        print('\n{}'.format(orig))
        local = '/tmp/bshtm_%s.utf8' %(orig.replace('/','_'))
        os.system('iconv -f big5 -t utf8 -c \'%s\' > \'%s\'' %(orig, local))
        os.system('sed -i \'s/,,/\\n/g\' \'%s\'' %(local))
        results = parse_csv(local)
        show_results(results)
    return

if __name__ == '__main__':
    main()
