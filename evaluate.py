#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os
import argparse
import datetime
import quote
import copy
import numpy as np

class defs:
    code = '00662'
    limit = 1000000
    batch = '10'
    day_of_month = 15
    ma_days = 60
    mv_days = 60
    policy = 'pow5'

class bcolors:
    BLACK_ON_RED = '\x1b[3;30;41m'
    BLACK_ON_GREEN = '\x1b[3;30;42m'
    BLACK_ON_YELLOW = '\x1b[3;30;43m'
    BLACK_ON_BLUE = '\x1b[3;30;44m'
    BLACK_ON_WHITE = '\x1b[3;30;47m'
    RED = '\33[31m'
    GREEN = '\33[32m'
    YELLOW = '\33[33m'
    BLUE = '\33[34m'
    ENDC = '\x1b[0m'

class Record:
    def __init__(self, date, pz, cost):
        self.date = date
        self.pz = pz
        self.cost = cost

class Stock:
    def __init__(self, code, start, end):
        self.code = code
        self.cost = 0
        self.qty = 0
        self.avg = 0
        self.min_return = None
        self.min_return_date = None
        self.max_return = None
        self.max_return_date = None
        self.records = []
        self.df = quote.get_data(code, start, end)

    def add_cost(self, date, pz, cost):
        self.cost += cost
        self.qty += cost / pz
        self.avg = self.cost / self.qty
        self.records.append(Record(date, pz, cost))

    def get_price(self, date):
        df = self.df
        start = date - datetime.timedelta(days=30)
        vals = df[(df['date'] >= start) & (df['date'] <= date)]['close'].to_numpy()
        return vals[-1]

    def get_prices(self, date, days):
        df = self.df
        days = min(int(days * 7 / 5), 30)
        start = date - datetime.timedelta(days=days)
        vals = df[(df['date'] >= start) & (df['date'] <= date)]['close'].tail(days).to_numpy()
        return vals

    def get_ma(self, date, days):
        df = self.df
        days = min(int(days * 7 / 5), 30)
        start = date - datetime.timedelta(days=days)
        vals = df[(df['date'] >= start) & (df['date'] <= date)]['close'].tail(days).to_numpy()
        return vals.mean()

    def get_gain(self, pz):
        gain = int(pz * self.qty - self.cost)
        gain_percent = gain / self.cost
        return (gain, gain_percent)

    def get_return(self, date_a, date_b):
        date_a_pz = self.get_price(date_a)
        date_b_pz = self.get_price(date_b)
        return date_b_pz / date_a_pz - 1 if date_a_pz and date_b_pz else 0

    def check_performance(self, date):
        if self.cost:
            pz = self.get_price(date)
            gain, gain_percent = self.get_gain(pz)
            if not self.min_return or self.min_return > gain_percent:
                self.min_return = gain_percent
                self.min_return_date = date
            if not self.max_return or self.max_return < gain_percent:
                self.max_return = gain_percent
                self.max_return_date = date

class Action:
    def __init__(self, date, stock, pz, ma, rate, cost):
        self.date = date
        self.stock = stock
        self.pz = pz
        self.ma = ma
        self.rate = rate
        self.cost = cost

    def __str__(self):
        s = self.stock
        gain = self.pz / s.avg - 1
        return '[{}] {} pz {:,} ma {:,.2f} rate {:.2f} cost {:,} qty {:,.2f} avg {:,.2f} gain {:.2%}'.format(self.date, s.code, self.pz, self.ma, self.rate, self.cost, s.qty, s.avg, gain)

class Result:
    def __init__(self, args, stock, total_gain, total_return, annual_return):
        self.label = '{} b{}_{}'.format(stock.code, args.batch, args.policy)
        self.records = stock.records
        self.total_cost = stock.cost
        self.total_gain = total_gain
        self.total_return = total_return
        self.annual_return = annual_return
        self.worst_loss = stock.min_return or 0

    def __str__(self):
        return '{} freq {} return {:,.2%} (annual {:.2%}) worst {:.2%}'.format(self.label, len(self.records), self.total_return, self.annual_return, self.worst_loss)

def count_annualized_return(start, end, total_return):
    total_years = (end - start).days / 365.25
    annualized_return = (1 + total_return)**(1 / total_years) - 1
    return annualized_return

def evaluate_action(args, stock, date):

    action = None

    pz = stock.get_price(date)
    if not pz:
        return None

    ma = stock.get_ma(date, args.ma_days)
    unit = int(args.limit / int(args.batch))

    if args.policy.startswith('pow'):
        exp = int(args.policy[3:])
        rate = pow(max(ma/pz, stock.avg/pz, 1), exp)
        cost = int(unit * rate)
        action = Action(date, stock, pz, ma, rate, cost)

    elif args.policy.startswith('mul'):
        mul = int(args.policy[3:])
        rate = max(ma/pz, stock.avg/pz, 1) * mul - 1
        cost = int(unit * rate)
        action = Action(date, stock, pz, ma, rate, cost)

    return action

def core(args):

    start = datetime.datetime.strptime(args.start, '%Y%m%d')
    end = datetime.datetime.strptime(args.end, '%Y%m%d')

    stock = Stock(args.code, start, end)
    balance = args.limit

    print('\n---')
    print(bcolors.GREEN + '{} b{}_{} [{} ~ {}]'.format(args.code, args.batch, args.policy, start, end) + bcolors.ENDC)

    d = start
    while d <= end:
        if balance > 0 and d.day == args.day_of_month:
            action = evaluate_action(args, stock, d)
            if action:
                action.cost = min(action.cost, balance)
                action.stock.add_cost(d, action.pz, action.cost)
                balance -= action.cost
                print(action)

        stock.check_performance(d)
        d += datetime.timedelta(days=1)

    total_gain = 0
    total_return = 0
    annual_return = 0

    if stock.cost:
        label = bcolors.GREEN + '[{}] {}'.format(end, stock.code) + bcolors.ENDC
        pz = stock.get_price(end)
        total_gain, total_return = stock.get_gain(pz)
        annual_return = count_annualized_return(start, end, total_return)
        print('{} pz {} cost {:,} qty {:,.2f} avg {:,.2f} return {:.2%} (annual {:.2%})'.format(label, pz, stock.cost, stock.qty, stock.avg, total_return, annual_return))
        print('{} min {} {:.2%} max {} {:.2%}'.format(label, stock.min_return_date, stock.min_return, stock.max_return_date, stock.max_return))

    print('---')

    return Result(args, stock, total_gain, total_return, annual_return)

def main():

    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--code', default=defs.code)
    parser.add_argument('-s', '--start', default='')
    parser.add_argument('-e', '--end', default='')
    parser.add_argument('-l', '--limit', type=int, default=defs.limit)
    parser.add_argument('-b', '--batch', default=defs.batch)
    parser.add_argument('-d', '--day_of_month', type=int, default=defs.day_of_month)
    parser.add_argument('-A', '--ma_days', type=int, default=defs.ma_days)
    parser.add_argument('-V', '--mv_days', type=int, default=defs.mv_days)
    parser.add_argument('-p', '--policy', default=defs.policy)
    parser.add_argument('-v', '--verbose', action="store_true")

    args, unparsed = parser.parse_known_args()

    if len(unparsed) > 0:
        args.code = unparsed[0]

    if len(args.start) == 0:
        args.start = str(datetime.datetime.now().year) + '0101'
    elif len(args.start) == 4:
        args.start = args.start + '0101'
    elif len(args.start) == 6:
        args.start = args.start + '01'

    if len(args.end) == 0:
        args.end = datetime.datetime.now().strftime('%Y%m%d')
    elif len(args.end) == 4:
        args.end = args.end + '1231'
    elif len(args.end) == 6:
        args.end = args.end + '31'

    results = []
    for code in args.code.split(','):
        for batch in args.batch.split(','):
            for policy in args.policy.split(','):
                new_args = copy.deepcopy(args)
                new_args.code = code
                new_args.batch = batch
                new_args.policy = policy
                result = core(new_args)
                if result.total_cost:
                    results.append(result)
                if batch == '1':
                    break

    results.sort(key=lambda x: x.total_gain, reverse=True)

    print('\n---')
    for x in results:
        print(x)
    print('---')

    return

if __name__ == '__main__':
    main()
