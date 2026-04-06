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

split_stocks = {
    '0050': {'date':20250618, 'rate':4},
    '00631L': {'date':20260331, 'rate':22},
    '00663L': {'date':20250611, 'rate':7},
}

parsed_name = {}

# "0證券代號","1證券名稱","2成交股數","3成交筆數","4成交金額","5開盤價",
# "6最高價","7最低價","8收盤價","9漲跌(+/-)","10漲跌價差","11最後揭示買價",
# "12最後揭示買量","13最後揭示賣價","14最後揭示賣量","15本益比"
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
        if self.code in split_stocks:
            apply_split(self.code, self)

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
        self.ma = 0
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

class HistoryInfo:
    def __init__(self):
        self.close = []
        self.volume = []

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

def get_name(code):
    if code in parsed_name:
        return parsed_name[code]
    tse_output = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'jsons/tse-code-list.json')
    otc_output = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'jsons/otc-code-list.json')
    data = {'TSE':tse_output, 'OTC':otc_output}
    ex, name = None, None
    for k, v in data.items():
        with open(v, 'r') as f:
            data = json.load(f)
            if code in data:
                ex, name = k, data[code]
                break
    parsed_name[code] = (ex, name)
    return parsed_name[code]

def get_ex_code(code):
    ex, name = get_name(code)
    assert ex, 'ERROR: ' + code
    return '{}_{}.tw'.format(ex.lower(), code)

def get_msg(codes):
    step = 25
    result = []
    idx = 0
    while idx < len(codes):
        count = min(len(codes) - idx, step)
        ex_ch = '|'.join([get_ex_code(x) for x in codes[idx:idx+count]])
        url = 'https://mis.twse.com.tw/stock/api/getStockInfo.jsp?ex_ch=%s&json=1&delay=0' %(ex_ch)
        txt = xurl.load(url, cache=False)
        data = json.loads(txt)
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
    txt = xurl.load(url, cache=False)
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

def get_tse_month_data(code, year, month, cache, cacheOnly, verbose):
    data = []
    url = 'http://www.twse.com.tw/exchangeReport/STOCK_DAY?response=json&date={}{:02}01&stockNo={}'.format(year, month, code)
    json_txt = xurl.load(url, cache=cache, cacheOnly=cacheOnly, verbose=verbose)
    try:
        json_obj = json.loads(json_txt)
    except ValueError as e:
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

def get_otc_month_data(code, year, month, cache, cacheOnly, verbose):
    data = []
    url = 'https://www.tpex.org.tw/www/zh-tw/afterTrading/tradingStock?code={}&date={}%2F{:02d}%2F{:02d}&id=&response=json'.format(code, year, month, 1)
    json_txt = xurl.load(url, cache=cache, cacheOnly=cacheOnly, verbose=verbose)
    try:
        json_obj = json.loads(json_txt)
    except ValueError as e:
        return []
    # fields":["日期","成交張數","成交仟元","開盤","最高","最低","收盤","筆數"]
    if 'tables' in json_obj and 'data' in json_obj['tables'][0]:
        for d in json_obj['tables'][0]['data']:
            if d[1] != '0' and d[6] != '--':
                d = [x.replace(',', '') for x in d]
                data.append({'date':convert_date(d[0]), 'open':d[3], 'high':d[4], 'low':d[5], 'close':d[6], 'volume':d[1]})
    return data

def get_month_data(code, year, month, verbose):
    today = datetime.date.today()
    cache = True
    cacheOnly = (year != today.year or month != today.month)
    ex, name = get_name(code)
    assert ex, 'ERROR: ' + code
    func = get_otc_month_data if ex == 'OTC' else get_tse_month_data
    data = func(code, year, month, cache, cacheOnly, verbose)
    if len(data) == 0 and cacheOnly == False:
        data = func(code, year, month, False, False, verbose)
    return data

def get_data(code, start, end, verbose=False):
    data = []
    fail = 0
    if isinstance(start, str):
        start = datetime.datetime.strptime(start, '%Y%m%d').date()
    if isinstance(end, str):
        end = datetime.datetime.strptime(end, '%Y%m%d').date()
    idx_s = start.year * 12 + start.month - 1
    idx = end.year * 12 + end.month - 1
    while idx >= idx_s and fail < 2:
        y = int(idx / 12)
        m = (idx % 12) + 1
        d = get_month_data(code, y, m, verbose)
        if len(d) == 0:
            fail += 1
        data = d + data
        idx -= 1

    return data

def get_data_by_days(code, days, verbose=False):
    data = []
    fail = 0
    end = datetime.date.today()
    idx = end.year * 12 + end.month - 1
    while len(data) < days and fail < 2:
        y = int(idx / 12)
        m = (idx % 12) + 1
        d = get_month_data(code, y, m, verbose)
        if len(d) == 0:
            fail += 1
        data = d + data
        idx -= 1

    return data

def analyze(date, ma_days, mv_days, pz_days, tail=1, verbose=False):

    if isinstance(date, str):
        date = datetime.datetime.strptime(date, '%Y%m%d').date()

    today = datetime.date.today()
    is_today = date == today
    today_str = today.strftime('%Y%m%d')
    has_today_data = False

    days = max(ma_days, mv_days, pz_days)
    records = [] # Ordering by "newer"
    while len(records) <= days:
        url = 'https://www.twse.com.tw/rwd/zh/afterTrading/MI_INDEX?date={}&type=0099P&response=json'.format(date.strftime('%Y%m%d'))
        json_obj = xurl.load_json(url, verbose=verbose, cacheOnly=not is_today)
        if not json_obj:
            break
        try:
            if 'stat' in json_obj and json_obj['stat'] == 'OK' and len(json_obj['tables'][8]['data']) > 0:
                objs = []
                for d in json_obj['tables'][8]['data']:
                    if d[5] != '--':
                        objs.append(AfterTradingInfo(d, date.strftime('%Y%m%d')))
                records.append(objs)
        except ValueError as e:
            if verbose:
                print('parse failed: {}'.format(ur))
            break
        date = date - datetime.timedelta(days=1)

    if len(records) < 2:
        return None

    info = None

    if is_today and records[0][0].date != today_str:
        codes = [x.code for x in records[0]]
        msg = get_msg(codes)
        if len(msg) and msg[0]['d'] == today_str:
            info = [StockInfo(msg=x) for x in msg]

    if not info:
        info = [StockInfo(trading=x) for x in records[0]]
        records = records[1:]

    parsed = {x.code: HistoryInfo() for x in info}

    # Ordering by "newer"
    for rec in records:
        for x in rec:
            if x.code in parsed:
                parsed[x.code].close.append(x.close)
                parsed[x.code].volume.append(x.volume)

    if tail > 1:
        for x in info:
            x.z = np.round((x.z + np.sum(parsed[x.code].close[:tail - 1])) / tail, 2)
            x.v = np.round((x.v + np.sum(parsed[x.code].volume[:tail - 1])) / tail)

    for x in info:
        if len(parsed[x.code].close) and len(parsed[x.code].volume):
            x.y = parsed[x.code].close[0]
            x.mv = int(np.mean(parsed[x.code].volume[:mv_days]))
            x.ma = np.mean(parsed[x.code].close[:ma_days])
            x.days_hi = np.max(parsed[x.code].close[:pz_days])
            x.days_lo = np.min(parsed[x.code].close[:pz_days])

    update_etf_nav(info)

    df = pd.DataFrame([x.__dict__ for x in info])
    return df

def main():

    parser = argparse.ArgumentParser()
    parser.add_argument('-v', '--verbose', action="store_true")
    args, unparsed = parser.parse_known_args()

    date = unparsed[0] if len(unparsed) > 0 else datetime.date.today()
    df = analyze(date, 60, 30, 240, 1, args.verbose)

    pd.set_option('display.max_rows', None)
    pd.set_option('display.max_columns', None)
    print(df)

    return

if __name__ == '__main__':
    main()
