#!/usr/bin/python3

import os
import re
import sys
import time
import glob
import argparse

import xurl

class defs:
    workdir = os.path.join(os.path.expanduser('~'), 'Downloads')

def get_code(f, encoding=None):
    with open(f, encoding=encoding) as fd:
        l0 = fd.readline()
        l1 = fd.readline()
        m = None
        if f.endswith('.csv'):
            m = re.search(r',="(\d{4})"', l1) or re.search(r',="(\d{5})"', l1)
        if f.endswith('.CSV'):
            m = re.search(r',(\d{4})', l1)
        if m:
            return m.group(1)
    return None

def get_date_from_bshtm():
    url = 'https://bsr.twse.com.tw/bshtm/bsWelcome.aspx'
    txt = xurl.load(url)
    m = re.search(r'<span id="Label_Date">(\d+)/(\d+)/(\d+)</span>', txt)
    return int(m.group(1) + m.group(2) + m.group(3))

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--dir', default=defs.workdir)
    parser.add_argument('-D', '--date')
    args = parser.parse_args()
    if args.dir:
        os.chdir(args.dir)
    files = []
    files.extend(glob.glob('*.csv'))
    files.extend(glob.glob('*.CSV'))
    for f in files:
        code = get_code(f, encoding='big5')
        if not code:
            continue
        d = args.date or get_date_from_bshtm()
        fdir = '{}'.format(code)
        fname = '{}-{}.csv'.format(code, d)
        print('%s/%s' %(fdir, fname))
        os.system('mkdir -p %s' %(fdir))
        os.system('mv \'%s\' %s/%s' %(f, fdir, fname))
    return

if __name__ == '__main__':
    main()
