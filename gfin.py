#!/usr/bin/python3

import os
import re
import time
import argparse
import pandas as pd

class defvals:
    expiration = 86400
    spreadsheets = '1Y3WzCZ2yuMKJvjNjK_f5vworkBUcGYRcRJGaRY7ivRA'
    sheets = ['SPY', 'VOO', 'LQD', 'QLD', 'QQQ', 'TLT', 'TPE_ETF']

def is_expired(path, expiration):
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
    return output

def load_df(sheet, expiration=defvals.expiration):
    path = load_sheet(sheet, expiration)
    new_names = ['code', 'name', 'z', 'y', 'h', 'l', 'v', 'days_hi', 'days_lo', 'ma', 'mv']
    df = pd.read_csv(path, names=new_names, header=0)
    return df

def query(df, code):
    flt = df[df['code'] == code]
    if len(flt.index):
        return flt.iloc[0].to_dict()
    return None


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-v', '--verbose', action="store_true", default=False)
    parser.add_argument('-e', '--expiration', type=int, default=defvals.expiration)
    parser.add_argument('-s', '--sheet')
    parser.add_argument('-c', '--code')
    args, unparsed = parser.parse_known_args()

    if args.sheet:
        ret = load_sheet(args.sheet, args.expiration)
        print(ret)

    if args.code:
        df = load_df('TPE_ETF')
        ret = get_dict(df, args.code)
        print(ret)

    return

if __name__ == '__main__':
    main()
