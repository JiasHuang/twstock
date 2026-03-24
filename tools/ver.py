#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import glob
import time

def main():

    codes = glob.glob("*.js") + glob.glob("*.css")

    for html in glob.glob("*.html"):
        if os.path.islink(html):
            continue
        for code in codes:
            ver = time.strftime('%Y%m%d', time.gmtime(os.path.getmtime(code)))
            os.system('sed -i -r \'s/%s([^"]*)/%s\?v=%s/g\' %s' %(code, code, ver, html))

    return

if __name__ == '__main__':
    main()
