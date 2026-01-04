#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os
import argparse
import datetime
import google_finance_csv
import copy

class defs:
    etf_x2_map = {'0050':'00631L', '00646':'00647L'}

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
    def __init__(self, exchange, code):
        self.exchange = exchange
        self.code = code
        self.cost = 0
        self.qty = 0
        self.avg = 0
        self.min_return = None
        self.min_return_date = None
        self.max_return = None
        self.max_return_date = None
        self.records = []

    def add_cost(self, date, pz, cost):
        self.cost += cost
        self.qty += cost / pz
        self.avg = self.cost / self.qty
        self.records.append(Record(date, pz, cost))

    def get_price(self, date):
        return google_finance_csv.get_price(self.exchange, self.code, date)

    def get_sma(self, date, days):
        return google_finance_csv.get_sma(self.exchange, self.code, date, days)

    def get_gain(self, pz):
        gain = int(pz * self.qty - self.cost)
        gain_percent = gain / self.cost
        return (gain, gain_percent)

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
    def __init__(self, date, stock, pz, sma, cost):
        self.date = date
        self.stock = stock
        self.pz = pz
        self.sma = sma
        self.cost = cost

    def __str__(self):
        s = self.stock
        gain = self.pz / self.stock.avg - 1
        return '[{}] {}:{} pz {:,} sma {:,.2f} cost {:,} qty {:,.2f} avg {:,.2f} gain {:.2%}'.format(self.date, s.exchange, s.code, self.pz, self.sma, self.cost, s.qty, s.avg, gain)

def count_annualized_return(start, end, total_return):
    total_years = (end - start).days / 365.25
    annualized_return = (1 + total_return)**(1 / total_years) - 1
    return annualized_return

def evaluate_actions(args, stock, stock2, date):

    actions = []

    pz = stock.get_price(date)
    if not pz:
        return []

    sma = stock.get_sma(date, args.sma_days)

    if args.policy.startswith('pow'):
        exp = int(args.policy[3:])
        rate = max(sma/pz, stock.avg/pz, 1)
        cost = int(args.unit * pow(rate, exp))
        actions.append(Action(date, stock, pz, sma, cost))

    elif args.policy.startswith('mul'):
        mul = int(args.policy[3:])
        rate = max(sma/pz, stock.avg/pz, 1)
        cost = int(args.unit * (rate * mul - 1))
        actions.append(Action(date, stock, pz, sma, cost))

    elif args.policy == 'x2':
        pz2 = stock2.get_price(date)
        if pz2:
            sma2 = stock2.get_sma(date, args.sma_days)
            rate2 = sma2 / pz2
            if rate2 >= 1.1:
                cost2 = int(args.unit * pow(rate2, 2))
                actions.append(Action(date, stock2, pz2, sma2, cost2))
        if not actions:
            rate = max(sma/pz, stock.avg/pz, 1)
            cost = int(args.unit * pow(rate, 2))
            actions.append(Action(date, stock, pz, sma, cost))

    elif args.policy == 'fb':
        rate = max(sma/pz, stock.avg/pz, 1)
        cost = int(args.unit * pow(rate, 2))
        if (stock.avg/pz) >= 1.1:
            cost = max(cost, int(stock.qty * pz))
        actions.append(Action(date, stock, pz, sma, cost))

    return actions

def core(args):

    start = datetime.datetime.strptime(args.start, '%Y%m%d').date()
    end = datetime.datetime.strptime(args.end, '%Y%m%d').date()

    stock = Stock(args.exchange, args.code)
    stock2 = Stock(args.exchange, args.code2)
    balance = args.limit

    for y in range(start.year, end.year + 1):
        for m in range(1, 13):

            d = datetime.date(y, m, args.day)
            if d > end:
                continue

            stock.check_performance(d)
            stock2.check_performance(d)

            if d < start or d > end:
                continue

            if balance <= 0:
                continue

            actions = evaluate_actions(args, stock, stock2, d)
            for action in actions:
                action.cost = min(action.cost, balance)
                action.stock.add_cost(d, action.pz, action.cost)
                balance -= action.cost
                if args.verbose:
                    print(action)

    total_cost = 0
    total_gain = 0

    print('\n---')
    print(bcolors.GREEN + '[{}] ~ [{}] {}:{} Policy {}'.format(start, end, args.exchange, args.code, args.policy) + bcolors.ENDC)

    for s in [stock, stock2]:
        if s.cost:
            pz = s.get_price(end)
            gain, gain_percent = s.get_gain(pz)
            total_cost += s.cost
            total_gain += gain
            label = bcolors.YELLOW + s.exchange + ":" + s.code + bcolors.ENDC
            print('{} cost {:,} qty {:,.2f} avg {:,.2f} gain {:,} ({:.2%})'.format(label, s.cost, s.qty, s.avg, gain, gain_percent))
            print('{} min: {} {:.2%}'.format(label, s.min_return_date, s.min_return))
            print('{} max: {} {:.2%}'.format(label, s.max_return_date, s.max_return))
            print('{} {} ~ {} ({})'.format(label, s.records[0].date, s.records[-1].date, len(s.records)))

    total_return = total_gain / total_cost
    annual_return = count_annualized_return(start, end, total_return)

    pz_start = stock.get_price(start)
    pz_end = stock.get_price(end)
    pz_return = (pz_end - pz_start) / pz_start - 1
    pz_annual_return = count_annualized_return(start, end, pz_return)

    print('Total: cost {:,} gain {:,} ({:.2%}) (annual {:.2%})'.format(total_cost, total_gain, total_return, annual_return))
    print('Price: {:.2%} (annual {:.2%})'.format(pz_return, pz_annual_return))
    print('---')

    return

def main():

    parser = argparse.ArgumentParser()
    parser.add_argument('-E', '--exchange', default='TPE')
    parser.add_argument('-c', '--code', default='0050')
    parser.add_argument('-C', '--code2')
    parser.add_argument('-s', '--start', default='2020')
    parser.add_argument('-e', '--end', default='')
    parser.add_argument('-u', '--unit', type=int, default=50000)
    parser.add_argument('-l', '--limit', type=int, default=3000000)
    parser.add_argument('-d', '--day', type=int, default=15)
    parser.add_argument('-S', '--sma_days', type=int, default=60)
    parser.add_argument('-p', '--policy', default='pow2')
    parser.add_argument('-v', '--verbose', type=int, default=1)
    args, unparsed = parser.parse_known_args()

    if len(args.start) == 4:
        args.start = args.start + '0101'
    elif len(args.start) == 6:
        args.start = args.start + '01'

    if len(args.end) == 0:
        args.end = datetime.date.today().strftime('%Y%m%d')
    elif len(args.end) == 4:
        args.end = args.end + '1231'
    elif len(args.end) == 6:
        args.end = args.end + '31'

    codes = args.code.split(',')
    code2 = args.code2
    policies = args.policy.split(',')
    for code in codes:
        for policy in policies:
            new_args = copy.deepcopy(args)
            if policy == 'x2' and not code2:
                new_args.code2 = defs.etf_x2_map[code]
            new_args.code = code
            new_args.policy = policy
            core(new_args)

    return

if __name__ == '__main__':
    main()
