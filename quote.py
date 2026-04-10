#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os
import argparse
import datetime
import csv
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

import twse
import xurl

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

def load_csv(code, start, end):
    path = 'csv/{}.csv'.format(code)
    ex, name = twse.get_name(code)
    if not ex:
        return path if os.path.exists(path) else None
    data = twse.get_data(code, start, end)
    df = pd.DataFrame(data)
    os.makedirs('csv', exist_ok=True)
    df.to_csv(path, index=False, quotechar='"', quoting=csv.QUOTE_ALL)
    return path

def get_data(code, start, end):
    path = load_csv(code, start, end)
    assert path, 'Not Found'
    new_names = ['date', 'open', 'high', 'low', 'close', 'volume']
    df = pd.read_csv(path, names=new_names, header=0, parse_dates=['date'])

    start_64 = np.datetime64(start)
    end_64 = np.datetime64(end)

    return df[(df['date'] >= start_64) & (df['date'] <= end_64)].copy()

def get_data_by_days(code, days, end=None):
    if not end:
        end = datetime.datetime.now() - datetime.timedelta(days=1)
    adjust_days = max(int(days * 7 / 5), 15)
    start = end - datetime.timedelta(days=adjust_days)
    return get_data(code, start, end)

def get_stat(code, ma_days=60, mv_days=30, pz_days=240):
    days = max(ma_days, mv_days, pz_days)
    df = get_data_by_days(code, days)
    if len(df.index):
        ma = round(df['close'].tail(ma_days).mean(), 2)
        mv = int(df['volume'].tail(mv_days).mean())
        days_hi = df['close'].tail(pz_days).max()
        days_lo = df['close'].tail(pz_days).min()
        return {'ma':ma, 'mv':mv, 'days_hi':days_hi, 'days_lo':days_lo}
    return None

def add_sma(df, days, col='close'):
    vals = df[col].to_numpy()
    sma_vals = [vals[idx-days:idx].mean() if idx >= days else 0 for idx in range(len(vals))]
    return sma_vals

def add_pct(df, col_a, col_b):
    vals = [(a / b * 100 - 100) if b else 0 for a, b in zip(df[col_a], df[col_b])]
    return vals

def get_percent_color(pct):
    if pct == 0:
        return 'green'
    if pct in [-10, 10]:
        return 'orange'
    if pct in [-20, 20]:
        return 'red'
    return 'grey'

def plot(df, title, output=None):

    plt.rcParams['font.sans-serif'] = 'SimHei'
    plt.rcParams['axes.unicode_minus'] = False

    fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(16, 8))

    x = df['date'].to_numpy()
    y = df['close'].to_numpy()

    ax.plot(x, y, zorder=10)

    ax.set_ylabel('close')
    date_formatter = mdates.DateFormatter('%Y-%m-%d')
    ax.xaxis.set_major_formatter(date_formatter)

    # improve readability by rotating labels
    plt.xticks(rotation=45, ha='right')

    ma = df['ma'].to_numpy()
    for pct in np.arange(-20, 25, 5):
        new_vals = [v * (100 + pct) / 100 if v else None for v in ma]
        if pct == 0:
            ax.plot(x, new_vals, color='green', linestyle='dashed', linewidth=1, zorder=0)
        else:
            ax.plot(x, new_vals, color='grey', linestyle='dashed', linewidth=0.5, zorder=0)

    hi = max(y)
    lo = min(y)
    pz = y[-1]
    pz_pct = (pz - hi) / (hi - lo) * 100

    for pct in [-23.6, -38.2, -61.8]:
        v = hi + (hi - lo) * pct / 100
        plt.axhline(y=v, color='grey', linestyle='--', linewidth=1)
        ax.text(ax.get_xlim()[1], v, ' {:.2f} ({}%)'.format(v, pct), color='grey')

    plt.axhline(y=pz, color='red', linestyle='--', linewidth=1)
    ax.text(ax.get_xlim()[1], pz, ' {:.2f} ({:.2f}%)'.format(pz, pz_pct), color='red', backgroundcolor='white')

    hi_x = df[df['close'] == hi]['date'].iloc[-1]
    lo_x = df[df['close'] == lo]['date'].iloc[-1]

    ax.text(hi_x, hi, '{:.2f}'.format(hi))
    ax.text(lo_x, lo, '{:.2f}'.format(lo))

    plt.ylim(lo, hi)
    plt.title(title, pad=20)

    if output:
        plt.savefig(output, format='png')
    else:
        plt.show()

    return

def chart(code, output):
    end = datetime.datetime.now()
    start = end - datetime.timedelta(days=540)

    df = get_data(code, start, end)
    df['ma'] = add_sma(df, 60)
    df['ma%'] = add_pct(df, 'close', 'ma')

    ex, name = twse.get_name(code)
    date = df['date'].iloc[-1].strftime('%Y-%m-%d')
    pz = df['close'].iloc[-1]
    ma = df['ma'].iloc[-1]
    ma_pct = df['ma%'].iloc[-1]
    title = '{} {} ${}\n[{}] 均線 {:.2f} ({:+.2f}%)'.format(code, name, pz, date, ma, ma_pct)

    if not output:
        print(df.head(10).round(2))
        print(df.tail(10).round(2))

    plot(df, title, output)
    return

def main():

    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--code', default='0050')
    parser.add_argument('-v', '--verbose', action="store_true")
    parser.add_argument('-o', '--output')
    args, unparsed = parser.parse_known_args()

    xurl.set_verbose(args.verbose)

    code = unparsed[0] if len(unparsed) else args.code
    chart(code, args.output)

    return

if __name__ == '__main__':
    main()
