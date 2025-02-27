#!/usr/bin/python3
# -*- coding: utf-8 -*-

import argparse
import code
import pandas
import json
import tabulate

import twse
import yuanta
import ctbc

def parse(code):
    basic = yuanta.parse(code) or ctbc.parse(code)
    curr_info = twse.get_stock_info(code)
    if basic and curr_info:
        p = curr_info['price']
        nav = basic['nav']
        eps = basic['eps']
        d = {}
        d['code'] = code
        d['price'] = p
        d['NAV'] = nav
        d['EPS'] = eps
        d['PB'] = p / nav
        d['PE'] = p / eps if eps else 0
        d['ROE'] = eps / nav * 100 if nav else 0
        d['name'] = curr_info['n']
        return d
    return None

def main():
    parser = argparse.ArgumentParser()
    args, unparsed = parser.parse_known_args()

    codes = []
    
    if unparsed:
        codes = unparsed[0].split(',')
    else:
        codes.extend(yuanta.codes)
        codes.extend(ctbc.codes)

    objs = []
    for code in codes:
        obj = parse(code)
        if obj:
            objs.append(obj)

    df = pandas.DataFrame(objs)
    print(tabulate.tabulate(df, floatfmt='.2f', headers=df.columns))

    return

if __name__ == '__main__':
    main()
