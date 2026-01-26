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
from matplotlib.widgets import MultiCursor
import twse

cached = {}

class StockInfo:
    def __init__(self, date, open, high, low, close, volume):
        self.date = date
        self.open = open
        self.high = high
        self.low = low
        self.close = close
        self.volume = volume
        self.desc = []

def get_exchange(code):
    exchanges = ['TPE', 'NASDAQ', 'NYSEARCA', 'NYSE']
    for exchange in exchanges:
        path = os.path.join(exchange, code + '.csv')
        if os.path.exists(path):
             return exchange
    return None

def get_data(exchange, code):
    path = os.path.join(exchange, code) + '.csv'
    if not os.path.exists(path):
        if exchange == 'TPE':
            data = twse.get_data(code)
            df = pd.DataFrame(data)
            df.to_csv(path, index=False, quotechar='"', quoting=csv.QUOTE_ALL)
    if path not in cached:
        new_names = ['date', 'open', 'high', 'low', 'close', 'volume']
        cached[path] = pd.read_csv(path, names=new_names, header=0, parse_dates=['date'])
    return cached[path]

def get_attrs(exchange, code, attr, date, days):
    vals = []
    data = get_data(exchange, code)
    for i, r in data[::-1].iterrows():
        if r['date'].date() <= date:
            vals.append(float(r[attr]))
            if len(vals) >= days:
                break
    vals.reverse()
    return vals

def get_attr(exchange, code, attr, date):
    vals = get_attrs(exchange, code, attr, date, 1)
    return vals[0] if vals else None

def get_ma(exchange, code, date, days):
    vals = get_attrs(exchange, code, "close", date, days)
    return sum(vals) / len(vals) if vals else 0

def get_infos(exchange, code, start, end, ma_list):
    infos = []
    data = get_data(exchange, code)
    for idx, row in data.iterrows():
        d = row['date'].date()
        if d < start:
            continue
        elif d > end:
            break
        else:
            infos.append(StockInfo(d, float(row['open']), float(row['high']), float(row['low']), float(row['close']), int(row['volume'])))

    df = pd.DataFrame([{'open':x.open, 'high':x.high, 'low':x.low, 'close':x.close, 'volume':x.volume} for x in infos])

    for ma in ma_list:
        result = abstract.SMA(df)
        for idx, val in enumerate(result):
            setattr(infos[idx], 'ma'+str(ma), val)

    names = ['HAMMER', 'MORNINGSTAR', 'ENGULFING', 'DOJI', 'SHOOTINGSTAR', 'EVENINGSTAR']
    for name in names:
        fun = getattr(abstract, 'CDL' + name)
        vals = fun(df)
        for idx, val in enumerate(vals):
            if val != 0:
                infos[idx].desc.append(name + '(' + str(val) + ')')

    return infos

def get_dataframe(exchange, code, start, end, ma_list):
    infos = []
    orig_data = get_data(exchange, code)
    data = []
    for idx, row in orig_data.iterrows():
        d = row['date'].date()
        if d < start:
            continue
        elif d > end:
            break
        else:
            data.append(row)

    df = pd.DataFrame(data)

    for ma in ma_list:
        df['ma'+str(ma)] = abstract.SMA(df, ma)

    names = ['HAMMER', 'MORNINGSTAR', 'ENGULFING', 'DOJI', 'SHOOTINGSTAR', 'EVENINGSTAR']
    for name in names:
        fun = getattr(abstract, 'CDL' + name)
        df[name] = fun(df)

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

    print(df.round(2))

    # Drop the initial NaN values from RSI calculation
    df.dropna(inplace=True)

    fig, axes = plt.subplots(nrows=3, ncols=1, figsize=(20, 10), gridspec_kw={'height_ratios': [4, 1, 1]})
    axes = axes.flatten()

    x = df['date'].to_numpy()

    axes[0].plot(x, df['close'].to_numpy())
    axes[0].set_ylabel('close')

    axes[1].plot(x, df['macd_hist'].to_numpy())
    axes[1].axhline(y=0, color='black', linestyle='--', linewidth=1.5)
    axes[1].set_ylabel('macd_hist')

    axes[2].plot(x, df['obv'].to_numpy())
    axes[2].plot(x, df['obv_ma10'].to_numpy(), color='orange')
    axes[2].set_ylabel('obv')

    # Create the MultiCursor object
    # Pass the figure's canvas and a list of axes to the MultiCursor
    # Set vertOn=True to enable the vertical line, horizOn=False to disable the horizontal line
    # useblit=True provides faster drawing if supported by the backend
    cursor = MultiCursor(fig.canvas, axes, color='black', linewidth=1, vertOn=True, horizOn=False, useblit=True)

    plt.tight_layout()
    plt.show()

    return infos

def main():

    parser = argparse.ArgumentParser()
    parser.add_argument('-e', '--exchange')
    parser.add_argument('-c', '--code', default='2330')
    parser.add_argument('-a', '--ma', type=int, default=60)
    parser.add_argument('-d', '--date')
    args, unparsed = parser.parse_known_args()

    if not args.exchange:
        args.exchange = get_exchange(args.code)

    if not args.date:
        args.date = datetime.date.today().strftime('%Y%m%d')

    date = datetime.datetime.strptime(args.date, '%Y%m%d').date()
    start = date - datetime.timedelta(days=365)
    df = get_dataframe(args.exchange, args.code, start, date, [args.ma])

    return

if __name__ == '__main__':
    main()
