#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os
import re
import json
import argparse
import datetime
import pandas as pd
import numpy as np

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
        self.z = 0
        self.n = None
        self.eps = []
        self.revenue = []
        self.pz_close = 0
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
        print(self.pz_close)
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

def get_ma(code, days):
    data = twse.get_data_by_days(code, days)
    vals = [float(x['close']) for x in data]
    return np.round(np.mean(vals), 2) if len(vals) else 0

def get_mv(code, days):
    data = twse.get_data_by_days(code, days)
    vals = [int(x['volume']) for x in data]
    return np.round(np.mean(vals)) if len(vals) else 0

def get_data(codes):
    parsed = {x['code']:x for x in codes}
    msg = twse.get_msg([x['code'] for x in codes])
    data = [twse.StockInfo(msg=m) for m in msg]
    for d in data:
        d.tags = parsed[d.code].get('tags', [])
        d.flts = parsed[d.code].get('flts', [])
    update_stock_stats(data)
    return data

def get_etf_msg_by_code(data, code):
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
    twse_data = json.loads(txt)
    for info in infos:
        if info.code.startswith('00'):
            msg = get_etf_msg_by_code(twse_data, info.code)
            if msg:
                nav = msg['f']
                if isinstance(nav, float):
                    info.nav = nav
                elif isinstance(nav, str) and not nav.startswith('-'):
                    info.nav = float(nav)
                info.nav_date = msg['i']
                info.nav_time = msg['j']
    return True

def update_stock_stats(infos):
    for info in infos:
        info.ma = get_ma(info.code, 60)
        info.mv = get_mv(info.code, 30)
    update_etf_nav(infos)
    return

def get_codes(codes=None):

    if codes:
        return [{'code':c} for c in codes.split(',')]

    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'jsons', 'stocks.json')
    txt = xurl.readLocal(path)
    data = json.loads(txt)
    return data['stocks']

def get_exchange_rate_data():

    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'jsons', 'exr.json')
    txt = xurl.readLocal(path)
    data = json.loads(txt)
    result = []

    url = 'https://rate.bot.com.tw/xrt/flcsv/0/day'
    txt = xurl.load(url, cache=False)

    # Currency,Rate,Cash,Spot
    for exr in data['ExchangeRates']:
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
        obj.pz_close = float(m.group(1).replace(',',''))
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
    codes = get_codes(code)
    data = get_data(codes)
    if len(data) == 0:
        return obj
    info = data[0]
    if info:
        obj.z = info.z
        obj.n = info.name
    update_stock_report_eps(obj)
    update_stock_report_revenue(obj)
    update_stock_report_overall(obj)
    return obj

def init_xcurl():
    xurl.addDelayObj(r'fbs.com.tw', 0.5)
    xurl.addDelayObj(r'twse.com.tw', 0.5)
    return

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--codes')
    parser.add_argument('-r', '--report', action="store_true", default=False)
    parser.add_argument('-e', '--exr', action="store_true", default=False)
    args, unparsed = parser.parse_known_args()

    init_xcurl()

    if args.report:
        if args.codes:
            for code in args.codes.split(','):
                rpt = get_stock_report(code)
                rpt.show()
        return

    codes = get_codes(args.codes)
    data = get_data(codes)
    update_stock_stats(data)

    df = pd.DataFrame([x.__dict__ for x in data])
    print(df.to_string())

    if args.exr:
        exr_data = get_exchange_rate_data()
        exr_df = pd.DataFrame([x.__dict__ for x in exr_data])
        print(exr_df)

    return

if __name__ == '__main__':
    main()
