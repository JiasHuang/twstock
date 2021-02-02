#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import json

import xurl
import broker
import bshtm

from mod_python import util, Cookie

def index(req):
    req.content_type = 'text/html; charset=utf-8'
    form = req.form or util.FieldStorage(req)
    a = form.get('a', None)
    bno = form.get('bno', None)
    no = form.get('no', None)
    if a == 'broker':
        json_list = [json.dumps(x.__dict__) for x in broker.get_db()]
        req.write('{"db":[%s]}' %(','.join(json_list)))
    if a == 'bshtm':
        json_list = [json.dumps(x.__dict__) for x in bshtm.get_db()]
        req.write('{"db":[%s]}' %(','.join(json_list)))
    if a == 'track':
        json_list = [json.dumps(x.__dict__) for x in broker.get_cached_tracks(bno, no)]
        req.write('{"db":[%s]}' %(','.join(json_list)))
    return

