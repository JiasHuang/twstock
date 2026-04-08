#!/usr/bin/python3
# -*- coding: utf-8 -*-

import argparse
import datetime
import calendar

import xurl

split_stocks = {
    #'0050': {'date':datetime.datetime(2025, 6, 18), 'rate':4},
    #'00631L': {'date':datetime.datetime(2026, 3, 31), 'rate':22},
    '00631L': {'date':datetime.datetime(2026, 3, 23), 'rate':22},
    #'00663L': {'date':datetime.datetime(2025, 6, 11), 'rate':7},
    '00663L': {'date':datetime.datetime(2025, 6, 2), 'rate':7},
}

def get_epoch(date):
    return int(date.timestamp())

def load(code, start, end, cacheOnly=False):
    data = []
    url = 'https://query1.finance.yahoo.com/v8/finance/chart/{}.TW?period1={}&period2={}&interval=1d&events=history'.format(code, get_epoch(start), get_epoch(end))
    obj = xurl.load_json(url, cacheOnly=cacheOnly)

    if not obj:
        return []

    try:
        result = obj.get('chart').get('result')[0]
        ts = result.get('timestamp')
        quote = result.get('indicators').get('quote')[0]
    except:
        return []

    ov = quote.get('open')
    hv = quote.get('high')
    lv = quote.get('low')
    cv = quote.get('close')
    vv = quote.get('volume')

    for i in range(len(ts)):
        if ts[i] and ov[i] and hv[i] and lv[i] and cv[i] and vv[i]:
            d = datetime.datetime.fromtimestamp(ts[i])
            o = round(ov[i], 2)
            h = round(hv[i], 2)
            l = round(lv[i], 2)
            c = round(cv[i], 2)
            v = round(vv[i] / 1000)

            if code in split_stocks and d < split_stocks[code]['date']:
                #print('{} {}'.format(d, c))
                r = split_stocks[code]['rate']
                o = round(o / r, 2)
                h = round(h / r, 2)
                l = round(l / r, 2)
                c = round(c / r, 2)
                v = v * r

            data.append({'date':d, 'open':o, 'high':h, 'low':l, 'close':c, 'volume':v})

    return data

def get_data(code, start, end, cacheOnly=False):

    if isinstance(start, str):
        start = datetime.datetime.strptime(start, '%Y%m%d')
    if isinstance(end, str):
        end = datetime.datetime.strptime(end, '%Y%m%d')

    data = []

    # before this year
    y = start.year
    while y != end.year:
        s = datetime.datetime(y, 1, 1, 0, 0)
        e = datetime.datetime(y, 12, 31, 23, 59)
        data = data + load(code, s, e, True)
        y += 1

    # before this month
    if end.month != 1:
          weekday, days = calendar.monthrange(end.year, end.month - 1)
          s = datetime.datetime(y, 1, 1, 0, 0)
          e = datetime.datetime(y, end.month - 1, days, 23, 59)
          data = data + load(code, s, e, True)

    # this month
    s = datetime.datetime(end.year, end.month, 1, 0, 0)
    e = datetime.datetime(end.year, end.month, end.day, 23, 59)
    data = data + load(code, s, e, False)

    filtered = []
    for d in data:
        if d['date'] >= start and d['date'] <= end:
            d['date'] = d['date'].strftime('%Y%m%d')
            filtered.append(d)

    return filtered

def main():

    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--code', default='0050')
    parser.add_argument('-s', '--start', default='20251001')
    parser.add_argument('-e', '--end')
    parser.add_argument('-v', '--verbose', action="store_true", default=False)
    args, unparsed = parser.parse_known_args()

    if not args.end:
        args.end = datetime.datetime.now()

    xurl.set_verbose(args.verbose)

    ret = get_data(args.code, args.start, args.end)
    for x in ret:
        print(x)

    return

if __name__ == '__main__':
    main()
