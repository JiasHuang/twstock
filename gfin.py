#!/usr/bin/python3

import os
import re
import time
import argparse
import pandas as pd

class defvals:
    expiration = 86400
    spreadsheets = '1Y3WzCZ2yuMKJvjNjK_f5vworkBUcGYRcRJGaRY7ivRA'
    cached = {}
    verbose = False

def is_cached(path, expiration):
    if os.path.exists(path):
        t0 = os.path.getmtime(path)
        t1 = time.time()
        return (t1 - t0) <= expiration
    return False

def load_sheet(sheet, expiration=defvals.expiration):
    output = 'csv/{}.csv'.format(sheet)
    if is_cached(output, expiration):
        return output
    cmd = 'curl -s -o {} --create-dirs \"https://docs.google.com/spreadsheets/d/{}/gviz/tq?tqx=out:csv&sheet={}\"'.format(output, defvals.spreadsheets, sheet)

    if defvals.verbose:
        print(cmd)

    os.system(cmd)
    return output

def load_df(sheet, expiration=defvals.expiration):
    if sheet in defvals.cached and (time.time() - defvals.cached[sheet]['t']) <= expiration:
        return defvals.cached[sheet]['df']

    path = load_sheet(sheet, expiration)
    new_names = ['code', 'name', 'z', 'y', 'h', 'l', 'v', 'days_hi', 'days_lo', 'ma', 'mv']
    df = pd.read_csv(path, names=new_names, header=0, dtype={'code':str})
    defvals.cached[sheet] = {'df':df, 't':os.path.getmtime(path)}

    return df

def query(code):
    df = load_df('TPE_ETF') if code.startswith('00') else load_df('TPE')
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

    defvals.verbose = args.verbose

    if args.sheet:
        ret = load_sheet(args.sheet, args.expiration)
        print(ret)

    if args.code:
        ret = query(args.code)
        print(ret)

    return

if __name__ == '__main__':
    main()
