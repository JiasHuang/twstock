#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os
import re
import json
import argparse
import datetime
import calendar
import pandas as pd
import numpy as np

import yfin
import xurl

split_stocks = {
    '0050': {'date':20250618, 'rate':4},
    '00631L': {'date':20260331, 'rate':22},
    '00663L': {'date':20250611, 'rate':7},
}

parsed_name = {}

class StockInfo:
    def __init__(self, msg=None, trading=None):
        self.code = None
        self.name = None
        self.date = None
        self.o = 0
        self.h = 0
        self.l = 0
        self.z = 0
        self.v = 0
        self.y = 0
        self.mv = 0
        self.ma20 = 0
        self.ma60 = 0
        self.nav = 0
        self.nav_date = None
        self.nav_time = None
        self.days_hi = 0
        self.days_lo = 0

        if msg:
            self.code = msg['c']
            self.name = msg['n']
            self.date = msg['d']
            for attr in ['o', 'h', 'l', 'z', 'y']:
                if attr in msg and msg[attr] != '-':
                    setattr(self, attr, float(msg[attr]))
            for attr in ['v']:
                if attr in msg and msg[attr] != '-':
                    setattr(self, attr, int(msg[attr]))
            if self.z == 0 and self.v == 0:
                self.z = self.y
            if self.z == 0 and 'b' in msg:
                for b in msg['b'].split('_'):
                    if b != '-' and float(b) != 0:
                        self.z = float(b)
                        break
            if self.l > 0:
                self.z = max(self.l, self.z)
            if self.h > 0:
                self.z = min(self.h, self.z)

        if trading:
            self.code = trading.code
            self.name = trading.name
            self.date = trading.date
            self.v = trading.volume
            self.o = trading.open
            self.h = trading.high
            self.l = trading.low
            self.z = trading.close

def apply_split(code, data):
    date = split_stocks[code]['date']
    rate = split_stocks[code]['rate']
    if isinstance(data, dict):
        if int(data['date']) < date:
            for attr in ['open', 'high', 'low', 'close']:
                val = float(data[attr])
                data[attr] = round(val / rate, 2)
            for attr in ['volume']:
                val = int(data[attr])
                data[attr] = val * rate
    else:
        if int(data.date) < date:
            for attr in ['open', 'high', 'low', 'close']:
                val = float(getattr(data, attr))
                setattr(data, attr, round(val / rate, 2))
            for attr in ['volume']:
                val = int(getattr(data, attr))
                setattr(data, attr, val * rate)

def from_common_era(x):
    v = int(x) - 1911
    return v

def to_common_era(x):
    v = int(x)
    if v < 1911:
        v += 1911
    return v

def convert_date(s):
    m = re.search(r'(\d+)/(\d+)/(\d+)', s)
    return str(to_common_era(m.group(1))) + m.group(2) + m.group(3)

def get_ex_name(code):
    if code in parsed_name:
        return parsed_name[code]
    tse_output = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'jsons/tse-code-list.json')
    otc_output = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'jsons/otc-code-list.json')
    data = {'TSE':tse_output, 'OTC':otc_output}
    ex, name = None, ''
    for k, v in data.items():
        with open(v, 'r') as f:
            data = json.load(f)
            if code in data:
                ex, name = k, data[code]
                break
    parsed_name[code] = (ex, name)
    return parsed_name[code]

def get_name(code):
    ex, name = get_ex_name(code)
    return name

def get_ex_code(code):
    ex, name = get_ex_name(code)
    assert ex, 'ERROR: ' + code
    return '{}_{}.tw'.format(ex.lower(), code)

def get_msg(codes):
    step = 25
    result = []
    idx = 0
    now_time = datetime.datetime.now().time()
    cache = now_time < datetime.time(9, 0) or now_time > datetime.time(13, 30)
    while idx < len(codes):
        count = min(len(codes) - idx, step)
        ex_ch = '|'.join([get_ex_code(x) for x in codes[idx:idx+count]])
        url = 'https://mis.twse.com.tw/stock/api/getStockInfo.jsp?ex_ch=%s&json=1&delay=0' %(ex_ch)
        data = xurl.load_json(url, cache=cache)
        if data:
            for msg in data.get('msgArray', []):
                if all(key in msg for key in ['c', 'n', 'd']):
                    result.append(msg)
        idx += count
    return result

def get_etf_msg(data, code):
    if 'a1' not in data:
        return None
    for a1 in data['a1']:
        if 'msgArray' in a1:
            for msg in a1['msgArray']:
                if msg['a'] == code:
                    return msg
    return None

def update_etf_nav(infos):
    url = 'https://mis.twse.com.tw/stock/data/all_etf.txt'
    now_time = datetime.datetime.now().time()
    cache = now_time < datetime.time(8, 0) or now_time > datetime.time(15, 30)
    txt = xurl.load(url, cache=cache)
    data = json.loads(txt)
    parsed = {x.code:x for x in infos}
    for a1 in data.get('a1', []):
        for msg in a1.get('msgArray', []):
            code = msg['a']
            if code in parsed:
                info = parsed[code]
                nav = msg['f']
                if isinstance(nav, float):
                    info.nav = nav
                elif isinstance(nav, str) and not nav.startswith('-'):
                    info.nav = float(nav)
                info.nav_date = msg['i']
                info.nav_time = msg['j']
    return True

def get_tse_month_data(code, year, month, cache, cacheOnly):
    data = []
    url = 'http://www.twse.com.tw/exchangeReport/STOCK_DAY?response=json&date={}{:02}01&stockNo={}'.format(year, month, code)
    json_obj = xurl.load_json(url, cache=cache, cacheOnly=cacheOnly)
    if not json_obj:
        return []
    # fields":["日期","成交股數","成交金額","開盤價","最高價","最低價","收盤價","漲跌價差","成交筆數"]
    if 'data' in json_obj:
        for d in json_obj['data']:
            if d[1] != '0' and d[6] != '--':
                d = [x.replace(',', '') for x in d]
                v = round(int(d[1]) / 1000)
                data.append({'date':convert_date(d[0]), 'open':d[3], 'high':d[4], 'low':d[5], 'close':d[6], 'volume':str(v)})
                if code in split_stocks:
                    apply_split(code, data[-1])
    return data

def get_otc_month_data(code, year, month, cache, cacheOnly):
    data = []
    url = 'https://www.tpex.org.tw/www/zh-tw/afterTrading/tradingStock?code={}&date={}%2F{:02d}%2F{:02d}&id=&response=json'.format(code, year, month, 1)
    json_obj = xurl.load_json(url, cache=cache, cacheOnly=cacheOnly)
    if not json_obj:
        return []
    # fields":["日期","成交張數","成交仟元","開盤","最高","最低","收盤","筆數"]
    if 'tables' in json_obj and 'data' in json_obj['tables'][0]:
        for d in json_obj['tables'][0]['data']:
            if d[1] != '0' and d[6] != '--':
                d = [x.replace(',', '') for x in d]
                data.append({'date':convert_date(d[0]), 'open':d[3], 'high':d[4], 'low':d[5], 'close':d[6], 'volume':d[1]})
    return data

def get_month_data(ex, code, year, month):
    today = datetime.date.today()
    cache = True
    cacheOnly = (year != today.year or month != today.month)
    if ex == 'TSE':
        return get_tse_month_data(code, year, month, cache, cacheOnly)
    if ex == 'OTC':
        return get_otc_month_data(code, year, month, cache, cacheOnly)
    return []

def get_data(code, start, end):
    data = []
    fail = 0
    ex, name = get_ex_name(code)
    if isinstance(start, str):
        start = datetime.datetime.strptime(start, '%Y%m%d')
    if isinstance(end, str):
        end = datetime.datetime.strptime(end, '%Y%m%d')

    if ex == 'TSE':
        return yfin.get_data(code, start, end)

    idx_s = start.year * 12 + start.month - 1
    idx = end.year * 12 + end.month - 1
    while idx >= idx_s and fail < 2:
        y = int(idx / 12)
        m = (idx % 12) + 1
        d = get_month_data(ex, code, y, m)
        if len(d) == 0:
            fail += 1
        data = d + data
        idx -= 1

    return data

def main():

    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--code', default='0050')
    parser.add_argument('-v', '--verbose', action="store_true", default=False)
    args, unparsed = parser.parse_known_args()

    xurl.set_verbose(args.verbose)

    code = unparsed[0] if unparsed else args.code
    objs = get_data(code, '20260101', '20260430')
    for obj in objs:
        print(obj)

    return

if __name__ == '__main__':
    main()
