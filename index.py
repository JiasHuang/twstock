#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import re
import tempfile
import cgi
import cgitb

def main():

    print('Content-type:text/html\n')

    args = cgi.FieldStorage()
    func_args = ''

    for k in args.keys():
        func_args = '{}={}'.format(k, args.getvalue(k))

    func = os.path.basename(__file__).replace('.py', '')
    tmpf = tempfile.NamedTemporaryFile(delete=False).name
    server = os.path.join(os.path.dirname(__file__), 'server.py')
    cmd = '%s -o %s -e \'%s("%s")\'' %(server, tmpf, func, func_args)

    os.system(cmd)
    with open(tmpf, 'r') as fd:
        print(fd.read())
    os.remove(tmpf)

    return

cgitb.enable()
main()
