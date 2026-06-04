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
import yfin
import gfin
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
    ex, name = twse.get_ex_name(code)
    if not ex:
        return gfin.load_sheet(code)
    data = yfin.get_data(code, start, end) if ex == 'TSE' else twse.get_data(code, start, end)
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

def get_stat(code, days=360):
    d = gfin.query(code)
    if d:
        return {'ma20':d['ma20'], 'ma60':d['ma60'], 'mv':d['mv'], 'days_hi':d['days_hi'], 'days_lo':d['days_lo']}
    df = get_data_by_days(code, days)
    if len(df.index):
        ma20 = round(df['close'].tail(20).mean(), 2)
        ma60 = round(df['close'].tail(60).mean(), 2)
        mv30 = int(df['volume'].tail(30).mean())
        days_hi = df['close'].max()
        days_lo = df['close'].min()
        return {'ma20':ma20, 'ma60':ma60, 'mv':mv30, 'days_hi':days_hi, 'days_lo':days_lo}
    return None

def add_sma(df, days, col='close'):
    vals = df[col].to_numpy()
    sma_vals = [vals[idx-days:idx].mean() if idx >= days else None for idx in range(len(vals))]
    return sma_vals

def add_pct(df, col_a, col_b):
    vals = [(a / b * 100 - 100) if b else 0 for a, b in zip(df[col_a], df[col_b])]
    return vals

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

    ma20 = df['ma20'].to_numpy()
    ax.plot(x, ma20, color='deeppink', linestyle='dashed', linewidth=1, zorder=1, label='ma20')

    ma60 = df['ma60'].to_numpy()
    ax.plot(x, ma60, color='green', linestyle='dashed', linewidth=1, zorder=0, label='ma60')

    for pct in [-20, -15, -10, -5, 5, 10, 15, 20]:
        new_vals = [v * (100 + pct) / 100 if v else None for v in ma60]
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

    ax.text(hi_x, hi, '{} ${}'.format(hi_x.date(), hi))
    ax.text(lo_x, lo, '{} ${}'.format(lo_x.date(), lo))

    plt.ylim(lo, hi)
    plt.title(title, pad=20)
    plt.legend()

    if output:
        plt.savefig(output, format='png')
    else:
        plt.show()

    return

def chart(code, output, days=540):
    end = datetime.datetime.now()
    start = end - datetime.timedelta(days=days)

    df = get_data(code, start, end)
    df['ma20'] = add_sma(df, 20)
    df['ma60'] = add_sma(df, 60)

    name = twse.get_name(code)
    date = df['date'].iloc[-1].strftime('%Y-%m-%d')
    pz = df['close'].iloc[-1]
    y = df['close'].iloc[-2]
    chg_pct = (pz / y - 1) * 100
    ma20 = df['ma20'].iloc[-1] or 0
    ma20_pct = (pz / ma20 - 1) * 100 if ma20 else 0
    ma60 = df['ma60'].iloc[-1] or 0
    ma60_pct = (pz / ma60 - 1) * 100 if ma60 else 0
    mv = round(df['volume'].tail(30).mean())
    title = '[{}] {} ${} ({:+.2f}%)\n[{}] MA20 {:.2f} ({:+.2f}%) MA60 {:.2f} ({:+.2f}%)均量 {:,}'.format(code, name, pz, chg_pct, date, ma20, ma20_pct, ma60, ma60_pct, mv)

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
