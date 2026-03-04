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
import tse
import otc

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

def round_tick(pz):
    tick = get_tick(pz)
    return round(pz / tick) * tick

def get_exchange(code):
    exchanges = ['TPE', 'NASDAQ', 'NYSEARCA', 'NYSE', 'TSE', 'OTC']
    for exchange in exchanges:
        path = os.path.join(exchange, code + '.csv')
        if os.path.exists(path):
             return exchange
    if tse.has_code(code):
        return 'TSE'
    if otc.has_code(code):
        return 'OTC'
    assert False, 'exchange not found'
    return None

def update_csv(path, exchange, code):
    if exchange in ['TSE', 'OTC']:
        start = '20250101'
        data = tse.get_data(code, start) if exchange == 'TSE' else otc.get_data(code, start)
        df = pd.DataFrame(data)
        if not os.path.exists(exchange):
            os.makedirs(exchange, exist_ok=True)
        df.to_csv(path, index=False, quotechar='"', quoting=csv.QUOTE_ALL)

def get_data(exchange, code, start=None, end=None):
    path = os.path.join(exchange, code) + '.csv'
    update_csv(path, exchange, code)

    if path not in cached:
        new_names = ['date', 'open', 'high', 'low', 'close', 'volume']
        cached[path] = pd.read_csv(path, names=new_names, header=0, parse_dates=['date'])

    df = cached[path]

    if start and end:
        start_64 = np.datetime64(start)
        end_64 = np.datetime64(end)
        return df[(df['date'] >= start_64) & (df['date'] <= end_64)].copy()

    elif start:
        start_64 = np.datetime64(start)
        return df[df['date'] >= start_64].copy()

    elif end:
        end_64 = np.datetime64(end)
        return df[df['date'] <= end_64].copy()

    return df

def get_attrs(exchange, code, attr, date, days):
    df = get_data(exchange, code, end=date)
    return df[attr].tail(days).to_numpy()

def get_attr(exchange, code, attr, date):
    vals = get_attrs(exchange, code, attr, date, 1)
    return vals[0] if vals else None

def get_ma(exchange, code, date, days):
    vals = get_attrs(exchange, code, "close", date, days)
    return vals.mean()

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
        if k == 'pz':
            k = bcolors.YELLOW + 'pz' + bcolors.ENDC
        print('{} {} {:.2f} ({:+.2%})'.format(label, k, v, v/pz-1))

    print('---')
    for ma in ma_list:
        low_vals = df['low'].to_numpy()
        ma_vals = df['ma'+str(ma)].to_numpy()
        rates = low_vals / ma_vals
        ref_ma = ma_vals[-1]
        ref_rate = min(rates[~np.isnan(rates)])
        for rate in [ref_rate, 0.95, 0.9, 0.85, 0.8]:
            x = ref_ma * rate
            print('{} ref_ma{} {:.2f} x {:.2f} = {:.2f} ({:.2f})'.format(label, ma, ref_ma, rate, x, round_tick(x)))

    return

def print_rates(df, label):

    pz = df['close'].iloc[-1]

    print('---')
    for rate in np.arange(1.01, 1.1, 0.01):
        x = pz * rate
        print('{} pz {:.2f} x {:.2f} = {:.2f} ({:.2f})'.format(label, pz, rate, x, round_tick(x)))

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
    parser.add_argument('-r', '--rates', action="store_true")
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

        if args.rates:
            print_rates(df, label)

        if args.plot:
            plot(df)

    return

if __name__ == '__main__':
    main()
