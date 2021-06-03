#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import re
import tempfile

from mod_python import util, Cookie

def index(req):

    req.content_type = 'text/html; charset=utf-8'
    form = req.form or util.FieldStorage(req)

    x = req.unparsed_uri.split('?')
    f = os.path.basename(x[0]).strip('.py')
    q = x[1] if len(x) > 1 else ''
    o = tempfile.NamedTemporaryFile(delete=False).name

    s = os.path.join(os.path.dirname(__file__), 'server.py')
    cmd = '%s -o %s -e \'%s("%s")\'' %(s, o, f, q)

    os.system(cmd)
    with open(o, 'r') as fd:
        req.write(fd.read())
    os.remove(o)

    return

