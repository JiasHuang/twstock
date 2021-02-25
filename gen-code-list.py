#!/usr/bin/python3

import re

import xurl

def gen_tse():
    url = 'https://isin.twse.com.tw/isin/C_public.jsp?strMode=2'
    txt = xurl.load(url)
    m = re.findall(r'<tr><td bgcolor=#FAFAD2>(\w+)', txt)
    xurl.saveLocal('tse-code-list.txt', '\n'.join(m))
    return

def gen_otc():
    url = 'https://isin.twse.com.tw/isin/C_public.jsp?strMode=4'
    txt = xurl.load(url)
    m = re.findall(r'<tr><td bgcolor=#FAFAD2>(\w+)', txt)
    xurl.saveLocal('otc-code-list.txt', '\n'.join(m))
    return

def main():
    gen_tse()
    gen_otc()
 
if __name__ == '__main__':
    main()
