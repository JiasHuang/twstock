#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import re
import sys
import time
import glob

from optparse import OptionParser

class defs:
    workdir = os.path.join(os.path.expanduser('~'), 'Downloads')

def get_code(f):
    with open(f) as fd:
        l0 = fd.readline()
        l1 = fd.readline()
        m = None
        if f.endswith('.csv'):
            m = re.search(r',="(\d{4})"', l1)
        if f.endswith('.CSV'):
            m = re.search(r',(\d{4})', l1)
        if m:
            return m.group(1)
    return None

def get_date_from_mtime(f):
    t = time.strftime('%Y%m%d%H%M', time.localtime(os.path.getmtime(f)))
    d = int(t[:8])
    h = int(t[8:10])
    if h < 14:
        d -= 1
    return d

def main():
    parser = OptionParser()
    parser.add_option("-d", "--dir", dest="dir", default=defs.workdir)
    parser.add_option("-D", "--date", dest="date")
    (options, args) = parser.parse_args()
    if options.dir:
        os.chdir(options.dir)
    files = []
    files.extend(glob.glob('*.csv'))
    files.extend(glob.glob('*.CSV'))
    for f in files:
        code = get_code(f)
        if not code:
            continue
        d = options.date or get_date_from_mtime(f)
        fdir = '{}'.format(code)
        fname = '{}-{}.csv'.format(code, d)
        print('%s/%s' %(fdir, fname))
        os.system('mkdir -p %s' %(fdir))
        os.system('mv \'%s\' %s/%s' %(f, fdir, fname))
    return

if __name__ == '__main__':
    main()
