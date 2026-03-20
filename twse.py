#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os
import re
import json
import argparse
import datetime
import pandas as pd
import numpy as np

import xurl

# ["0證券代號","1證券名稱","2成交股數","3成交筆數","4成交金額","5開盤價","6最高價","7最低價","8收盤價","9漲跌(+/-)","10漲跌價差","11最後揭示買價","12最後揭示買量","13最後揭示賣價","14最後揭示賣量","15本益比"]
class AfterTradingInfo:
    def __init__(self, v, date):
        self.code = v[0]
        self.name = v[1]
        self.date = date
        self.volume = round(int(v[2].replace(',','')) / 1000)
        self.open = float(v[5])
        self.high = float(v[6])
        self.low = float(v[7])
        self.close = float(v[8])

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
        self.chg = 0
        self.vol_pct = 0
        self.nav = 0
        self.nav_date = None
        self.nav_time = None

        if msg:
            self.code = msg['c']
            self.name = msg['n']
            self.date = msg['d']
            for attr in ['v', 'o', 'h', 'l', 'z', 'y']:
                if msg[attr] != '-':
                    setattr(self, attr, float(msg[attr]))
            if self.z == 0:
                for b in msg['b'].split('_'):
                    if b != '-' and float(b) != 0:
                        self.z = float(b)
                        break
            if self.z == 0:
                self.z = self.y
            if self.l:
                self.z = max(self.l, self.z)
            if self.h:
                self.z = min(self.h, self.z)

        if trading:
            self.code = trading.code
            self.name = trading.name
            self.v = trading.volume
            self.o = trading.open
            self.h = trading.high
            self.l = trading.low
            self.z = trading.close

class HistoryInfo:
    def __init__(self):
        self.close = []
        self.volume = []

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

def get_msg(codes):
    step = 50
    result = []
    idx = 0
    while idx < len(codes):
        count = min(len(codes) - idx, step)
        ex_ch = '|'.join([get_ex_ch_by_code(x) for x in codes[idx:idx+count]])
        url = 'https://mis.twse.com.tw/stock/api/getStockInfo.jsp?ex_ch=%s&json=1&delay=0' %(ex_ch)
        txt = xurl.load(url, cache=False)
        data = json.loads(txt)
        if 'msgArray' in data:
            result.extend(data['msgArray'])
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

def get_etf_infos():
    url = 'https://mis.twse.com.tw/stock/data/all_etf.txt'
    txt = xurl.load(url, cache=False)
    data = json.loads(txt)
    return data

def update_nav(infos):
    etf_infos = get_etf_infos()
    for x in infos:
        msg = get_etf_msg(etf_infos, x.code)
        if msg:
            nav = msg['f']
            if isinstance(nav, float):
                x.nav = nav
            elif isinstance(nav, str) and not nav.startswith('-'):
                x.nav = float(nav)
            x.nav_date = msg['i']
            x.nav_time = msg['j']

def get_tse_objs(code, year, month, verbose):
    data = []
    today = datetime.date.today()
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
    today = datetime.date.today()
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
        start = datetime.datetime.strptime(start, '%Y%m%d').date()
    if isinstance(end, str):
        end = datetime.datetime.strptime(end, '%Y%m%d').date()
    idx_s = start.year * 12 + start.month - 1
    idx = end.year * 12 + end.month - 1
    while idx >= idx_s:
        y = int(idx / 12)
        m = (idx % 12) + 1
        objs = get_objs(code, y, m, verbose)
        if len(objs) == 0:
            if verbose:
                print('{}{:02d} not found'.format(y, m))
            break
        data = objs + data
        idx -= 1

    return data

def get_data_by_days(code, days, verbose=False):
    data = []
    end = datetime.date.today()
    idx = end.year * 12 + end.month - 1
    while len(data) < days:
        y = int(idx / 12)
        m = (idx % 12) + 1
        objs = get_objs(code, y, m, verbose)
        if len(objs) == 0:
            if verbose:
                print('{}{:02d} not found'.format(y, m))
            break
        data = objs + data
        idx -= 1

    return data

def analyze(date, days=30, verbose=False):

    if isinstance(date, str):
        date = datetime.datetime.strptime(date, '%Y%m%d').date()

    is_realtime = date == datetime.date.today()

    trading_objs = [];
    while len(trading_objs) < (days + 1):
        url = 'https://www.twse.com.tw/rwd/zh/afterTrading/MI_INDEX?date={}&type=0099P&response=json'.format(date.strftime('%Y%m%d'))
        json_txt = xurl.load(url, verbose=verbose, cacheOnly=not is_realtime)
        try:
            json_obj = json.loads(json_txt)
        except ValueError as e:
            break
        try:
            if 'stat' in json_obj and json_obj['stat'] == 'OK' and len(json_obj['tables'][8]['data']) > 0:
                objs = []
                for d in json_obj['tables'][8]['data']:
                    if d[5] != '--':
                        objs.append(AfterTradingInfo(d, date.strftime('%Y%m%d')))
                trading_objs.append(objs)
        except ValueError as e:
            break
        date = date - datetime.timedelta(days=1)

    if (len(trading_objs) < 2):
        return None

    parsed = {}
    for x in trading_objs[0]:
        parsed[x.code] = HistoryInfo()

    infos = []
    if is_realtime:
        codes = [x.code for x in trading_objs[0]]
        msg = get_msg(codes)
        infos = [StockInfo(msg=x) for x in msg]
        if infos[0].date == trading_objs[0][0].date:
            trading_objs = trading_objs[1:]
    else:
        infos = [StockInfo(trading=x) for x in trading_objs[0]]
        trading_objs = trading_objs[1:]

    for trading in trading_objs:
        for x in trading:
            if x.code in parsed:
                parsed[x.code].close.append(x.close)
                parsed[x.code].volume.append(x.volume)

    for x in infos:
        if len(parsed[x.code].close):
            x.chg = x.z - parsed[x.code].close[0];
        avg = np.mean(parsed[x.code].volume)
        if avg > 0:
            x.vol_pct = np.round(x.v / avg * 100, 2)

    update_nav(infos)

    df = pd.DataFrame([x.__dict__ for x in infos])
    return df

def main():

    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--days', type=int, default=30)
    parser.add_argument('-v', '--verbose', action="store_true")
    args, unparsed = parser.parse_known_args()

    date = unparsed[0] if len(unparsed) > 0 else datetime.date.today()
    analyze(date, args.days, args.verbose);

    return

if __name__ == '__main__':
    main()
