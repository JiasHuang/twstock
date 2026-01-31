#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os
import re
import json
import xurl
from datetime import datetime
from dateutil.relativedelta import relativedelta

def has_code(code):
    local = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'otc-code-list.txt')
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
        url = 'https://www.tpex.org.tw/www/zh-tw/afterTrading/tradingStock?code={}&date={}%2F{:02d}%2F{:02d}&id=&response=json'.format(code, date.year, date.month, date.day)
        json_txt = xurl.load(url)
        json_obj = json.loads(json_txt)
        # fields":["日期","成交張數","成交仟元","開盤","最高","最低","收盤","筆數"]
        if 'tables' in json_obj and 'data' in json_obj['tables'][0]:
            for d in json_obj['tables'][0]['data']:
                if d[1] != '0':
                    d = [x.replace(',', '') for x in d]
                    data.append({'date':convert_date(d[0]), 'open':d[3], 'high':d[4], 'low':d[5], 'close':d[6], 'volume':d[1]+'000'})
        date = date + relativedelta(months=+1)
    return data

