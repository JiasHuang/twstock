#!/usr/bin/python3

import re
import os
import json
import configparser
import argparse
import datetime

from http.server import BaseHTTPRequestHandler, HTTPServer
from http.cookies import SimpleCookie
from urllib.parse import urlparse, parse_qs, unquote_plus

import xurl
import twstock
import twse
import quote

class defvals:
    hostname = ''
    hostport = 8081
    expiration = 28800

def load_json(fn):
    local = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'jsons', fn)
    with open(local, 'r') as f:
        return json.load(f)
    return None

def stock(args):
    obj = load_json('stocks.json')
    parsed = {s['code']:s for s in obj['stocks']}
    data = twstock.get_data(list(parsed.keys()))
    for d in data:
        d.tags = parsed[d.code]['tags']
        d.flts = parsed[d.code]['flts']
    json_list = [json.dumps(x.__dict__) for x in data]
    return '{"stocks":[%s]}' %(','.join(json_list))

def loadcsv(args):
    code = args.get('c')
    end = datetime.date.today()
    start = end - datetime.timedelta(days=540)
    df = quote.get_data(code, start, end)
    df['date'] = df['date'].dt.strftime('%Y-%m-%d')
    ex, name = twse.get_name(code)
    return '{{"code":"{}","name":"{}","data":{}}}'.format(code, name, df.to_json(orient='records', indent=4))

def analyze(args):
    date = args.get('d', datetime.date.today())
    tail = int(args.get('t', 1))
    df = twse.analyze(date, 60, 30, 240, tail=tail)
    return df.to_json(orient='records', indent=4)

def load_exr():
    data = twstock.get_exchange_rate_data()
    json_list = [json.dumps(x.__dict__) for x in data]
    return '{"ExchangeRates":[%s]}' %(','.join(json_list))

def load_stocks():
    data = load_json('stocks.json')
    for s in data['stocks']:
        ex, s['name'] = twse.get_name(s['code'])
    return json.dumps(data)

def load_strategy():
    data = load_json('strategy.json')
    codes = [s['code'] for s in data['stocks']]
    msg = twse.get_msg(codes)
    parsed = {m['c']:twse.StockInfo(msg=m) for m in msg}
    for s in data['stocks']:
        c = s['code']
        ex, s['name'] = twse.get_name(c)
        if c in parsed:
            s['z'] = parsed[c].z
    return json.dumps(data)

def load(args):
    name = args.get('n')
    json = args.get('j')
    if name == 'exr':
        return load_exr()
    if name == 'stocks':
        return load_stocks()
    if name == 'strategy':
        return load_strategy()
    return None

def report(args):
    code = args.get('c')
    if code:
        rpt_obj = twstock.get_stock_report(code)
        return json.dumps(rpt_obj.__dict__, cls=twstock.MyJSONEncoder)
    return

def upload(post_data, args):
    j = args.get('j')
    data = unquote_plus(post_data.decode('utf8'))[5:]
    defpath = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'jsons', os.path.basename(j))
    xurl.saveLocal(defpath, data)
    return

def dispatch(func, args, output):
    with open(output, 'w') as fd:
        ret = eval(func+'(args)')
        fd.write(ret)
    return

def query_to_dict(q):
    args = parse_qs(q)
    return {k:args[k][0] for k in args.keys()}

class TWStockServer(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass
    def do_POST(self):
        content_len = int(self.headers.get('Content-Length'))
        post_data = self.rfile.read(content_len)
        p = urlparse(self.path)
        if p.path in ['/upload.py']:
            func_args = query_to_dict(p.query)
            eval('%s(post_data, func_args)' %(p.path[1:-3]))
            self.send_response(200)
            self.send_header('Content-type', "text/html")
            self.end_headers()
            try:
                self.wfile.write(bytes('OK', "utf8"))
            except:
                pass
        return
    def do_GET(self):
        if self.path == '/':
            self.send_response(302)
            self.send_header('Location', 'index.html')
            self.end_headers()
            return
        p = urlparse(self.path)
        if p.path.endswith('.py'):
            self.send_response(200)
            self.send_header('Content-type', "text/html")
            self.end_headers()
            func_args = query_to_dict(p.query)
            results = eval('%s(func_args)' %(os.path.basename(p.path)[:-3]))
            try:
                self.wfile.write(bytes(results, 'utf8'))
            except:
                pass
            return
        if p.path.endswith(('.css', '.js', '.html', '.png', '.gif')):
            local = os.path.abspath(os.curdir) + p.path
            if os.path.exists(local):
                with open(local, 'rb') as fd:
                    self.send_response(200)
                    if local.endswith('.css'):
                        self.send_header('Content-type', 'text/css')
                    elif local.endswith('.js'):
                        self.send_header('Content-type', 'application/javascript')
                    elif local.endswith('.png'):
                        self.send_header('Content-type', 'image/png')
                    elif local.endswith('.gif'):
                        self.send_header('Content-type', 'image/gif')
                    else:
                        self.send_header('Content-type', "text/html")
                    self.end_headers()
                    self.wfile.write(fd.read())
                    return
        self.send_error(404, 'File Not Found: %s' %(self.path))
        return

class LoadConfig(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        cfg = configparser.ConfigParser()
        cfg.read(values)
        for k in cfg['TWStock']:
            if k in ['hostport', 'expiration']:
                setattr(namespace, k, int(cfg['TWStock'][k]))
            else:
                setattr(namespace, k, cfg['TWStock'][k])

def main():

    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    parser = argparse.ArgumentParser()
    parser.add_argument('-n', '--hostname', default=defvals.hostname)
    parser.add_argument('-p', '--hostport', default=defvals.hostport)
    parser.add_argument('-c', '--config', action=LoadConfig)
    parser.add_argument('--func')
    parser.add_argument('--func_args')
    parser.add_argument('--output')
    parser.add_argument('--workdir')
    parser.add_argument('--ua')
    parser.add_argument('--expiration', default=defvals.expiration)
    args = parser.parse_args()

    # update xurl settings
    for k in ['workdir', 'ua', 'expiration']:
        if getattr(args, k):
            setattr(xurl.defvals, k, getattr(args, k))

    if args.func and args.func_args and args.output:
        dispatch(args.func, json.loads(args.func_args), args.output)
        return

    webServer = HTTPServer((args.hostname, args.hostport), TWStockServer)
    print('TWStock Server started http://%s:%s' % (args.hostname, args.hostport))

    try:
        webServer.serve_forever()
    except KeyboardInterrupt:
        pass

    webServer.server_close()
    print('TWStock Server stopped.')

    return

if __name__ == '__main__':
    main()
