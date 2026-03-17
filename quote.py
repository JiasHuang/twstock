#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os
import argparse
import datetime
import csv
import pandas as pd
import numpy as np
import talib
from talib import abstract
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.widgets import MultiCursor
from matplotlib.widgets import Cursor

import twse

cached = {}

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

class StockInfo:
    def __init__(self, row, ma_list):
        self.date = row['date'].date()
        attrs = ['open', 'high', 'low', 'close', 'volume']
        for ma in ma_list:
            attrs.append('ma'+str(ma))
        for attr in attrs:
            setattr(self, attr, getattr(row, attr))

def get_tick(pz):
    if pz < 10:
        return 0.01
    if pz < 50:
        return 0.05
    if pz < 100:
        return 0.1
    if pz < 500:
        return 0.5
    if pz < 1000:
        return 1
    return 5

def get_etf_tick(pz):
    if pz < 50:
        return 0.01
    return 0.05

def round_tick(pz, tick):
    return round(pz / tick) * tick

def get_exchange(code):
    exchanges = ['TPE', 'NASDAQ', 'NYSEARCA', 'NYSE', 'TSE', 'OTC']
    for exchange in exchanges:
        path = os.path.join(exchange, code + '.csv')
        if os.path.exists(path):
             return exchange
    return 'OTC' if twse.is_otc(code) else 'TSE'

def update_csv(path, exchange, code, start, end):
    if exchange in ['TSE', 'OTC']:
        data = twse.get_data(code, start, end)
        df = pd.DataFrame(data)
        if not os.path.exists(exchange):
            os.makedirs(exchange, exist_ok=True)
        df.to_csv(path, index=False, quotechar='"', quoting=csv.QUOTE_ALL)

def get_data(exchange, code, start, end):
    path = os.path.join(exchange, code) + '.csv'
    update_csv(path, exchange, code, start, end)

    if path not in cached:
        new_names = ['date', 'open', 'high', 'low', 'close', 'volume']
        cached[path] = pd.read_csv(path, names=new_names, header=0, parse_dates=['date'])

    df = cached[path]

    start_64 = np.datetime64(start)
    end_64 = np.datetime64(end)
    return df[(df['date'] >= start_64) & (df['date'] <= end_64)].copy()

def get_attrs(exchange, code, attr, end, days):
    start = end - datetime.timedelta(days=int(days * 1.5))
    df = get_data(exchange, code, start, end)
    return df[attr].tail(days).to_numpy()

def get_attr(exchange, code, attr, date):
    vals = get_attrs(exchange, code, attr, date, 30)
    return vals[0] if len(vals) else None

def get_ma(exchange, code, end, days):
    vals = get_attrs(exchange, code, "close", end, days)
    return vals.mean()

def get_ma_ratio(df, ma):
    low_vals = df['low'].to_numpy()
    ma_vals = df['ma'+str(ma)].to_numpy()
    ratios = low_vals / ma_vals
    return ratios[~np.isnan(ratios)]

def get_infos(exchange, code, start, end, ma_list):
    df = get_dataframe(exchange, code, start, end, ma_list)
    infos = [StockInfo(row, ma_list) for idx, row in df.iterrows()]
    return infos

def get_dataframe(exchange, code, start, end, ma_list):
    df = get_data(exchange, code, start, end)

    for ma in ma_list:
        df['ma'+str(ma)] = abstract.SMA(df, ma)

    #df.dropna(inplace=True)

    return df

def analyze(df, ma_list, label):

    pz = df['close'].iloc[-1]

    data = {}
    data['pz'] = pz
    for ma in [20, 60, 120, 240]:
        vals = df['close'].tail(ma).to_numpy()
        data['ma'+str(ma)] = vals.mean()

    for days in [60, 120, 240]:
        vals = df['close'].tail(days).to_numpy()
        data['lo' + str(days)] = np.min(vals)
        data['hi' + str(days)] = np.max(vals)

    print('---')
    for k, v in sorted(data.items(), key=lambda item: item[1], reverse=True):
        msg = '{} {:.2f} ({:+.2%})'.format(k, v, v/pz - 1)
        if k == 'pz':
            msg = bcolors.YELLOW + msg + bcolors.ENDC
        print('{} {}'.format(label, msg))

    print('---')
    for ma in ma_list:
        ma_val = df['ma'+str(ma)].iloc[-1]
        ma_ratio = get_ma_ratio(df, ma)
        if np.isnan(ma_val) or len(ma_ratio) == 0:
            continue
        max_ratio = max(ma_ratio)
        min_ratio = min(ma_ratio)
        max_pct = ((max_ratio - 1) * 100)
        min_pct = ((min_ratio - 1) * 100)
        data = {}
        data['pz'] = pz
        data['ma {:+.2f}%'.format(max_pct)] = ma_val * (1 + max_pct / 100)
        data['ma {:+.2f}%'.format(min_pct)] = ma_val * (1 + min_pct / 100)
        for pct in np.arange(-30, 30 + 2.5, 2.5):
            if pct < min_pct or pct > max_pct:
                continue
            data['ma {:+.2f}%'.format(pct)] = ma_val * (1 + pct / 100)
        for k, v in sorted(data.items(), key=lambda item: item[1], reverse=True):
            msg = '{} {:.2f}'.format(k, v)
            if k == 'pz':
                pct = (v / ma_val - 1) * 100
                msg = bcolors.YELLOW + 'pz {:+.2f}% {:.2f}'.format(pct, v) + bcolors.ENDC
            print('{} {}'.format(label, msg))

    return

def print_range(df, code, label):

    pz = df['close'].iloc[-1]
    tick = get_etf_tick(pz) if code.startswith('00') else get_tick(pz)

    print('---')
    for pct in np.arange(10, -11, -1):
        x = pz * (1 + pct / 100)
        msg = 'pz {:+d}% {:.2f} ({:.2f})'.format(pct, x, round_tick(x, tick))
        if pct == 0:
            msg = bcolors.YELLOW + msg + bcolors.ENDC
        print('{} {}'.format(label, msg))

    return

def get_percent_color(pct):
    if pct == 0:
        return 'black'
    if pct in [-10, 10]:
        return 'orange'
    if pct in [-20, 20]:
        return 'red'
    return 'grey'

def plot(df):

    height_ratios = [4, 1]
    fig, axes = plt.subplots(nrows=2, ncols=1, figsize=(20, 10), gridspec_kw={'height_ratios': height_ratios}, sharex=True)
    axes = axes.flatten()

    x = df['date'].to_numpy()

    axes[0].plot(x, df['close'].to_numpy(), zorder=10)
    for pct in np.arange(-20, 25, 5):
        axes[0].plot(x, df['ma60'].to_numpy() * (100 + pct) / 100, color=get_percent_color(pct), linestyle='dashed', linewidth=0.5, zorder=0)
    axes[0].set_ylabel('close')

    ma60_ratio = df['close'] / df['ma60'] - 1
    axes[1].plot(x, ma60_ratio.to_numpy(), zorder=10)
    for pct in np.arange(-20, 25, 5):
        axes[1].axhline(y=(pct/100), color=get_percent_color(pct), linestyle='dashed', linewidth=0.5, zorder=0)
    axes[1].set_ylabel('ma60_ratio')

    # Create the MultiCursor object
    # Pass the figure's canvas and a list of axes to the MultiCursor
    # Set vertOn=True to enable the vertical line, horizOn=False to disable the horizontal line
    # useblit=True provides faster drawing if supported by the backend
    cursor = MultiCursor(fig.canvas, axes, color='black', linewidth=1, vertOn=True, horizOn=False, useblit=True)
    cursor0 = Cursor(axes[0], useblit=True, color='red', linewidth=1)

    date_formatter = mdates.DateFormatter('%Y-%m-%d')
    axes[0].xaxis.set_major_formatter(date_formatter)
    # 4. Optional: improve readability by rotating labels
    plt.xticks(rotation=45, ha='right')

    plt.tight_layout()
    plt.show()

    return

def main():

    parser = argparse.ArgumentParser()
    parser.add_argument('-e', '--exchange')
    parser.add_argument('-c', '--code', nargs='+', default='2330')
    parser.add_argument('--ma', nargs='+', type=int, default=[60])
    parser.add_argument('-p', '--plot', action="store_true")
    parser.add_argument('-r', '--range', action="store_true")
    args, unparsed = parser.parse_known_args()

    if len(unparsed) > 0:
        args.code = unparsed

    for code in args.code:

        exchange = args.exchange or get_exchange(code)
        label = bcolors.GREEN + '{}:{}'.format(exchange, code) + bcolors.ENDC

        end = datetime.date.today()
        start = end - datetime.timedelta(days=540)
        df = get_dataframe(exchange, code, start, end, args.ma)
        print('---')
        print(df.tail(20).round(2))
        analyze(df, args.ma, label)

        if args.range:
            print_range(df, code, label)

        if args.plot:
            plot(df)

    return

if __name__ == '__main__':
    main()
