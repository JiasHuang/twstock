#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import json

import xurl

from mod_python import util, Cookie

def index(req):
    req.content_type = 'text/html; charset=utf-8'
    form = req.form or util.FieldStorage(req)
    j = form.get('j', 'stocks.json') # json
    local = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'jsons', os.path.basename(j))
    req.write(xurl.readLocal(local))
    return

