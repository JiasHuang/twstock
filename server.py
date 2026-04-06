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

def upload(post_data, args):
    j = args.get('j')
    data = unquote_plus(post_data.decode('utf8'))[5:]
    defpath = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'jsons', os.path.basename(j))
    xurl.saveLocal(defpath, data)
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
            upload(post_data, func_args)
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
            func = os.path.basename(p.path)[:-3]
            func_args = query_to_dict(p.query)
            results = twstock.dispatch(func, func_args)
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
    parser.add_argument('--workdir')
    parser.add_argument('--ua')
    parser.add_argument('--expiration', default=defvals.expiration)
    args = parser.parse_args()

    # update xurl settings
    for k in ['workdir', 'ua', 'expiration']:
        if getattr(args, k):
            setattr(xurl.defvals, k, getattr(args, k))

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
