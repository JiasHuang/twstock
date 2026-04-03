#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import re
import tempfile
import cgi
import cgitb
import sys

def main():

    sys.stdout.write('Content-Type: image/png\r\n\r\n')

    args = cgi.FieldStorage()
    code = args.getvalue('c', '0050')

    tmpf = tempfile.NamedTemporaryFile(mode='w+b', delete=False).name
    app = os.path.join(os.path.dirname(__file__), 'quote.py')
    cmd = '{} -c {} -o {}'.format(app, code, tmpf)

    os.system(cmd)
    with open(tmpf, 'rb') as fd:
        sys.stdout.write(fd.read())
    os.remove(tmpf)

    return

cgitb.enable()
main()
