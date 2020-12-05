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
    twstock.init(logfile='/var/tmp/twstock-report.log')
    if code:
        rpt_obj = twstock.get_stock_report(code)
        req.write(json.dumps(rpt_obj.__dict__))
    return

