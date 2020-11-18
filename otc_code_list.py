#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import re
import sys

import xurl

def main():
    url = 'https://isin.twse.com.tw/isin/C_public.jsp?strMode=4'
    txt = xurl.load(url)
    m = re.findall(r'<tr><td bgcolor=#FAFAD2>(\w+)', txt)
    xurl.saveLocal('otc_code_list.txt', '\n'.join(m))
    return

if __name__ == '__main__':
    main()
