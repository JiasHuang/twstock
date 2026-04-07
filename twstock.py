#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os
import re
import json
import argparse
import datetime
import pandas as pd
import numpy as np

import quote
import twse
import xurl

from optparse import OptionParser

class defs:
    from_year_offset = 5

class exchange_rate_info:
    def __init__(self, currency, buy_spot, sell_spot, flts):
        self.currency = currency
        self.buy_spot = buy_spot
        self.sell_spot = sell_spot
        self.flts = flts

class revenue_info:
    def __init__(self, Y, M, rev=0):
        self.Y = twse.to_common_era(Y)
        self.M = int(M)
        self.rev = rev

    def __str__(self):
        return 'Y {} M {} rev {}'.format(self.Y, self.M, self.rev)

    def __jsonencode__(self):
        return {'Y':self.Y, 'M':self.M, 'rev':self.rev}

class eps_info:
    def __init__(self, Y, Q, rev='-', gross='', profit='-', nor='-', ni='-', eps='-'):
        self.Y = twse.to_common_era(Y)
        self.Q = int(Q)
        self.rev = rev  # 營業收入
        self.gross = gross # 營業毛利
        self.profit = profit # 營業利益
        self.nor = nor # Total Non-operating Revenue 業外收支
        self.ni = ni # Net Income 稅後淨利
        self.eps = eps

    def __str__(self):
        return 'Y {} Q {} rev {} profit {} nor {} ni {} eps {}'.format(self.Y, self.Q, self.rev, self.profit, self.nor, self.ni, self.eps)

    def __jsonencode__(self):
        return {'Y':self.Y, 'Q':self.Q, 'rev':self.rev, 'gross':self.gross, 'profit':self.profit, 'nor':self.nor, 'ni':self.ni, 'eps':self.eps}

class stock_report:
    def __init__(self, code):
        self.code = code
        ex, self.name = twse.get_name(code)
        self.eps = []
        self.revenue = []
        self.close = 0
        self.per = 0
        self.nav = 0
        self.debt_ratio = 0
        self.per_year = []
        self.per_max = []
        self.per_min = []
        self.dividend_cash = []
        self.dividend_stock = []
        self.capital_stock = 0
    def show(self):
        print('-- eps --')
        for x in self.eps:
            print(x)
        print('-- revenue --')
        for x in self.revenue:
            print(x)
        print('-- overall --')
        print(self.close)
        print(self.per)
        print(self.nav)
        print(self.per_year)
        print(self.per_max)
        print(self.per_min)
        print(self.dividend_cash)
        print(self.dividend_stock)
        print(self.capital_stock)

class MyJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if hasattr(obj, '__jsonencode__'):
            return obj.__jsonencode__()
        return json.JSONEncoder.default(self, obj)

def get_data(codes):
    msg = twse.get_msg(codes)
    data = [twse.StockInfo(msg=m) for m in msg]
    update_stock_stats(data)
    return data

def update_stock_stats(infos):
    ma_days = 60
    mv_days = 30
    pz_days = 240
    days = max(ma_days, mv_days, pz_days)
    for info in infos:
        code = info.code
        df = quote.get_data_by_days(code, days)
        vals = df['close'].to_numpy()
        vols = df['volume'].to_numpy()
        if len(vals) and len(vols):
            info.ma = np.round(np.mean(vals[-ma_days-1:-1]), 2) if len(vals) > ma_days else 0
            info.mv = int(np.mean(vols[-mv_days-1:-1])) if len(vols) > mv_days else 0
            info.days_hi = max(vals[max(0, len(vals)-pz_days):])
            info.days_lo = min(vals[max(0, len(vals)-pz_days):])
        else:
            info.ma, info.mv, info.days_hi, info.days_lo = 0, 0, 0, 0
    twse.update_etf_nav(infos)
    return

def get_exchange_rate_data():

    data = load_json('exr.json')
    result = []

    url = 'https://rate.bot.com.tw/xrt/flcsv/0/day'
    txt = xurl.load(url, cache=False)

    # Currency,Rate,Cash,Spot
    for exr in data:
        c = exr['currency']
        m = re.search(re.escape(c) + r',本行買入,([^,]*),([^,]*),.*?本行賣出,([^,]*),([^,]*),', txt)
        if m:
            result.append(exchange_rate_info(c, m.group(2), m.group(4), exr.get('flts', [])))

    return result

def update_stock_report_eps(obj):
    now = datetime.datetime.now()
    from_year = twse.from_common_era(now.year) - defs.from_year_offset
    url = 'https://fubon-ebrokerdj.fbs.com.tw/z/zc/zce/zce_%s.djhtm' %(obj.code)
    txt = xurl.load(url, encoding='big5_hkscs')
    # 季別,0營業收入,1營業成本,2營業毛利,3毛利率,4營業利益,5營益率,6業外收支,7稅前淨利,8稅後淨利,9EPS(元)
    for m in re.finditer(r'<td class="t3n0">(\d+)\.(\d)Q(.*?)</tr>', txt, re.MULTILINE | re.DOTALL):
        Y, Q = m.group(1), m.group(2)
        if int(Y) < from_year:
            break
        m2 = re.findall(r'>([^\n<]*)<', m.group(3))
        if len(m2) == 10:
            obj.eps.insert(0, eps_info(Y, Q, rev=m2[0], gross=m2[2], profit=m2[4], nor=m2[6], ni=m2[8], eps=m2[9]))
    return

def update_stock_report_revenue(obj):
    now = datetime.datetime.now()
    from_year = twse.from_common_era(now.year) - defs.from_year_offset
    url = 'https://fubon-ebrokerdj.fbs.com.tw/z/zc/zch/zch_%s.djhtm' %(obj.code)
    txt = xurl.load(url, encoding='big5_hkscs')
    for m in re.finditer(r'<td class="t3n0">(\d+)/(\d+)</td>(.*?)</tr>', txt, re.MULTILINE | re.DOTALL):
        Y, M = m.group(1), m.group(2)
        if int(Y) < from_year:
            break
        m2 = re.findall(r'>([^<]+)</td>', m.group(3))
        if len(m2) > 0:
            obj.revenue.insert(0, revenue_info(Y, M, m2[0].replace(',','')))
    return

def update_stock_report_overall(obj):
    url = 'https://fubon-ebrokerdj.fbs.com.tw/z/zc/zca/zca_%s.djhtm' %(obj.code)
    txt = xurl.load(url, encoding='big5_hkscs')
    m = re.search(r'>收盤價</td>\s*<td class="t3n1">(.*)</td>', txt)
    if m:
        obj.close = float(m.group(1).replace(',',''))
    m = re.search(r'>本益比</td>\s*<td class="t3n1">(.*)</td>', txt)
    if m and m.group(1) != 'N/A':
        obj.per = float(m.group(1).replace(',',''))
    m = re.search(r'>每股淨值\(元\)</td>\s*<td class="t3n1"><span class="t3n1">(.*?)</span></td>', txt)
    if m:
        obj.nav = float(m.group(1).replace(',',''))
    m = re.search(r'>負債比例</td>\s*<td class="t3n1"><span class="t3n1">(.*?)%</span></td>', txt)
    if m:
        obj.debt_ratio = float(m.group(1)) / 100
    m = re.search(r'>年度</td>(.*?)</tr>', txt, re.MULTILINE | re.DOTALL)
    if m:
        obj.per_year = [twse.to_common_era(x.replace(',','')) for x in re.findall(r'>([^<]+)</td>', m.group(1))]
    m = re.search(r'>最高本益比</td>(.*?)</tr>', txt, re.MULTILINE | re.DOTALL)
    if m:
        obj.per_max = [float(x.replace(',','')) if x != 'N/A' else 0 for x in re.findall(r'>([^<]+)</td>', m.group(1))]
    m = re.search(r'>最低本益比</td>(.*?)</tr>', txt, re.MULTILINE | re.DOTALL)
    if m:
        obj.per_min = [float(x.replace(',','')) if x != 'N/A' else 0 for x in re.findall(r'>([^<]+)</td>', m.group(1))]
    m = re.search(r'>現金股利</td>(.*?)</tr>', txt, re.MULTILINE | re.DOTALL)
    if m:
        obj.dividend_cash = [float(x.replace(',','')) if x != 'N/A' else 0 for x in re.findall(r'>([^<]+)</td>', m.group(1))]
    m = re.search(r'<tr>\s*<td[^>]*>股票股利</td>(.*?)</tr>', txt, re.MULTILINE | re.DOTALL)
    if m:
        obj.dividend_stock = [float(x.replace(',','')) if x != 'N/A' else 0 for x in re.findall(r'>([^<]+)</td>', m.group(1))]
    m = re.search(r'>股本\(億, 台幣\)</td>\s*<td class="t3n1">(.*)</td>', txt)
    if m:
        obj.capital_stock = float(m.group(1).replace(',',''))
    return

def get_stock_report(code):
    obj = stock_report(code)
    update_stock_report_eps(obj)
    update_stock_report_revenue(obj)
    update_stock_report_overall(obj)
    return obj

def load_json(fn):
    local = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'jsons', fn)
    with open(local, 'r') as f:
        return json.load(f)
    return None

def load_exr():
    data = get_exchange_rate_data()
    return json.dumps([x.__dict__ for x in data])

def load_stock():
    objs = load_json('stocks.json')
    parsed = {s['code']:s for s in objs}
    data = get_data(list(parsed.keys()))
    for d in data:
        d.tags = parsed[d.code]['tags']
        d.flts = parsed[d.code]['flts']
    return json.dumps([x.__dict__ for x in data])

def load_watchlist():
    objs = load_json('stocks.json')
    for s in objs:
        ex, s['name'] = twse.get_name(s['code'])
    return json.dumps(objs)

def load_strategy():
    objs = load_json('strategy.json')
    codes = [s['code'] for s in objs]
    msg = twse.get_msg(codes)
    parsed = {m['c']:twse.StockInfo(msg=m) for m in msg}
    for s in objs:
        c = s['code']
        if c in parsed:
            s['z'] = parsed[c].z
            s['name'] = parsed[c].name
    return json.dumps(objs)

def load_csv(args):
    code = args.get('c')
    end = datetime.datetime.now()
    start = end - datetime.timedelta(days=540)
    df = quote.get_data(code, start, end)
    df['date'] = df['date'].dt.strftime('%Y-%m-%d')
    ex, name = twse.get_name(code)
    return '{{"code":"{}","name":"{}","data":{}}}'.format(code, name, df.to_json(orient='records', indent=4))

def load_etf(args):
    date = args.get('d', datetime.date.today())
    tail = int(args.get('t', 1))
    df = twse.all_etf(date, 60, tail)
    return df.to_json(orient='records', indent=4)

def load(args):
    name = args.get('n')
    if name == 'exr':
        return load_exr()
    if name == 'stock':
        return load_stock()
    if name == 'watchlist':
        return load_watchlist()
    if name == 'strategy':
        return load_strategy()
    if name == 'csv':
        return load_csv(args)
    if name == 'etf':
        return load_etf(args)
    return None

def report(args):
    code = args.get('c')
    if code:
        rpt_obj = get_stock_report(code)
        return json.dumps(rpt_obj.__dict__, cls=MyJSONEncoder)
    return

def dispatch(fn, args):
    func = globals().get(fn)
    if callable(func):
        return func(args)
    return 'EEROR'

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--code', default='0050')
    parser.add_argument('-r', '--report', action="store_true", default=False)
    parser.add_argument('-v', '--verbose', action="store_true", default=False)
    parser.add_argument('--func')
    parser.add_argument('--func_args')
    parser.add_argument('--output')
    args, unparsed = parser.parse_known_args()

    xurl.set_verbose(args.verbose)

    if args.func and args.func_args and args.output:
        ret = dispatch(args.func, json.loads(args.func_args))
        with open(args.output, 'w') as fd:
            fd.write(ret)
        return

    if args.report and args.code:
        rpt = get_stock_report(code)
        rpt.show()
        return

    if unparsed:
        ret = load({'n':unparsed[0], 'c':args.code})
        print(ret)

    return

if __name__ == '__main__':
    main()
