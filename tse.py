#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os
import re
import json
import xurl
from datetime import datetime
from dateutil.relativedelta import relativedelta

def has_code(code):
    local = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'tse-code-list.txt')
    with open(local) as fd:
        for line in fd.readlines():
            if line.rstrip() == code:
                return True
    return False

def convert_date(s):
    return re.sub('(\d+)/(\d+)/(\d+)', lambda y: str(int(y.group(1)) + 1911) + y.group(2) + y.group(3), s)

def get_data(code, start='20250101'):
    today = datetime.today().date()
    date = datetime.strptime(start, '%Y%m%d').date()
    data = []
    while date <= today:
        url = 'http://www.twse.com.tw/exchangeReport/STOCK_DAY?response=json&date={}&stockNo={}'.format(date.strftime('%Y%m%d'), code)
        json_txt = xurl.load(url)
        json_obj = json.loads(json_txt)
        # fields":["日期","成交股數","成交金額","開盤價","最高價","最低價","收盤價","漲跌價差","成交筆數"]
        if 'data' in json_obj:
            for d in json_obj['data']:
                if d[1] != '0':
                    d = [x.replace(',', '') for x in d]
                    data.append({'date':convert_date(d[0]), 'open':d[3], 'high':d[4], 'low':d[5], 'close':d[6], 'volume':d[1]})
        date = date + relativedelta(months=+1)
    return data

