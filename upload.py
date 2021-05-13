#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import re

from mod_python import util, Cookie

def index(req):

    req.content_type = 'text/html; charset=utf-8'
    form = req.form or util.FieldStorage(req)

    j = form.get('j', None) # json
    data = form.get('data', None) # data

    if j:
        local = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'jsons', os.path.basename(j))
        with open(local, 'w') as fd:
            fd.write(data)
        req.write('OK')

    return

