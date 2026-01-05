#!/usr/bin/python3

import os
import re
import argparse

class defs:
    tickers = 'TPE:0050,TPE:00631L,TPE:00646,TPE:00647L,TPE:00752,TPE:00662'
    ID = '1Y3WzCZ2yuMKJvjNjK_f5vworkBUcGYRcRJGaRY7ivRA'

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-t', '--tickers', default=defs.tickers)
    args = parser.parse_args()

    for ticker in args.tickers.split(','):
        [exchange, code] = ticker.split(':')
        cmd = 'curl -o {}/{}.csv --create-dirs \"https://docs.google.com/spreadsheets/d/{}/gviz/tq?tqx=out:csv&sheet={}\"'.format(exchange, code, defs.ID, code)
        os.system(cmd)

    return

if __name__ == '__main__':
    main()
