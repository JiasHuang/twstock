#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os
import re
import tempfile
import json
import twstock
import cgi
import cgitb

def main():

    print('Content-type:text/html\n')

    args = cgi.FieldStorage()
    func_args = {k:args.getvalue(k) for k in args.keys()}
    func = os.path.basename(__file__).replace('.py', '')

    if True:
        ret = twstock.dispatch(func, func_args)
        print(ret)
        return

    tmpf = tempfile.NamedTemporaryFile(delete=False).name
    app = os.path.join(os.path.dirname(__file__), 'twstock.py')
    cmd = '{} --func {} --func_args \'{}\' --output {}'.format(app, func, json.dumps(func_args), tmpf)
    os.system(cmd)
    with open(tmpf, 'r') as fd:
        print(fd.read())
    os.remove(tmpf)

    return

cgitb.enable()
main()
