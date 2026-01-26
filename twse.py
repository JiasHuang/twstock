#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os
import re
import json
import xurl
from datetime import datetime
from dateutil.relativedelta import relativedelta

def from_common_era(x):
    v = int(x) - 1911
    return v

def to_common_era(x):
    v = int(x)
    if v < 1911:
        v += 1911
    return v

def convert_date(s):
    return re.sub('(\d+)/(\d+)/(\d+)', lambda y: str(int(y.group(1)) + 1911) + y.group(2) + y.group(3), s)

def get_ex_ch_by_code(code):
    local = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'tse-code-list.txt')
    with open(local) as fd:
        for line in fd.readlines():
            if line.rstrip() == code:
                return 'tse_%s.tw' %(code)
    local = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'otc-code-list.txt')
    with open(local) as fd:
        for line in fd.readlines():
            if line.rstrip() == code:
                return 'otc_%s.tw' %(code)
    return None


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

def get_data(code, start='20200101'):
    today = datetime.today().date()
    date = datetime.strptime(start, '%Y%m%d').date()
    data = []
    while date <= today:
        url = 'http://www.twse.com.tw/exchangeReport/STOCK_DAY?response=json&date={}&stockNo={}'.format(date.strftime('%Y%m%d'), code)
        json_txt = xurl.load(url, verbose=True)
        json_obj = json.loads(json_txt)
        # fields":["日期","成交股數","成交金額","開盤價","最高價","最低價","收盤價","漲跌價差","成交筆數"]
        if 'data' in json_obj:
            for d in json_obj['data']:
                if d[1] != '0':
                    d = [x.replace(',', '') for x in d]
                    data.append({'date':convert_date(d[0]), 'open':d[3], 'high':d[4], 'low':d[5], 'close':d[6], 'volume':d[1]})
        date = date + relativedelta(months=+1)
    return data

