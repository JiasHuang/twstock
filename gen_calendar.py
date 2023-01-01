#!/usr/bin/python3

import os
import re
import json
import argparse
from datetime import date
import calendar

class WeekInfo:
    def __init__(self, week):
        self.W = week
        self.days = ['' for x in range(7)]
        self.note = ''
    def reprJSON(self):
        return self.__dict__

class MonthInfo:
    def __init__(self, month):
        self.M = month
        self.note = ''
        self.weeks = []
    def reprJSON(self):
        return self.__dict__

class QuarterInfo:
    def __init__(self, quarter):
        self.Q = quarter
        self.note = ''
        self.months = []
    def reprJSON(self):
        return self.__dict__

class YearInfo:
    def __init__(self, year):
        self.Y = year
        self.note = ''
        self.quarters = []
    def reprJSON(self):
        return self.__dict__

def gen_calendar(Y):
    y = YearInfo(Y)
    for Q in range(1, 5):
        q = QuarterInfo(Q)
        for M in range(Q*3-2, Q*3+1):
            days = calendar.monthrange(Y, M)[1]
            m = MonthInfo(M)
            for D in range(1, days + 1):
                year, week, weekday = date(Y, M, D).isocalendar()
                if len(m.weeks) == 0 or m.weeks[-1].W != week:
                    m.weeks.append(WeekInfo(week))
                m.weeks[-1].days[weekday-1] = D
            q.months.append(m)
        y.quarters.append(q)
    return y

class ComplexEncoder(json.JSONEncoder):
    def default(self, obj):
        if hasattr(obj,'reprJSON'):
            return obj.reprJSON()
        else:
            return json.JSONEncoder.default(self, obj)

def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument('-Y', '--year', type=int, default=date.today().year)
    args = parser.parse_args(argv)
    obj = gen_calendar(args.year)
    print(json.dumps(obj.reprJSON(), cls=ComplexEncoder, indent=2))
    return

if __name__ == '__main__':
    main()
