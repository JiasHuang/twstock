#!/usr/bin/python3

import re
import json

import xurl

tse_output = 'jsons/tse-code-list.json'
otc_output = 'jsons/otc-code-list.json'
tse_test = ['0050']
otc_test = ['00720B']

def parse(url, output):
    txt = xurl.load(url, encoding='big5_hkscs', verbose=True)
    matches = re.finditer(r'<tr><td bgcolor=#FAFAD2>(\w+)　([\w&-\*]+)', txt)
    data = {m.group(1):m.group(2) for m in matches}
    with open(output, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    return

def gen_tse():
    url = 'https://isin.twse.com.tw/isin/C_public.jsp?strMode=2'
    parse(url, tse_output)
    return

def gen_otc():
    url = 'https://isin.twse.com.tw/isin/C_public.jsp?strMode=4'
    parse(url, otc_output)
    return

def test():
    with open(tse_output, 'r') as f:
        data = json.load(f)
        for k in tse_test:
            print('{}: {}'.format(k, data[k]))
    with open(otc_output, 'r') as f:
        data = json.load(f)
        for k in otc_test:
            print('{}: {}'.format(k, data[k]))
    return

def main():
    gen_tse()
    gen_otc()
    test()
 
if __name__ == '__main__':
    main()
