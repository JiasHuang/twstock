#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os
import re
import json
import xurl

def convert_date(s):
    return re.sub('(\d+)/(\d+)/(\d+)', lambda y: str(int(y.group(1)) + 1911) + y.group(2) + y.group(3), s)

def get_ex_ch_by_code(code):
    local = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'otc-code-list.txt')
    with open(local) as fd:
        for line in fd.readlines():
            if line.rstrip() == code:
                return 'otc_%s.tw' %(code)
    return 'tse_%s.tw' %(code)

def get_close(code, date):
    url = 'http://www.twse.com.tw/exchangeReport/STOCK_DAY?response=json&date={}&stockNo={}'.format(date, code)
    json_txt = xurl.load(url)
    json_obj = json.loads(json_txt)
    close = 0
    # fields":["日期","成交股數","成交金額","開盤價","最高價","最低價","收盤價","漲跌價差","成交筆數"]
    for d in json_obj['data']:
        d0 = convert_date(d[0])
        if d0 == date:
            close = float(d[6])
            break
    return close

def get_stock_info(code):
    ex_ch = get_ex_ch_by_code(code)
    url = 'https://mis.twse.com.tw/stock/api/getStockInfo.jsp?ex_ch={}&json=1&delay=0'.format(ex_ch)
    json_txt = xurl.load(url)
    json_obj = json.loads(json_txt)
    msg = json_obj['msgArray'][0]
    price = msg['z']

    if price == '-':
        price = msg['y']

    msg['price'] = float(price)

    return msg