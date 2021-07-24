#!/usr/bin/python3

import os
import re
import glob
import configparser
import argparse

import xurl

class defvals:
    config_section = 'TWStock'
    config_path = os.path.join(os.path.expanduser('~'), '.myconfig')

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
    db_location = '/var/tmp/twstock_load_broker_*'
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
    def __init__(self, no, bno, idx_start, idx_end):
        self.no = no
        self.bno = bno
        self.bname = get_broker_name(bno)
        self.idx_start = idx_start
        self.idx_end = idx_end

class trace_broker_args:
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
        with open(f, 'r', errors='replace') as fd:
            m = re.search(r'bno=(\w{4})&amp;no=(\w{4})"', fd.read())
            if m:
                tuples.append((m.group(2), m.group(1)))
    return tuples

def get_tracks(no, bno, args):
    url = 'https://histock.tw/stock/brokertrace.aspx?bno={b}&no={n}'.format(b=bno, n=no)
    url_opts = []
    if args.cookies:
        url_opts.append('-H \'cookie: ' + args.cookies + '\'')

    local = xurl.genLocal(url, prefix='twstock_load_broker_')
    txt = xurl.load(url, local=local, opts=url_opts, cache=args.cache, cacheOnly=args.cacheOnly, verbose=args.verbose)

    vec = []
    for m in re.finditer(r'<td>(.*?)</td><td>([\d|,]+)</td><td>(\d+[.]\d*)</td><td>([\d|,]+)</td><td>(\d+[.]\d*)</td>', txt):
        vec.insert(0, track(m.group(1), m.group(2), m.group(3), m.group(4), m.group(5)))

    if len(vec) == 0 and re.search('alert', txt):
        os.remove(local)

    return vec

def get_cached_tracks(no, bno=None):
    args = trace_broker_args()
    if bno:
        tracks = get_tracks(no, bno, args)
        hdrs = [track_hdr(no, bno, len(tracks))]
        return (hdrs, tracks)
    tracks = []
    hdrs = []
    for (db_no, db_bno) in get_db_pairs():
        if db_no == no:
            ret = get_tracks(db_no, db_bno, args)
            if len(ret):
                tracks.extend(ret)
                hdrs.append(track_hdr(db_no, db_bno, len(tracks) - len(ret), len(tracks)))
    return (hdrs, tracks)

def trace_broker(no, bno, args):
    vec = get_tracks(no, bno, args)
    if len(vec) == 0:
        print('[broker] stock_no={} broker_no={} : Not Found'.format(no, bno))
        return None

    qty = 0
    cost = 0
    avg = 0
    idx_range = None
    if args.lines:
        idx_range = len(vec) - args.lines

    if args.track:
        print('\n{}\n{}\n'.format('-' * 100, get_broker_name(bno)))

    for idx, x in enumerate(vec):
        if x.s_qty:
            if qty < x.s_qty:
                qty = cost = avg = 0
            else:
                qty -= x.s_qty
                cost -= x.s_qty * avg
        if x.b_qty:
            qty += x.b_qty
            cost += x.b_qty * x.b_pz
            avg = cost / qty
        text = ['-', '-']
        if x.b_qty:
            text[0] = '{0:+8} {1:8.2f}'.format(x.b_qty, x.b_pz)
        if x.s_qty:
            text[1] = '{0:+8} {1:8.2f}'.format(-x.s_qty, x.s_pz)
        if args.track and (not idx_range or idx >= idx_range):
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

def get_db(args=None):
    tuples = get_db_pairs()
    results = []
    args = args or trace_broker_args()
    for (no, bno) in tuples:
        ret = trace_broker(no, bno, args)
        if ret:
            results.append(ret)
    return results

def list_db(args):
    args.cacheOnly = True
    args.track = False
    results = get_db(args)
    show_results(results)
    return

class LoadConfig(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        setattr(namespace, self.dest, values)
        cfg = configparser.ConfigParser()
        cfg.read(values)
        section = cfg[defvals.config_section]
        for k in section:
            setattr(namespace, k, section[k])

def str2bool(v):
    if isinstance(v, bool):
        return v
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')

def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument('-b', '--broker')
    parser.add_argument('-n', '--stockno')
    parser.add_argument('-l', '--lines', default=20)
    act_cfg = parser.add_argument('-c', '--config', action=LoadConfig)
    parser.add_argument('-v', '--verbose', type=str2bool, nargs='?', const=True, default=False)
    parser.add_argument('--track', type=str2bool, nargs='?', const=True, default=True)
    parser.add_argument('--cache', type=str2bool, nargs='?', const=True, default=True)
    parser.add_argument('--cacheOnly', type=str2bool, nargs='?', const=True, default=False)
    parser.add_argument('--listbn', type=str2bool, nargs='?', const=True, default=False)
    parser.add_argument('--listdb', type=str2bool, nargs='?', const=True, default=False)
    parser.add_argument('--cookies')
    args = parser.parse_args(argv)

    # auto load config
    if not args.config and os.path.exists(defvals.config_path):
        act_cfg(parser, args, defvals.config_path)
        args = parser.parse_args(argv, namespace=args)

    if args.listbn:
        list_bn()
        return

    if args.listdb:
        list_db(args)
        return

    if args.broker and args.stockno:
        results = []
        for bno in (args.broker or '').split(','):
            ret = trace_broker(args.stockno, bno, args)
            if ret:
                results.append(ret)
        show_results(results)

    return

if __name__ == '__main__':
    xurl.addDelayObj(r'histock.tw', 2)
    main()
