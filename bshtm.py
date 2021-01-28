#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import re
import sys
import json
import time
import datetime

from optparse import OptionParser

class broker:
    foreign = ['1360','1380','1440','1470','1480','1520','1560','1570','1590','1650','8440','8890','8900','8960']
    def __init__(self, code, name):
        self.code = code
        self.name = name
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
        print('%s%s: %16s | %16s | %8s' %('  ' * (4 - len(self.name.decode('utf8'))), self.name, text[0], text[1], text[2]))

def parse_csv(local):
    vec = []
    curr = None
    fd = open(local)
    lines = fd.readlines()
    stock_id = re.search(r',="(\w{4})"', lines[1]).group(1)
    for l in lines[4:]:
        m = re.search(r'^\d+,([^,]+),([0-9.]+),([0-9.]+),([0-9.]+)', l)
        if m:
            code = m.group(1)[:4]
            name = m.group(1)[4:].replace(' ', '').replace('　', '')
            pz = float(m.group(2))
            buy_qty = int(m.group(3)) / 1000
            sell_qty = int(m.group(4)) / 1000
            if not curr or curr.code != code:
                curr = broker(code, name)
                vec.append(curr)
            if buy_qty:
                curr.buy_qty += buy_qty
                curr.buy_cost += buy_qty * pz
            if sell_qty:
                curr.sell_qty += sell_qty
                curr.sell_cost += sell_qty * pz

    # update avg
    for x in vec:
        x.update_avg()

    divider = '-' * 22;

    # top10 buy - sell
    print('\n{d} {c} 買超 TOP10 {d}'.format(d=divider, c=stock_id));
    for x in sorted(vec, key=lambda x: x.buy_qty - x.sell_qty, reverse=True)[:10]:
        x.show()

    # top10 sell - buy
    print('\n{d} {c} 賣超 TOP10 {d}'.format(d=divider, c=stock_id));
    for x in sorted(vec, key=lambda x: x.sell_qty - x.buy_qty, reverse=True)[:10]:
        x.show()

    # foreign
    print('\n{d} {c} 外資券商買超 {d}'.format(d=divider, c=stock_id));
    for x in sorted(vec, key=lambda x: x.buy_qty - x.sell_qty, reverse=True):
        if x.code in broker.foreign and x.buy_qty > x.sell_qty:
            x.show()

    print('\n{d} {c} 外資券商賣超 {d}'.format(d=divider, c=stock_id));
    for x in sorted(vec, key=lambda x: x.sell_qty - x.buy_qty, reverse=True):
        if x.code in broker.foreign and x.sell_qty > x.buy_qty:
            x.show()

    total_buy_qty = 0
    total_sell_qty = 0
    foreign_qty = 0
    for x in vec:
        total_buy_qty += x.buy_qty
        total_sell_qty += x.sell_qty
        if x.code in broker.foreign:
            foreign_qty += x.buy_qty - x.sell_qty

    print('\n{d} {c} 統計 {d}'.format(d=divider, c=stock_id))
    print('成交張數 {:10,}'.format(max(total_buy_qty, total_sell_qty)))
    print('外資券商 {:+10,}'.format(foreign_qty))

    return

def main():
    parser = OptionParser()
    parser.add_option("-i", "--input", dest="input", action="append")
    (options, args) = parser.parse_args()
    for orig in options.input or args:
        print('\n{}'.format(orig))
        local = '/tmp/bshtm_%s.utf8' %(orig.replace('/','_'))
        os.system('iconv -f big5 -t utf8 -c \'%s\' > \'%s\'' %(orig, local))
        os.system('sed -i \'s/,,/\\n/g\' \'%s\'' %(local))
        parse_csv(local)
    return

if __name__ == '__main__':
    main()
