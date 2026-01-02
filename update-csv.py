#!/usr/bin/python3

import os
import re
import argparse

class defs:
    codes = ['0050', '00631L', '00646', '00647L', '00752']
    ID = '1Y3WzCZ2yuMKJvjNjK_f5vworkBUcGYRcRJGaRY7ivRA'

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--code')
    args = parser.parse_args()

    codes = args.code.split(',') or defs.codes

    for code in codes:
        cmd = 'curl -o TPE/{}.csv --create-dirs \"https://docs.google.com/spreadsheets/d/{}/gviz/tq?tqx=out:csv&sheet={}\"'.format(code, defs.ID, code)
        os.system(cmd)

    return

if __name__ == '__main__':
    main()
