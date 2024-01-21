#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import re
import cgi
import cgitb

def main():

    print('Content-type:text/html\n')

    args = cgi.FieldStorage()
    j = args.getvalue('j', None)
    data = args.getvalue('data', None)

    if j and data:
        local = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'jsons', j)
        with open(local, 'w') as fd:
            fd.write(data)
        print('OK')

    return

cgitb.enable()
main()
