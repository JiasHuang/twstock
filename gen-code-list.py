#!/usr/bin/python3
# -*- coding: utf-8 -*-

import re
import json
import argparse

import xurl

tse_output = 'jsons/tse-code-list.json'
otc_output = 'jsons/otc-code-list.json'
etf_output = 'jsons/etf-code-list.json'
tse_etf_output = 'jsons/tse-etf-code-list.json'
otc_etf_output = 'jsons/otc-etf-code-list.json'
tse_test = ['0050']
otc_test = ['00720B']

def save(path, data):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def parse(url):
    txt = xurl.load(url, encoding='big5_hkscs')
    matches = re.finditer(r'<tr><td bgcolor=#FAFAD2>(\w+)　([\w&-\*]+)', txt)
    data = {m.group(1):m.group(2) for m in matches}
    return data

def gen_tse():
    url = 'https://isin.twse.com.tw/isin/C_public.jsp?strMode=2'
    data = parse(url)
    save(tse_output, data)
    return data

def gen_otc():
    url = 'https://isin.twse.com.tw/isin/C_public.jsp?strMode=4'
    data = parse(url)
    save(otc_output, data)
    return data

def gen_etf():
    url = 'https://mis.twse.com.tw/stock/data/all_etf.txt'
    data = xurl.load_json(url)
    parsed = {}
    for a1 in data.get('a1', []):
        for msg in a1.get('msgArray', []):
            code = msg['a']
            name = msg['b']
            parsed[code] = name
    save(etf_output, parsed)
    return parsed

def gen_overlap(output, a, b):
    data = {k:a[k] for k in a.keys() if k in b}
    save(output, data)
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

    parser = argparse.ArgumentParser()
    parser.add_argument('-v', '--verbose', action="store_true", default=False)
    args, unparsed = parser.parse_known_args()

    xurl.set_verbose(args.verbose)

    tse = gen_tse()
    otc = gen_otc()
    etf = gen_etf()
    gen_overlap(tse_etf_output, tse, etf)
    gen_overlap(otc_etf_output, otc, etf)
    test()

    return
 
if __name__ == '__main__':
    main()
