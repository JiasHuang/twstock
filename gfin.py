#!/usr/bin/python3

import os
import re
import time
import argparse

class defvals:
    expiration = 86400
    spreadsheets = '1Y3WzCZ2yuMKJvjNjK_f5vworkBUcGYRcRJGaRY7ivRA'
    sheets = ['SPY', 'VOO', 'LQD', 'QLD', 'QQQ', 'TLT', 'TPE_ETF']

def is_expired(path, expiration=defvals.expiration):
    if os.path.exists(path):
        t0 = int(os.path.getmtime(path))
        t1 = int(time.time())
        return (t1 - t0) > expiration
    return True

def load_sheet(sheet, expiration=defvals.expiration):
    output = 'csv/{}.csv'.format(sheet)
    if not is_expired(output, expiration):
        return output
    cmd = 'curl -s -o {} --create-dirs \"https://docs.google.com/spreadsheets/d/{}/gviz/tq?tqx=out:csv&sheet={}\"'.format(output, defvals.spreadsheets, sheet)
    os.system(cmd)
    return

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-v', '--verbose', action="store_true", default=False)
    parser.add_argument('-e', '--expiration', type=int, default=defvals.expiration)
    args, unparsed = parser.parse_known_args()

    for sheet in defvals.sheets:
        load_sheet(sheet, args.expiration)

    return

if __name__ == '__main__':
    main()
