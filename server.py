#!/usr/bin/python3

import re
import os
import json
import configparser

from http.server import BaseHTTPRequestHandler, HTTPServer
from http.cookies import SimpleCookie
from urllib.parse import urlparse, parse_qs, quote, unquote, unquote_plus
from optparse import OptionParser

import xurl
import twstock
import broker
import bshtm

opts = None

class defvals:
    hostname = ''
    hostport = 8081

def exr(q):
    d = parse_qs(q)
    path = d['i'][0] if 'i' in d else os.path.join(os.path.dirname(os.path.abspath(__file__)), 'jsons', 'exr.json')
    data = twstock.get_json_from_file(path)
    exchange_rate_infos = twstock.get_exchange_rate_infos(data)
    exchange_rate_json_list = [json.dumps(x.__dict__) for x in exchange_rate_infos]
    return '{"ExchangeRates":[%s]}' %(','.join(exchange_rate_json_list))

def view(q):
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
    j = d['j'][0] if 'j' in d else 'stocks.json'
    local = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'jsons', os.path.basename(j))
    return xurl.readLocal(local)

def dividend(q):
    d = parse_qs(q)
    code = d['c'][0] if 'c' in d else None
    objs = []
    if code:
        for c in code.split(','):
            obj = twstock.stock_report(c)
            twstock.update_stock_report_dividend(obj)
            objs.append(obj)
        json_list = [json.dumps(obj.__dict__) for obj in objs]
        return '{"stocks":[%s]}' %(','.join(json_list))
    return

def report(q):
    d = parse_qs(q)
    code = d['c'][0] if 'c' in d else None
    if code:
        rpt_obj = twstock.get_stock_report(code)
        return json.dumps(rpt_obj.__dict__)
    return

def populate(q):
    d = parse_qs(q)
    a = d['a'][0] if 'a' in d else None
    no = d['no'][0] if 'no' in d else None
    if a == 'broker':
        json_list = [json.dumps(x.__dict__) for x in broker.get_db()]
        return '{"db":[%s]}' %(','.join(json_list))
    if a == 'bshtm':
        json_list = [json.dumps(x.__dict__) for x in bshtm.get_db()]
        return '{"db":[%s]}' %(','.join(json_list))
    if a == 'track':
        (hdrs, tracks) = broker.get_cached_tracks(no)
        hdrs_json_list = [json.dumps(x.__dict__) for x in hdrs]
        tracks_json_list = [json.dumps(x.__dict__) for x in tracks]
        return '{"hdrs":[%s],"tracks":[%s]}' %(','.join(hdrs_json_list), ','.join(tracks_json_list))
    return None

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
        if p.path in ['/upload']:
            eval('%s(post_data, p.query)' %(p.path[1:]))
            self.send_response(200)
            self.send_header('Content-type', "text/html")
            self.end_headers()
            self.wfile.write(bytes('OK', "utf8"))
        return
    def do_GET(self):
        if self.path == '/':
            self.send_response(302)
            self.send_header('Location', 'index.html')
            self.end_headers()
            return
        p = urlparse(self.path)
        if p.path in ['/exr', '/view', '/load', '/dividend', '/report', '/populate']:
            self.send_response(200)
            self.send_header('Content-type', "text/html")
            self.end_headers()
            results = eval('%s(p.query)' %(p.path[1:]))
            self.wfile.write(bytes(results, 'utf8'))
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

def main():
    global opts

    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    parser = OptionParser()
    parser.add_option("-n", "--hostname", dest="hostname", default=defvals.hostname)
    parser.add_option("-p", "--hostport", type="int", dest="port", default=defvals.hostport)
    parser.add_option("-c", "--config", dest="config")
    parser.add_option("--workdir", dest="workdir")
    parser.add_option("--ua", dest="ua")
    parser.add_option("--expiration", dest="expiration")
    (opts, args) = parser.parse_args()

    if opts.config:
        parser = configparser.ConfigParser()
        parser.read(opts.config)
        for k in parser['TWStock']:
            setattr(opts, k, parser['TWStock'][k])

    # update xurl settings
    for k in ['workdir', 'ua', 'expiration']:
        if getattr(opts, k):
            setattr(xurl.defvals, k, getattr(opts, k))

    webServer = HTTPServer((opts.hostname, opts.port), TWStockServer)
    print('TWStock Server started http://%s:%s' % (opts.hostname, opts.port))

    try:
        webServer.serve_forever()
    except KeyboardInterrupt:
        pass

    webServer.server_close()
    print('TWStock Server stopped.')

    return

if __name__ == '__main__':
    main()
