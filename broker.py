#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import re
import glob

from optparse import OptionParser

import xurl

class broker:
    codemap = {
        '1360':'　麥格理',
        '1380':'台灣匯立',
        '1440':'　　美林',
        '1470':'台灣摩根',
        '1480':'美商高盛',
        '1520':'瑞士信貸',
        '1560':'港商野村',
        '1570':'法國興業',
        '1590':'花旗環球',
        '1650':'　　瑞銀',
        '8440':'摩根大通',
        '8890':'大和國泰',
        '8900':'法銀巴黎',
        '8960':'上海匯豐'}
    defs = ['1470','1480','1520','1650','8440','8960']
    db_location = '/var/tmp/vod_load_*'
    def __init__(self, no, bno, qty, avg, date):
        self.no = no
        self.bno = bno
        self.bname = get_broker_name(bno)
        self.qty = qty
        self.avg = avg
        self.date = date

class track:
    def __init__(self, date, b_qty, b_pz, s_qty, s_pz):
        self.date = date
        self.b_qty = int(b_qty.replace(',',''))
        self.b_pz = float(b_pz)
        self.s_qty = int(s_qty.replace(',',''))
        self.s_pz = float(s_pz)
    def show(self):
        print('{0.date} {0.b_qty:+8} {0.b_pz:8.2f} | {1:+8} {0.s_pz:8.2f}'.format(self, -x.s_qty))

class track_hdr:
    def __init__(self, no, bno, cnt):
        self.no = no
        self.bno = bno
        self.bname = get_broker_name(bno)
        self.cnt = cnt

class trace_broker_opts:
    def __init__(self):
        self.lines = None
        self.cookies = None
        self.verbose = False
        self.track = False
        self.cache = True
        self.cacheOnly = True

def get_broker_name(b):
    if b in broker.codemap:
        return '{b} {n}'.format(b=b, n=broker.codemap[b])
    return b

def get_db_pairs():
    tuples = []
    for f in glob.glob(broker.db_location):
        with open(f) as fd:
            m = re.search(r'bno=(\w{4})&amp;no=(\w{4})"', fd.read())
            if m:
                tuples.append((m.group(2), m.group(1)))
    return tuples

def get_tracks(no, bno, opts):
    url = 'https://histock.tw/stock/brokertrace.aspx?bno={b}&no={n}'.format(b=bno, n=no)
    url_opts = []
    if opts.cookies:
        url_opts.append('-H \'cookie: ' + opts.cookies + '\'')
    txt = xurl.load(url, opts=url_opts, cache=opts.cache, cacheOnly=opts.cacheOnly, verbose=opts.verbose)

    vec = []
    for m in re.finditer(r'<td>(.*?)</td><td>([\d|,]+)</td><td>(\d+[.]\d*)</td><td>([\d|,]+)</td><td>(\d+[.]\d*)</td>', txt):
        vec.insert(0, track(m.group(1), m.group(2), m.group(3), m.group(4), m.group(5)))

    if len(vec) == 0 and re.search('alert', txt):
        os.remove(xurl.genLocal(url))

    return vec

def get_cached_tracks(no, bno=None):
    opts = trace_broker_opts()
    if bno:
        tracks = get_tracks(no, bno, opts)
        hdrs = [track_hdr(no, bno, len(tracks))]
        return (hdrs, tracks)
    tracks = []
    hdrs = []
    for (db_no, db_bno) in get_db_pairs():
        if db_no == no:
            ret = get_tracks(db_no, db_bno, opts)
            if len(ret):
                tracks.extend(ret)
                hdrs.append(track_hdr(db_no, db_bno, len(ret)))
    return (hdrs, tracks)

def trace_broker(no, bno, opts):
    vec = get_tracks(no, bno, opts)
    if len(vec) == 0:
        print('NOT FOUND: no={} bno={}'.format(no, bno))
        return None

    qty = 0
    cost = 0
    avg = 0
    idx_range = None
    if opts.lines:
        idx_range = len(vec) - opts.lines

    if opts.track:
        print('{}\n{}'.format('-' * 100, get_broker_name(bno)))

    for idx, x in enumerate(vec):
        qty += x.b_qty - x.s_qty;
        if qty > 0:
            cost = (cost + x.b_qty * x.b_pz) / (qty + x.s_qty) * qty
            avg = cost / qty
        else:
            qty = cost = avg = 0
        text = ['-', '-']
        if x.b_qty:
            text[0] = '{0:+8} {1:8.2f}'.format(x.b_qty, x.b_pz)
        if x.s_qty:
            text[1] = '{0:+8} {1:8.2f}'.format(-x.s_qty, x.s_pz)
        if opts.track and (not idx_range or idx >= idx_range):
            print('{} | {:>17s} | {:>17s} | {:+8,} | qty {:10,} | avg {:8.2f}'.format(x.date, text[0], text[1], x.b_qty - x.s_qty, qty, avg))

    return broker(no, bno, qty, avg, vec[-1].date)

def list_bn():
    for k in broker.codemap:
        print('{k} {n}'.format(k=k, n=broker.codemap[k]))
    return

def show_results(results):
    curno = None
    for x in sorted(results, key=lambda x: (x.no, x.qty), reverse=True):
        if curno != x.no:
            curno = x.no
            print('\n{d}\n股票代碼：{n}\n'.format(d='-'*100, n=x.no))
        print('{:15} | qty {:10,} | avg {:8.2f} | {}'.format(x.bname, x.qty, x.avg, x.date))
    return

def get_db(opts=None):
    tuples = get_db_pairs()
    results = []
    opts = opts or trace_broker_opts()
    for (no, bno) in tuples:
        ret = trace_broker(no, bno, opts)
        if ret:
            results.append(ret)
    return results

def list_db(opts):
    opts.cacheOnly = True
    opts.track = False
    results = get_db(opts)
    show_results(results)
    return

def main():
    parser = OptionParser()
    parser.add_option("-b", "--broker", dest="broker", action="append")
    parser.add_option("-n", "--stockno", dest="stockno")
    parser.add_option("-l", "--lines", dest="lines", type="int", default=20)
    parser.add_option("-c", "--cookies", dest="cookies")
    parser.add_option("-v", "--verbose", dest="verbose", action="store_true", default=False)
    parser.add_option("--notrack", dest="track", action="store_false", default=True)
    parser.add_option("--nocache", dest="cache", action="store_false", default=True)
    parser.add_option("--cacheOnly", dest="cacheOnly", action="store_true", default=False)
    parser.add_option("--listbn", dest="listbn", action="store_true", default=False)
    parser.add_option("--listdb", dest="listdb", action="store_true", default=False)
    (opts, args) = parser.parse_args()
    if opts.listbn:
        list_bn()
        return
    if opts.listdb:
        list_db(opts)
        return
    brokers = opts.broker or broker.defs
    results = []
    for bno in brokers:
        ret = trace_broker(opts.stockno, bno, opts)
        if ret:
            results.append(ret)
    show_results(results)
    return

if __name__ == '__main__':
    xurl.addDelayObj(r'histock.tw', 2)
    main()
