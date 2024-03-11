#!/usr/bin/python3

import re
import os
import json
import configparser
import argparse

from http.server import BaseHTTPRequestHandler, HTTPServer
from http.cookies import SimpleCookie
from urllib.parse import urlparse, parse_qs, quote, unquote, unquote_plus

import xurl
import twstock

class defvals:
    hostname = ''
    hostport = 8081
    expiration = 28800

def exr(q):
    d = parse_qs(q)
    if 'j' in d:
        j = d['j'][0]
        local = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'jsons', j)
        data = twstock.get_json_from_file(local)
        exchange_rate_infos = twstock.get_exchange_rate_infos(data)
        exchange_rate_json_list = [json.dumps(x.__dict__) for x in exchange_rate_infos]
        return '{"ExchangeRates":[%s]}' %(','.join(exchange_rate_json_list))
    return None

def stock(q):
    d = parse_qs(q)
    path = d['i'][0] if 'i' in d else None
    code = d['c'][0] if 'c' in d else None
    stat = d['s'][0] if 's' in d else None
    infos = []
    if code:
        data = twstock.get_stock_json_by_codes(code)
        infos.extend(twstock.get_stock_infos(data))
    if path:
        data = twstock.get_json_from_file(path)
        infos.extend(twstock.get_stock_infos(data))
    if len(infos) == 0:
        defpath = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'jsons', 'stocks.json')
        data = twstock.get_json_from_file(defpath)
        infos = twstock.get_stock_infos(data)
    twstock.update_stock_stats(infos, not stat)
    json_list = [json.dumps(info.__dict__) for info in infos]
    return '{"stocks":[%s]}' %(','.join(json_list))

def load(q):
    d = parse_qs(q)
    if 'j' in d:
        j = d['j'][0]
        local = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'jsons', j)
        return xurl.readLocal(local)
    return None

def dividend(q):
    d = parse_qs(q)
    code = d['c'][0] if 'c' in d else None
    objs = []
    if code:
        for c in code.split(','):
            obj = twstock.stock_report(c)
            twstock.update_stock_report_dividend(obj)
            objs.append(obj)
        json_list = [json.dumps(obj.__dict__, cls=twstock.MyJSONEncoder) for obj in objs]
        return '{"stocks":[%s]}' %(','.join(json_list))
    return

def report(q):
    d = parse_qs(q)
    code = d['c'][0] if 'c' in d else None
    if code:
        rpt_obj = twstock.get_stock_report(code)
        return json.dumps(rpt_obj.__dict__, cls=twstock.MyJSONEncoder)
    return

def upload(post_data, q):
    d = parse_qs(q)
    j = d['j'][0] if 'j' in d else None
    data = unquote_plus(post_data.decode('utf8'))[5:]
    defpath = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'jsons', os.path.basename(j))
    xurl.saveLocal(defpath, data)
    return

class TWStockServer(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass
    def do_POST(self):
        content_len = int(self.headers.get('Content-Length'))
        post_data = self.rfile.read(content_len)
        p = urlparse(self.path)
        if p.path in ['/upload.py']:
            eval('%s(post_data, p.query)' %(p.path[1:-3]))
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
            results = eval('%s(p.query)' %(os.path.basename(p.path)[:-3]))
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

def str2bool(v):
    if isinstance(v, bool):
       return v
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')

def main():

    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    parser = argparse.ArgumentParser()
    parser.add_argument('-n', '--hostname', default=defvals.hostname)
    parser.add_argument('-p', '--hostport', default=defvals.hostport)
    parser.add_argument('-c', '--config', action=LoadConfig)
    parser.add_argument('-e', '--eval')
    parser.add_argument('-o', '--output')
    parser.add_argument('--workdir')
    parser.add_argument('--ua')
    parser.add_argument('--expiration', default=defvals.expiration)
    args = parser.parse_args()

    # update xurl settings
    for k in ['workdir', 'ua', 'expiration']:
        if getattr(args, k):
            setattr(xurl.defvals, k, getattr(args, k))

    if args.eval and args.output:
        with open(args.output, 'w') as fd:
            fd.write(eval(args.eval))
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
