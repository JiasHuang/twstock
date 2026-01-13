#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os
import argparse
import datetime
import google_finance_csv
import copy

class defs:
    code = '00662'
    limit = 1000000
    batch = '10'
    day_of_month = 15
    sma_days = 60
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

    def get_prices(self, date, days):
        return google_finance_csv.get_prices(self.exchange, self.code, date, days)

    def get_sma(self, date, days):
        return google_finance_csv.get_sma(self.exchange, self.code, date, days)

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
    def __init__(self, date, stock, pz, sma, cost):
        self.date = date
        self.stock = stock
        self.pz = pz
        self.sma = sma
        self.cost = cost

    def __str__(self):
        s = self.stock
        gain = self.pz / s.avg - 1
        return '[{}] {}:{} pz {:,} sma {:,.2f} cost {:,} qty {:,.2f} avg {:,.2f} gain {:.2%}'.format(self.date, s.exchange, s.code, self.pz, self.sma, self.cost, s.qty, s.avg, gain)

class Result:
    def __init__(self, args, stock, total_gain, total_return, annual_return):
        self.label = '{}:{} b{}_{}'.format(stock.exchange, stock.code, args.batch, args.policy)
        self.records = stock.records
        self.total_cost = stock.cost
        self.total_gain = total_gain
        self.total_return = total_return
        self.annual_return = annual_return
        self.worst_loss = stock.min_return or 0

    def __str__(self):
        return '{} freq {} return {:,.2%} (annual {:.2%}) worst {:.2%}'.format(self.label, len(self.records), self.total_return, self.annual_return, self.worst_loss)

def get_exchange(code):
    exchanges = ['TPE', 'NASDAQ', 'NYSEARCA', 'NYSE']
    for exchange in exchanges:
        csv = os.path.join(exchange, code + '.csv')
        if os.path.exists(csv):
             return exchange
    return None

def count_annualized_return(start, end, total_return):
    total_years = (end - start).days / 365.25
    annualized_return = (1 + total_return)**(1 / total_years) - 1
    return annualized_return

def evaluate_action(args, stock, date):

    action = None

    pz = stock.get_price(date)
    if not pz:
        return None

    sma = stock.get_sma(date, args.sma_days)
    unit = int(args.limit / int(args.batch))

    if args.policy.startswith('pow'):
        exp = int(args.policy[3:])
        rate = max(sma/pz, stock.avg/pz, 1)
        cost = int(unit * pow(rate, exp))
        action = Action(date, stock, pz, sma, cost)

    elif args.policy.startswith('mul'):
        mul = int(args.policy[3:])
        rate = max(sma/pz, stock.avg/pz, 1)
        cost = int(unit * (rate * mul - 1))
        action = Action(date, stock, pz, sma, cost)

    return action

def analyze(args):

    start = datetime.datetime.strptime(args.start, '%Y%m%d').date()
    end = datetime.datetime.strptime(args.end, '%Y%m%d').date()

    stock = Stock(args.exchange, args.code)
    label = bcolors.GREEN + '{}:{}'.format(stock.exchange, stock.code) + bcolors.ENDC

    for y in range(start.year, end.year + 1):

        year_start = datetime.datetime.strptime(str(y) + '0101', '%Y%m%d').date()
        year_end = datetime.datetime.strptime(str(y) + '1231', '%Y%m%d').date()
        year_return = stock.get_return(year_start, year_end)
        year_sma_rates = []

        for m in range(1, 13):
            for x in [1, 5, 10, 15, 20, 25]:

                d = datetime.date(y, m, x)
                if d < start or d > end:
                    continue

                pz = stock.get_price(d)
                if not pz:
                    continue

                sma = stock.get_sma(d, args.sma_days)
                year_sma_rates.append(pz / sma - 1)

        year_sma_rate_min = min(year_sma_rates)
        year_sma_rate_avg = sum(year_sma_rates) / len(year_sma_rates)
        print('{} {} ~ {} return {:.2%} sma_rate (min {:.2%} avg {:.2%})'.format(label, year_start, year_end, year_return, year_sma_rate_min, year_sma_rate_avg))

    pz = stock.get_price(end)
    pz_s = stock.get_price(start)
    total_return = pz / pz_s - 1
    annual_return = count_annualized_return(start, end, total_return)
    print('{} {} ~ {} return {:.2%} (annual {:.2%})'.format(label, start, end, total_return, annual_return))

    vals = {}
    vals['*** pz ***'] = pz
    vals['sma5'] = stock.get_sma(end, 5)
    vals['sma10'] = stock.get_sma(end, 10)
    vals['sma20'] = stock.get_sma(end, 20)
    vals['sma60'] = stock.get_sma(end, 60)
    vals['sma120'] = stock.get_sma(end, 120)
    vals['sma240'] = stock.get_sma(end, 240)

    for days in [60, 120, 240]:
        pzs = stock.get_prices(end, days)
        vals['low' + str(days)] = min(pzs)

    print('---')
    for k, v in sorted(vals.items(), key=lambda item: item[1], reverse=True):
        print('{} {} {:.2f} ({:.2%})'.format(label, k, v, v/pz-1))

    return

def regression(args):

    ystart = int(args.regression)
    yend = datetime.date.today().year
    rank = {}

    for y in range(ystart, yend + 1):
        results = []
        for code in args.code.split(','):
            for batch in args.batch.split(','):
                for policy in args.policy.split(','):
                    new_args = copy.deepcopy(args)
                    new_args.start = str(y) + '0101'
                    new_args.code = code
                    new_args.batch = batch
                    new_args.policy = policy
                    ret = core(new_args)
                    if ret.total_cost:
                        results.append(ret)
                        if ret.label not in rank:
                            rank[ret.label] = ret.total_gain
                        else:
                            rank[ret.label] += ret.total_gain
                    if batch == '1':
                        break

        results.sort(key=lambda x: x.total_gain, reverse=True)

        print('\n---')
        for x in results:
            print(x)
        print('---')

    print('\n---')
    for k, v in sorted(rank.items(), key=lambda item: item[1], reverse=True):
        print('{}: {:,}'.format(k, v))
    print('---')

    return

def core(args):

    start = datetime.datetime.strptime(args.start, '%Y%m%d').date()
    end = datetime.datetime.strptime(args.end, '%Y%m%d').date()

    stock = Stock(args.exchange, args.code)
    balance = args.limit

    print('\n---')
    print(bcolors.GREEN + '{}:{} b{}_{} [{} ~ {}]'.format(args.exchange, args.code, args.batch, args.policy, start, end) + bcolors.ENDC)

    for y in range(start.year, end.year + 1):
        for m in range(1, 13):

            d = datetime.date(y, m, args.day_of_month)
            if d < start or d > end:
                continue

            stock.check_performance(d)

            if balance <= 0:
                stock.check_performance(d)
                continue

            action = evaluate_action(args, stock, d)
            if action:
                action.cost = min(action.cost, balance)
                action.stock.add_cost(d, action.pz, action.cost)
                balance -= action.cost
                stock.check_performance(d)
                if args.verbose:
                    print(action)

    total_gain = 0
    total_return = 0
    annual_return = 0

    if stock.cost:
        label = bcolors.GREEN + '[{}] {}:{}'.format(end, stock.exchange, stock.code) + bcolors.ENDC
        pz = stock.get_price(end)
        total_gain, total_return = stock.get_gain(pz)
        annual_return = count_annualized_return(start, end, total_return)
        print('{} pz {} cost {:,} qty {:,.2f} avg {:,.2f} return {:.2%} (annual {:.2%})'.format(label, pz, stock.cost, stock.qty, stock.avg, total_return, annual_return))
        print('{} min {:.2%} max {:.2%}'.format(label, stock.min_return, stock.max_return))

    print('---')

    return Result(args, stock, total_gain, total_return, annual_return)

def main():

    parser = argparse.ArgumentParser()
    parser.add_argument('-E', '--exchange')
    parser.add_argument('-c', '--code', default=defs.code)
    parser.add_argument('-s', '--start', default='')
    parser.add_argument('-e', '--end', default='')
    parser.add_argument('-l', '--limit', type=int, default=defs.limit)
    parser.add_argument('-b', '--batch', default=defs.batch)
    parser.add_argument('-d', '--day_of_month', type=int, default=defs.day_of_month)
    parser.add_argument('-S', '--sma_days', type=int, default=defs.sma_days)
    parser.add_argument('-p', '--policy', default=defs.policy)
    parser.add_argument('-v', '--verbose', action="store_true")
    parser.add_argument('-a', '--analyze', action="store_true")
    parser.add_argument('-r', '--regression')

    args, unparsed = parser.parse_known_args()

    if len(args.start) == 0:
        args.start = str(datetime.date.today().year) + '0101'
    elif len(args.start) == 4:
        args.start = args.start + '0101'
    elif len(args.start) == 6:
        args.start = args.start + '01'

    if len(args.end) == 0:
        args.end = datetime.date.today().strftime('%Y%m%d')
    elif len(args.end) == 4:
        args.end = args.end + '1231'
    elif len(args.end) == 6:
        args.end = args.end + '31'

    if args.analyze:
        for code in args.code.split(','):
            new_args = copy.deepcopy(args)
            new_args.code = code
            new_args.exchange = args.exchange or get_exchange(code)
            analyze(new_args)
        return

    if args.regression:
        regression(args)
        return

    results = []
    for code in args.code.split(','):
        for batch in args.batch.split(','):
            for policy in args.policy.split(','):
                new_args = copy.deepcopy(args)
                new_args.code = code
                new_args.batch = batch
                new_args.policy = policy
                new_args.exchange = args.exchange or get_exchange(code)
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
