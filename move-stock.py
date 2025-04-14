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
    parser.add_argument('-s', '--sell',type=float, default=10)
    parser.add_argument('-b', '--buy', type=float, default=10)
    parser.add_argument('-a', '--amount', type=float, default=500000)
    args, unparsed = parser.parse_known_args()

    if len(unparsed) > 0:
        args.sell = float(unparsed[0])

    if len(unparsed) > 1:
        args.buy = float(unparsed[1])

    if len(unparsed) > 2:
        args.amount = float(unparsed[2])

    s_unit = args.sell * 1000
    b_unit = args.buy * 1000
    max_amount = args.amount
    objs = []

    s_cnt = 1
    while True:
        obj = Result(s_unit, b_unit)
        obj.evaluate(s_cnt)
        objs.append(obj.__dict__)
        if max(obj.s_amount, obj.b_amount) >= max_amount:
            break
        s_cnt += 1

    df = pandas.DataFrame(objs)
    df = df.sort_values(by='diff', key=abs)
    print(df)

    return

if __name__ == '__main__':
    main()
