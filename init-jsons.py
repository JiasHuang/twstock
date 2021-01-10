#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os

def init_file(d, n, text, buffering=-1):
    local = os.path.join(d, n)
    if not os.path.exists(local):
        fd = open(local, 'w', buffering)
        fd.write(text)
        fd.close()
        print(local)
    return

def main():
    d = os.path.realpath('jsons')
    if not os.path.exists(d):
        os.makedirs(d)
    init_file(d, 'stocks.json', '{"stocks":[]}')
    init_file(d, 'strategy.json', '{"stocks":[]}')
    init_file(d, 'account.json', '{"stocks":[]}')
    init_file(d, 'exr.json', '{"ExchangeRates":[]}')

if __name__ == '__main__':
    main()
