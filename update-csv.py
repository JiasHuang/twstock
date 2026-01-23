#!/usr/bin/python3

import os
import re
import argparse

class defs:
    TPE = ['0050', '00631L', '00657L', '00670L', '00646', '00662', '2330']
    NYSEARCA = ['SPY', 'QQQ', 'LQD', 'QLD']
    NASDAQ = ['QQQ', 'TLT']
    NYSE = ['TSM']
    ID = '1Y3WzCZ2yuMKJvjNjK_f5vworkBUcGYRcRJGaRY7ivRA'

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-t', '--tickers')
    args = parser.parse_args()

    if not args.tickers:
        tickers = []
        for attr in ['TPE', 'NYSEARCA', 'NASDAQ', 'NYSE']:
            tickers.extend([attr + ':' + x for x in getattr(defs, attr)])
        args.tickers = ','.join(tickers)

    for ticker in args.tickers.split(','):
        [exchange, code] = ticker.split(':')
        cmd = 'curl -o {}/{}.csv --create-dirs \"https://docs.google.com/spreadsheets/d/{}/gviz/tq?tqx=out:csv&sheet={}\"'.format(exchange, code, defs.ID, code)
        os.system(cmd)

    return

if __name__ == '__main__':
    main()
