#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os
import argparse
import datetime
import google_finance_csv
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

    def get_infos(self, start, end, ma_list):
        return google_finance_csv.get_infos(self.exchange, self.code, start, end, ma_list)

    def get_price(self, date):
        return google_finance_csv.get_attr(self.exchange, self.code, 'close', date)

    def get_prices(self, date, days):
        return google_finance_csv.get_attrs(self.exchange, self.code, 'close', date, days)

    def get_ma(self, date, days):
        return google_finance_csv.get_ma(self.exchange, self.code, date, days)

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
    def __init__(self, date, stock, pz, ma, cost):
        self.date = date
        self.stock = stock
        self.pz = pz
        self.ma = ma
        self.cost = cost

    def __str__(self):
        s = self.stock
        gain = self.pz / s.avg - 1
        return '[{}] {}:{} pz {:,} ma {:,.2f} cost {:,} qty {:,.2f} avg {:,.2f} gain {:.2%}'.format(self.date, s.exchange, s.code, self.pz, self.ma, self.cost, s.qty, s.avg, gain)

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
        rate = max(ma/pz, stock.avg/pz, 1)
        cost = int(unit * pow(rate, exp))
        action = Action(date, stock, pz, ma, cost)

    elif args.policy.startswith('mul'):
        mul = int(args.policy[3:])
        rate = max(ma/pz, stock.avg/pz, 1)
        cost = int(unit * (rate * mul - 1))
        action = Action(date, stock, pz, ma, cost)

    return action

def analyze(args):

    start = datetime.datetime.strptime(args.start, '%Y%m%d').date()
    end = datetime.datetime.strptime(args.end, '%Y%m%d').date()

    stock = Stock(args.exchange, args.code)
    label = bcolors.GREEN + '{}:{}'.format(stock.exchange, stock.code) + bcolors.ENDC

    print('\n---')

    ma_list = [60]
    interval = 20
    infos = stock.get_infos(start, end, ma_list)
    avg_vol = np.mean([x.volume for x in infos])
    for idx, x in enumerate(infos):
        if idx > interval and idx + interval < len(infos):
            vals = [y.close for y in infos[idx - interval:idx + interval]]
            if infos[idx].close == max(vals):
                infos[idx].desc.append('high')
            if infos[idx].close == min(vals):
                infos[idx].desc.append('low')

    for idx, x in enumerate(infos):
        if x.desc or idx > len(infos) - 10:
            basic = []
            for ma in ma_list:
                rate = x.close / getattr(x, 'ma'+str(ma)) - 1
                basic.append('ma{} {:+.2%}'.format(ma, rate))
            basic.append('vol {:+.2%}'.format(x.volume / avg_vol - 1))
            print('{} {} {:.2f} {} {}'.format(label, x.date, x.close, ' '.join(basic), ' '.join(x.desc)))

    print('---')
    idx = max(0, len(infos) - 120)
    while idx < len(infos):
        week_num = infos[idx].date.isocalendar()[1]
        week = [infos[idx]]
        for idx2 in range(idx + 1, len(infos)):
            if infos[idx2].date.isocalendar()[1] != week_num:
                break
            week.append(infos[idx2])

        last_close = infos[max(idx - 1, 0)].close
        wk_return = week[-1].close / last_close - 1
        wk_vol = np.mean([y.volume for y in week]) / avg_vol - 1
        wk_low = min([y.low for y in week])
        print('{} {} ~ {} (w{}) {:.2f} return {:.2%} vol {:+.2%} low {:.2f}'.format(label, week[0].date, week[-1].date, week_num, week[-1].close, wk_return, wk_vol, wk_low))
        idx = idx + len(week)

    pz = infos[-1].close

    print('---')
    idxs = [0, len(infos) - 120, len(infos) - 60, len(infos) - 20]
    for idx in idxs:
        if idx < 0:
            continue
        pz_s = infos[idx].close
        total_return = pz / pz_s - 1
        annual_return = count_annualized_return(infos[idx].date, end, total_return)
        diff_in_month = round((end - infos[idx].date).days / 30, 1)
        print('{} {} ~ {} ({}m) return {:.2%} (annual {:.2%})'.format(label, infos[idx].date, end, diff_in_month, total_return, annual_return))

    vals = {}
    vals['*** pz ***'] = pz
    for ma in [5, 10, 20, 60, 120, 240]:
        vals['ma'+str(ma)] = stock.get_ma(end, ma)

    for days in [60, 120, 240]:
        pzs = stock.get_prices(end, days)
        vals['low' + str(days)] = min(pzs)

    print('---')
    for k, v in sorted(vals.items(), key=lambda item: item[1], reverse=True):
        print('{} {} {:.2f} ({:+.2%})'.format(label, k, v, pz/v-1))

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
    parser.add_argument('-A', '--ma_days', type=int, default=defs.ma_days)
    parser.add_argument('-V', '--mv_days', type=int, default=defs.mv_days)
    parser.add_argument('-p', '--policy', default=defs.policy)
    parser.add_argument('-v', '--verbose', action="store_true")
    parser.add_argument('-a', '--analyze', action="store_true")
    parser.add_argument('-r', '--regression')

    args, unparsed = parser.parse_known_args()

    if len(args.start) == 0:
        if args.analyze:
            args.start = (datetime.date.today() - datetime.timedelta(days=365)).strftime('%Y%m%d')
        else:
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
            new_args.exchange = args.exchange or google_finance_csv.get_exchange(code)
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
                new_args.exchange = args.exchange or google_finance_csv.get_exchange(code)
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
