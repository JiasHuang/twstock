#!/usr/bin/python3

import os

def init_file(d, n, text):
    local = os.path.join(d, n)
    if not os.path.exists(local):
        fd = open(local, 'w')
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
    init_file(d, 'exr.json', '{"ExchangeRates":[]}')

if __name__ == '__main__':
    main()
