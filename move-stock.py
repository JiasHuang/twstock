#!/usr/bin/python3
# -*- coding: utf-8 -*-

import argparse
import pandas

class Result:
    def __init__(self, sell, buy):
        self.s_unit = sell
        self.b_unit = buy
        self.s_cnt = 0
        self.b_cnt = 0
        self.s_amount = 0
        self.b_amount = 0
        self.diff = -1

    def evaluate(self, s_cnt):
        self.s_cnt = s_cnt
        self.s_amount = self.s_unit * s_cnt
        self.b_cnt = round(self.s_amount / self.b_unit)
        self.b_amount =  self.b_unit * self.b_cnt
        self.diff = self.s_amount - self.b_amount

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--sell')
    parser.add_argument('-b', '--buy')
    parser.add_argument('-a', '--amount')    
    args, unparsed = parser.parse_known_args()

    if len(unparsed) == 3:
        args.sell = unparsed[0]
        args.buy = unparsed[1]
        args.amount = unparsed[2]

    s_unit = float(args.sell) * 1000
    b_unit = float(args.buy) * 1000
    max_amount = float(args.amount)
    objs = []

    s_cnt = 1
    while True:
        obj = Result(s_unit, b_unit)
        obj.evaluate(s_cnt)
        objs.append(obj.__dict__)
        if obj.s_amount >= max_amount:
            break
        s_cnt += 1

    df = pandas.DataFrame(objs)
    df = df.sort_values(by='diff', key=abs)
    print(df)

    return

if __name__ == '__main__':
    main()
