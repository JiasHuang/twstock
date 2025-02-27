#!/usr/bin/python3
# -*- coding: utf-8 -*-

import re
import json
import xurl
import twse

codes = ['0050', '0056', '00646', '00661', '00762', '006206']

def parse(code):

    if code not in codes:
        return None

    url = 'https://www.yuantaetfs.com/product/detail/{}/Basic_information'.format(code)
    txt = xurl.load(url)

    for m in re.finditer('ETF 特性 (\d+)/(\d+)/(\d+)', txt):
        date = m.group(1) + m.group(2) + m.group(3)

    vals = []
    for m in re.finditer('<div class="border-bottom col-7 col-md-5 p-2 pl-3 fundData" data-v-1211c2a0>(.*?)<', txt):
        vals.append(float(m.group(1)))

    if len(vals) < 3:
        return None

    pe = vals[0]
    pb = vals[2]

    close = twse.get_close(code, date)
    eps = close / pe
    nav = close / pb

    d = {}
    d['date'] = date
    d['eps'] = eps
    d['nav'] = nav
    return d
