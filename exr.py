#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import json

import twstock

from mod_python import util, Cookie

def index(req):
    req.content_type = 'text/html; charset=utf-8'
    form = req.form or util.FieldStorage(req)
    path = form.get('i', os.path.join(os.path.dirname(os.path.abspath(__file__)), 'jsons/exr.json'))
    twstock.init()
    data = twstock.get_json_from_file(path)
    exchange_rate_infos = twstock.get_exchange_rate_infos(data)
    exchange_rate_json_list = [json.dumps(x.__dict__) for x in exchange_rate_infos]
    req.write('{"ExchangeRates":[%s]}' %(','.join(exchange_rate_json_list)))
    return

