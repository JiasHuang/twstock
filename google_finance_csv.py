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
import tse
import otc

cached = {}

class StockInfo:
    def __init__(self, row, ma_list):
        self.date = row['date'].date()
        attrs = ['open', 'high', 'low', 'close', 'volume', 'desc']
        for ma in ma_list:
            attrs.append('ma'+str(ma))
        for attr in attrs:
            setattr(self, attr, getattr(row, attr))

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
    return None

def update_csv(path, exchange, code):
    if exchange in ['TSE', 'OTC']:
        data = tse.get_data(code) if exchange == 'TSE' else otc.get_data(code)
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
    return df[attr].tail(days).to_list()

def get_attr(exchange, code, attr, date):
    vals = get_attrs(exchange, code, attr, date, 1)
    return vals[0] if vals else None

def get_ma(exchange, code, date, days):
    vals = get_attrs(exchange, code, "close", date, days)
    return np.mean(vals)

def get_infos(exchange, code, start, end, ma_list):
    df = get_dataframe(exchange, code, start, end, ma_list)
    infos = [StockInfo(row, ma_list) for idx, row in df.iterrows()]
    return infos

def get_dataframe(exchange, code, start, end, ma_list, compare=None):
    df = get_data(exchange, code, start, end)

    for ma in ma_list:
        df['ma'+str(ma)] = abstract.SMA(df, ma)

    desc = [[] for _ in range(len(df))]
    names = ['HAMMER', 'MORNINGSTAR', 'ENGULFING', 'DOJI', 'SHOOTINGSTAR', 'EVENINGSTAR']
    for name in names:
        fun = getattr(abstract, 'CDL' + name)
        vals = fun(df)
        for idx, val in enumerate(vals):
            if val != 0:
                desc[idx].append(name + '(' + str(val) + ')')
    df['desc'] = desc

    df['rsi'] = abstract.RSI(df)
    df['obv'] = abstract.OBV(df).divide(1000)
    df['obv_ma10'] = talib.SMA(df['obv'], 10)

    kd = abstract.STOCH(df)
    df['k'] = kd['slowk']
    df['d'] = kd['slowd']

    macd = abstract.MACD(df)
    df['macd'] = macd['macd']
    df['macd_signal'] = macd['macdsignal']
    df['macd_hist'] = macd['macdhist']

    df.dropna(inplace=True)

    if compare:
        ex2 = get_exchange(compare)
        df2 = get_data(ex2, compare, df['date'].iloc[0], end)
        df['compare'] = df2['close']

    return df

def analyze(df):

    pz = df['close'].iloc[-1]

    data = {}
    data['*** pz ***'] = pz
    for ma in [5, 10, 20, 60, 120, 240]:
        vals = df['close'].tail(ma).to_list()
        data['ma'+str(ma)] = np.mean(vals)

    for days in [60, 120, 240]:
        vals = df['close'].tail(days).to_list()
        data['lo' + str(days)] = min(vals)
        data['hi' + str(days)] = max(vals)

    print('---')
    for k, v in sorted(data.items(), key=lambda item: item[1], reverse=True):
        print('{} {:.2f} ({:+.2%})'.format(k, v, pz/v-1))

    return

def plot(df):

    has_compare = True if 'compare' in df else False
    nrows = 4 if has_compare else 3
    height_ratios = [4, 1, 1, 1] if has_compare else [4, 1, 1]
    fig, axes = plt.subplots(nrows=nrows, ncols=1, figsize=(20, 10), gridspec_kw={'height_ratios': height_ratios}, sharex=True)
    axes = axes.flatten()

    x = df['date'].to_numpy()

    axes[0].plot(x, df['close'].to_numpy())
    axes[0].set_ylabel('close')

    if has_compare:
        pz2 = df['compare'].to_numpy()
        rate = df['close'].to_numpy() / pz2
        axes[0].plot(x, pz2, color='orange')
        axes[3].plot(x, rate)
        axes[3].set_ylabel('rate')

    axes[1].plot(x, df['macd_hist'].to_numpy(), zorder=10)
    axes[1].axhline(y=0, color='black', linestyle='--', linewidth=1.5, zorder=0)
    axes[1].set_ylabel('macd_hist')

    axes[2].plot(x, df['obv'].to_numpy(), zorder=10)
    axes[2].plot(x, df['obv_ma10'].to_numpy(), color='orange', zorder=0)
    axes[2].set_ylabel('obv')

    # Create the MultiCursor object
    # Pass the figure's canvas and a list of axes to the MultiCursor
    # Set vertOn=True to enable the vertical line, horizOn=False to disable the horizontal line
    # useblit=True provides faster drawing if supported by the backend
    cursor = MultiCursor(fig.canvas, axes, color='black', linewidth=1, vertOn=True, horizOn=False, useblit=True)

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
    parser.add_argument('-c', '--code', default='2330')
    parser.add_argument('-a', '--ma', type=int, default=60)
    parser.add_argument('-d', '--date')
    parser.add_argument('--compare')
    args, unparsed = parser.parse_known_args()

    if not args.exchange:
        args.exchange = get_exchange(args.code)

    if not args.date:
        args.date = datetime.date.today().strftime('%Y%m%d')

    date = datetime.datetime.strptime(args.date, '%Y%m%d').date()
    start = date - datetime.timedelta(days=365)
    df = get_dataframe(args.exchange, args.code, start, date, [args.ma], args.compare)
    print(df.round(2))
    analyze(df)
    plot(df)

    return

if __name__ == '__main__':
    main()
