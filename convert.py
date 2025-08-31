#!/usr/bin/python3

import os
import glob
import argparse

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--src', default='webp')
    parser.add_argument('-d', '--dst', default='jpg')
    args = parser.parse_args()
    files = []
    files.extend(glob.glob('*.' + args.src))
    for f in files:
        dst = f + '.jpg'
        print(f)
        os.system('convert \'%s\' \'%s\'' %(f, dst))
        os.system('rm -f \'%s\'' %(f))
    return

if __name__ == '__main__':
    main()
