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
    no = form.get('no', None)
    bno = form.get('bno', None)
    if a == 'broker':
        json_list = [json.dumps(x.__dict__) for x in broker.get_db()]
        req.write('{"db":[%s]}' %(','.join(json_list)))
    if a == 'bshtm':
        json_list = [json.dumps(x.__dict__) for x in bshtm.get_db()]
        req.write('{"db":[%s]}' %(','.join(json_list)))
    if a == 'track':
        (hdrs, tracks) = broker.get_cached_tracks(no, bno)
        hdrs_json_list = [json.dumps(x.__dict__) for x in hdrs]
        tracks_json_list = [json.dumps(x.__dict__) for x in tracks]
        req.write('{"hdrs":[%s],"tracks":[%s]}' %(','.join(hdrs_json_list), ','.join(tracks_json_list)))
    return

