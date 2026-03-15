#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os
import re
import json
from datetime import datetime

import xurl

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

def is_otc(code):
    local = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'otc-code-list.txt')
    with open(local) as fd:
        for line in fd.readlines():
            if line.rstrip() == code:
                return True
    return False

def get_ex_ch_by_code(code):
    ex = 'otc' if is_otc(code) else 'tse'
    return '{}_{}.tw'.format(ex, code)

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

def get_tse_objs(code, year, month, verbose):
    data = []
    today = datetime.today().date()
    url = 'http://www.twse.com.tw/exchangeReport/STOCK_DAY?response=json&date={}{:02}01&stockNo={}'.format(year, month, code)
    cacheOnly = (year != today.year or month != today.month)
    json_txt = xurl.load(url, verbose=verbose, cacheOnly=cacheOnly)
    try:
        json_obj = json.loads(json_txt)
    except ValueError as e:
        return []
    # fields":["日期","成交股數","成交金額","開盤價","最高價","最低價","收盤價","漲跌價差","成交筆數"]
    if 'data' in json_obj:
        for d in json_obj['data']:
            if d[1] != '0' and d[6] != '--':
                d = [x.replace(',', '') for x in d]
                data.append({'date':convert_date(d[0]), 'open':d[3], 'high':d[4], 'low':d[5], 'close':d[6], 'volume':d[1]})
    return data

def get_otc_objs(code, year, month, verbose):
    data = []
    today = datetime.today().date()
    url = 'https://www.tpex.org.tw/www/zh-tw/afterTrading/tradingStock?code={}&date={}%2F{:02d}%2F{:02d}&id=&response=json'.format(code, year, month, 1)
    cacheOnly = (year != today.year or month != today.month)
    json_txt = xurl.load(url, verbose=verbose, cacheOnly=cacheOnly)
    try:
        json_obj = json.loads(json_txt)
    except ValueError as e:
        return []
    # fields":["日期","成交張數","成交仟元","開盤","最高","最低","收盤","筆數"]
    if 'tables' in json_obj and 'data' in json_obj['tables'][0]:
        for d in json_obj['tables'][0]['data']:
            if d[1] != '0' and d[6] != '--':
                d = [x.replace(',', '') for x in d]
                data.append({'date':convert_date(d[0]), 'open':d[3], 'high':d[4], 'low':d[5], 'close':d[6], 'volume':d[1]+'000'})
    return data


def get_objs(code, year, month, verbose):
    if is_otc(code):
        return get_otc_objs(code, year, month, verbose)
    return get_tse_objs(code, year, month, verbose)

def get_data(code, start, end, verbose=False):
    data = []
    if isinstance(start, str):
        start = datetime.strptime(start, '%Y%m%d').date()
    if isinstance(end, str):
        end = datetime.strptime(end, '%Y%m%d').date()
    idx_s = start.year * 12 + start.month - 1
    idx = end.year * 12 + end.month - 1
    while idx >= idx_s:
        y = int(idx / 12)
        m = (idx % 12) + 1
        objs = get_objs(code, y, m, verbose)
        if len(objs) == 0:
            break
        data = objs + data
        idx -= 1

    return data

def get_data_by_days(code, days, verbose=False):
    data = []
    end = datetime.today().date()
    idx = end.year * 12 + end.month - 1
    while len(data) < days:
        y = int(idx / 12)
        m = (idx % 12) + 1
        objs = get_objs(code, y, m, verbose)
        if len(objs) == 0:
            break
        data = objs + data
        idx -= 1

    return data
