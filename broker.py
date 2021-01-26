#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import re
import sys
import json
import time
import datetime

from optparse import OptionParser

import xurl

class broker:
    codemap = {'1360':'港商麥格理','1380':'台灣匯立','1440':'美林','1470':'台灣摩根','1480':'美商高盛','1520':'瑞士信貸','1560':'港商野村','1570':'港商法國興業','1590':'花旗環球','1650':'新加坡商瑞銀','8440':'摩根大通','8890':'大和國泰','8900':'法銀巴黎','8960':'香港上海匯豐'}

class track:
    def __init__(self, date, b_qty, b_pz, s_qty, s_pz):
        self.date = date.replace('/','')
        self.b_qty = int(b_qty.replace(',',''))
        self.b_pz = float(b_pz)
        self.s_qty = int(s_qty.replace(',',''))
        self.s_pz = float(s_pz)
    def show(self):
        print('{0.date} {0.b_qty:+8} {0.b_pz:8.2f} | {1:+8} {0.s_pz:8.2f}'.format(self, -x.s_qty))

def trace_broker(broker, stock, pr_lines):
    vec = []
    url = 'https://histock.tw/stock/brokertrace.aspx?bno={b}&no={s}'.format(b=broker, s=stock)
    txt = xurl.load(url, verbose=False)
    for m in re.finditer(r'<td>(.*?)</td><td>([\d|,]+)</td><td>(\d+[.]\d*)</td><td>([\d|,]+)</td><td>(\d+[.]\d*)</td>', txt):
        vec.append(track(m.group(1), m.group(2), m.group(3), m.group(4), m.group(5)))
    qty = 0
    cost = 0
    avg = 0
    idx_range = None
    if pr_lines:
        idx_range = len(vec) - int(pr_lines)
    for idx, x in enumerate(sorted(vec, key=lambda x: x.date)):
        qty += x.b_qty - x.s_qty;
        if qty > 0:
            cost = (cost + x.b_qty * x.b_pz) / (qty + x.s_qty) * qty
            avg = cost / qty
        else:
            qty = cost = avg = 0
        text = ['-', '-']
        if x.b_qty:
            text[0] = '{0:+8} {1:8.2f}'.format(x.b_qty, x.b_pz)
        if x.s_qty:
            text[1] = '{0:+8} {1:8.2f}'.format(-x.s_qty, x.s_pz)
        if not pr_lines or idx >= idx_range:
            print('{} | {:>17s} | {:>17s} | {:+8,} | qty {:10,} | avg {:8.2f}'.format(x.date, text[0], text[1], x.b_qty - x.s_qty, qty, avg))
    return

def main():
    parser = OptionParser()
    parser.add_option("-b", "--broker", dest="broker", action="append")
    parser.add_option("-s", "--stock", dest="stock")
    parser.add_option("-l", "--lines", dest="lines")
    (options, args) = parser.parse_args()
    brokers = options.broker or broker.codemap.keys()
    divider = '-' * 36
    for b in brokers:
        n = b
        if b in broker.codemap:
            n += ' ' + broker.codemap[b]
        print('{d} {n:^20} {d}'.format(d=divider, n=n))
        trace_broker(b, options.stock, options.lines)
    return

if __name__ == '__main__':
    main()
