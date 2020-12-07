#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import json

import twstock

from mod_python import util, Cookie

def index(req):
    req.content_type = 'text/html; charset=utf-8'
    form = req.form or util.FieldStorage(req)
    code = form.get('c', None)
    twstock.init(logfile='twstock-dividend.log')
    objs = []
    if code:
        for c in code.split(','):
            obj = twstock.stock_report(c)
            twstock.update_stock_report_dividend(obj)
            objs.append(obj)
        json_list = [json.dumps(obj.__dict__) for obj in objs]
        req.write('{"stocks":[%s]}' %(','.join(json_list)))
    return



