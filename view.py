#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import json

import twstock

from mod_python import util, Cookie

def index(req):
    req.content_type = 'text/html; charset=utf-8'
    form = req.form or util.FieldStorage(req)
    path = form.get('i', None)
    code = form.get('c', None)
    stat = form.get('s', None)
    infos = []
    twstock.init('twstock-view.log')
    if code:
        data = twstock.get_stock_json_by_codes(code)
        infos.extend(twstock.get_stock_infos(data))
    if path:
        data = twstock.get_json_from_file(path)
        infos.extend(twstock.get_stock_infos(data))
    if len(infos) == 0:
        defpath = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'jsons/stocks.json')
        data = twstock.get_json_from_file(defpath)
        infos = twstock.get_stock_infos(data)
    twstock.update_stock_stats(infos, not stat)
    json_list = [json.dumps(info.__dict__) for info in infos]
    req.write('{"stocks":[%s]}' %(','.join(json_list)))
    return

