#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import re
import sys
import json
import time
import datetime

from optparse import OptionParser

class trader:
    def __init__(self, code):
        self.code = code
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
        print('%s: 買%s $%.2f 賣%s $%.2f (%s)' %(self.code[4:], '{:,}'.format(self.buy_qty), self.buy_avg, '{:,}'.format(self.sell_qty), self.sell_avg, '{:,}'.format(self.buy_qty - self.sell_qty)))

def parse_csv(local):
    vec = []
    curr = None
    fd = open(local)
    lines = fd.readlines()
    for l in lines[4:]:
        m = re.search(r'^\d+,([^,]+),([0-9.]+),([0-9.]+),([0-9.]+)', l)
        if m:
            code = m.group(1)
            pz = float(m.group(2))
            buy_qty = int(m.group(3)) / 1000
            sell_qty = int(m.group(4)) / 1000
            if not curr or curr.code != code:
                curr = trader(code)
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

    # top10 buy
    print('\n' + '-' * 20 + ' 買張 TOP10 ' + '-' * 20)
    for x in sorted(vec, key=lambda x: x.buy_qty, reverse=True)[:10]:
        x.show()

    # top10 sell
    print('\n' + '-' * 20 + ' 賣張 TOP10 ' + '-' * 20)
    for x in sorted(vec, key=lambda x: x.sell_qty, reverse=True)[:10]:
        x.show()

    # top10 sell + buy
    print('\n' + '-' * 20 + ' 張數 TOP10 ' + '-' * 20)
    for x in sorted(vec, key=lambda x: x.sell_qty + x.buy_qty, reverse=True)[:10]:
        x.show()

    # top10 buy - sell
    print('\n' + '-' * 20 + ' 買超 TOP10 ' + '-' * 20)
    for x in sorted(vec, key=lambda x: x.buy_qty - x.sell_qty, reverse=True)[:10]:
        x.show()

    # top10 sell - buy
    print('\n' + '-' * 20 + ' 賣超 TOP10 ' + '-' * 20)
    for x in sorted(vec, key=lambda x: x.sell_qty - x.buy_qty, reverse=True)[:10]:
        x.show()

    return

def main():
    parser = OptionParser()
    parser.add_option("-i", "--input", dest="input")
    (options, args) = parser.parse_args()
    orig = options.input or args[0]
    local = orig + '.utf8'
    os.system('iconv -f big5 -t utf8 -c %s > %s' %(orig, local))
    os.system('sed -i \'s/,,/\\n/g\' %s' %(local))
    parse_csv(local)
    return

if __name__ == '__main__':
    main()
