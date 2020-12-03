#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import re
import sys
import json
import time
import datetime

import xurl

from optparse import OptionParser

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

class exchange_rate_info:
    def __init__(self, currency, buy_cash, buy_spot, sell_cash, sell_spot):
        self.flts = []
        self.flts_ret = []
        self.currency = currency
        self.buy_cash = buy_cash
        self.buy_spot = buy_spot
        self.sell_cash = sell_cash
        self.sell_spot = sell_spot

class stock_info:
    def __init__(self, code, flts = None, tags = None):
        self.code = code
        self.flts = flts or []
        self.flts_ret = [0] * len(self.flts)
        self.tags = tags or []
        self.msg = None
        self.z = 0
        self.y = 0
        self.v = 0
        self.v_ratio = 0
        self.h = 0
        self.l = 0
        self.avg = {}

class stock_report:
    def __init__(self, code):
        self.code = code
        self.z = 0
        self.n = None
        self.nf = None
        self.ex = None
        self.hi = []
        self.lo = []
        self.wap = []
        self.eps = []
        self.dividend = []
        self.revenue = []
        self.pz_vol_pairs = []
        self.news = []
    def show(self):
        print('-- wap --')
        for x in self.wap:
            print(x)
        print('-- eps --')
        for x in self.eps:
            print(x)
        print('-- dividend --')
        for x in self.dividend:
            print(x)
        print('-- revenue --')
        for x in self.revenue:
            print(x)
        print('-- news --')
        for x in self.news:
            print(x)

def get_stat_from_fubon(code, cacheOnly):
    obj = {}
    url = 'https://fubon-ebrokerdj.fbs.com.tw/Z/ZC/ZCW/ZCWG/ZCWG_%s_30.djhtm' %(code)
    txt = xurl.load(url, cacheOnly=cacheOnly, expiration=432000)
    m = re.search(r'GetBcdData\(\'([^ ]*) ([^\']*)\'', txt)
    if m:
        pzs = map(float, m.group(1).split(','))
        vols = map(int, m.group(2).split(','))
        total = 0
        pairs = []
        for i in range(len(pzs)):
            total = total + (pzs[i] * vols[i])
            pairs.append((pzs[i], vols[i]))
        obj['30d_pz'] = total / sum(vols)
        obj['30d_vol'] = sum(vols) / 30
        obj['30d_pz_vol_pairs']= pairs
    return obj

def get_stat_from_goodinfo(code, cacheOnly):
    obj = {}
    url = 'https://goodinfo.tw/StockInfo/StockDetail.asp?STOCK_ID=' + code
    txt = xurl.load(url, cacheOnly=cacheOnly)
    # 統計區間,累計漲跌價,累計漲跌幅,區間振幅,成交量週轉率,均線落點,均線乖離率
    ranges = {'1m':'月', '3m':'季', '6m':'半年', '1y':'年', '3y':'三年'}
    for k in ranges:
        vals = []
        m = re.search(r'<td>'+re.escape(ranges[k])+'</td>.*?</tr>', txt, re.DOTALL | re.MULTILINE)
        if m:
            for num in re.finditer(r'<nobr>(.*?)[→↘↗%]*</nobr></td>', m.group()):
                vals.append(float(num.group(1)))
            if len(vals) == 6:
                obj[k+'_pz'] = vals[4]
    print('%.2f %s %s' %(time.time(), code, str(obj)))
    return obj

def get_ex_ch_by_code(code):
    local = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'otc_code_list.txt')
    with open(local) as fd:
        for line in fd.readlines():
            if line.rstrip() == code:
                return 'otc_%s.tw' %(code)
    return 'tse_%s.tw' %(code)

def get_stock_infos(data):
    info = []
    for s in data['stocks']:
        info.append(stock_info(s['code'], s.get('flts'), s.get('tags')))
    ex_ch = '|'.join([get_ex_ch_by_code(i.code) for i in info])
    url = 'https://mis.twse.com.tw/stock/api/getStockInfo.jsp?ex_ch=%s&json=1&delay=0' %(ex_ch)
    txt = xurl.load(url, cache=False)
    data = json.loads(txt)
    for i in range(len(info)):
        info[i].msg = data['msgArray'][i]
        parse_info(info[i])
    return info

def update_stock_stats(infos, cacheOnly):
    for info in infos:
        info.avg.update(get_stat_from_fubon(info.code, cacheOnly))
        #info.avg.update(get_stat_from_goodinfo(info.code, cacheOnly))
    return

def parse_info(info):

    msg = info.msg

    # FIXME
    if msg['z'] == '-':
        try:
            msg['z'] = msg['b'].split('_')[0]
        except:
            pass

    try:
        info.y = y = float(msg['y'])
        info.v = v = float(msg['v'])
        info.z = z = float(msg['z'])
        info.h = h = float(msg['h'])
        info.l = l = float(msg['l'])
    except:
        pass

    if info.z == 0:
        info.z = info.y

    for i, f in enumerate(info.flts):
        try:
            m = re.search(r'(\w+)', f)
            vname = m.group(1)
            val = msg[vname]
            cmd = f.replace(vname, val)
            info.flts_ret[i] = eval(cmd)
        except:
            pass

    return

def chg_ratio_txt(val, ref):
    chg = val - ref
    ratio = chg / ref * 100
    return (chg, ratio, '%.2f (%+.2f, %+.2f%%)' %(val, chg, ratio))

def show_stock_info(info):

    print('%s %s' %(info.msg['c'], info.msg['n']))

    cflts = []
    for i, f in enumerate(info.flts):
        if info.flts_ret[i]:
            cflts.append(bcolors.BLACK_ON_YELLOW + f + bcolors.ENDC)
        else:
            cflts.append(f)

    chg, ratio, txt = chg_ratio_txt(info.z, info.y)
    if chg > 0:
        txt = bcolors.RED + txt + bcolors.ENDC
    elif chg < 0:
        txt = bcolors.GREEN + txt + bcolors.ENDC

    print('\t\t%s | %s' %(txt, ', '.join(cflts)))

    if '30d_vol' in info.avg:
        ratio = info.v / info.avg['30d_vol'] * 100
        txt = '#%.0f (%.2f%%)' %(info.v, ratio)
        if ratio > 100:
            txt = bcolors.YELLOW + txt + bcolors.ENDC
        print('\t\t%s' %(txt))

    if info.h > 0:
        chg, ratio, txt = chg_ratio_txt(info.h, info.y)
        print('\t\tHi %s' %(txt))

    if info.l > 0:
        chg, ratio, txt = chg_ratio_txt(info.l, info.y)
        print('\t\tLo %s' %(txt))

    for x in ['30d_pz', '1m_pz', '3m_pz', '6m_pz', '1y_pz']:
        if x in info.avg:
            chg, ratio, txt = chg_ratio_txt(info.z, info.avg[x])
            print('\t\t%s: %s' %(x, txt))

    return

def get_json_from_file(path):
    txt = xurl.readLocal(path)
    return json.loads(txt)

def get_stock_json_by_codes(codes):
    json_strs = ['{"code":"%s"}' %(c) for c in codes.split(',')]
    return json.loads('{"stocks":[%s]}' %(','.join(json_strs)))

def get_exchange_rate_infos(data):

    if 'ExchangeRates' not in data:
        return []

    url = 'https://rate.bot.com.tw/xrt/flcsv/0/day'
    txt = xurl.load(url, cache=False)
    infos = []

    for exr in data['ExchangeRates']:
        c = exr['currency'].encode('utf-8')
        m = re.search(re.escape(c) + r',本行買入,([^,]*),([^,]*),.*?本行賣出,([^,]*),([^,]*),', txt)
        if m:
            info = exchange_rate_info(c, m.group(1), m.group(2), m.group(3), m.group(4))
            info.flts = exr['flts']
            info.flts_ret = [0] * len(info.flts)
            infos.append(info)

    # check the retured value of flts
    for info in infos:
        for i, f in enumerate(info.flts):
            try:
                m = re.search(r'(\w+)', f)
                vname = m.group(1)
                val = getattr(info, vname)
                cmd = f.replace(vname, val)
                info.flts_ret[i] = eval(cmd)
            except:
                pass

    return infos

def show_exr_info(info):
    print('%s: %s' %(info.currency, info.sell_spot))
    #print(str(info.__dict__))
    return

def get_stock_info_by_code(code):
    data = get_stock_json_by_codes(code)
    infos = get_stock_infos(data)
    update_stock_stats(infos, False)
    return infos[0]

def update_stock_report_wap(obj):
    now = datetime.datetime.now()
    years = [now.year - 2, now.year - 1, now.year]
    for year in years:
        url = 'https://www.twse.com.tw/exchangeReport/FMSRFK?response=json&stockNo=%s&date=%4d0101' %(obj.code, year)
        txt = xurl.load(url)
        data = json.loads(txt)
        if 'data' not in data:
            continue
        # 年度,月份,最高價,最低價,加權(A/B)平均價,成交筆數,成交金額(A),成交股數(B),週轉率(%),
        for d in data['data']:
            Y, M = d[0], d[1]
            h, l, a, = d[2], d[3], d[4]
            A = d[6].replace(',','')
            B = d[7].replace(',','')
            obj.wap.append((Y, M, h, l, a, A, B))
    return

def update_stock_report_wap_otc(obj):
    now = datetime.datetime.now()
    years = [now.year - 2, now.year - 1, now.year]
    for year in years:
        url = 'https://www.tpex.org.tw/web/stock/statistics/monthly/download_st44.php?yy=%s' %(year)
        txt = xurl.load(url, opts=['--data-raw \'yy=%s&stk_no=%s\'' %(year, obj.code)])
        # 年度,月份,收市最高價,收市最低價,收市平均價,成交筆數,成交金額仟元(A),成交股數仟股(B),週轉率(%),
        for m in re.finditer(r'"(\d+)","(\d+)","(.*?)","(.*?)","(.*?)",".*?","(.*?)","(.*?)",', txt):
            Y, M = m.group(1), m.group(2)
            h, l, = m.group(3), m.group(4)
            A = m.group(6).replace(',','')
            B = m.group(7).replace(',','')
            a = '%.2f' %(float(A) / float(B))
            obj.wap.append((Y, M, h, l, a, A + '000', B + '000'))
    return

def update_stock_report_eps(obj):
    now = datetime.datetime.now()
    from_year = int(now.year) - 1911 - 3
    url = 'https://fubon-ebrokerdj.fbs.com.tw/z/zc/zcd/zcd_%s.djhtm' %(obj.code)
    txt = xurl.load(url)
    years = 0
    # 季別,加權平均股數,營業收入,稅前淨利,稅後淨利,每股營收(元),稅前每股盈餘(元),稅後每股盈餘(元)
    for m in re.finditer(r'<tr><td class="t3n0">(\d+)\.(\d)Q</td>(.*?)</tr>', txt):
        Y, Q = m.group(1), m.group(2)
        if int(Y) <= from_year:
            break
        m2 = re.findall(r'>([^<]+)<', m.group(3))
        if len(m2) == 7:
            obj.eps.insert(0, (Y, Q, m2[5], m2[6]))
    return

def update_stock_report_dividend(obj):
    url = 'https://fubon-ebrokerdj.fbs.com.tw/z/zc/zcc/zcc_%s.djhtm' %(obj.code)
    txt = xurl.load(url)
    for m in re.finditer(r'<td class="t3n0">(.*?)</tr>', txt, re.MULTILINE | re.DOTALL):
        m2 = re.findall(r'>([^<]+)</td>', m.group(0))
        if len(m2) == 9:
            obj.dividend.append((m2[0], m2[1], m2[2], m2[4], m2[5]))
        if len(obj.dividend) >= 5:
            break
    return

def update_stock_report_revenue(obj):
    now = datetime.datetime.now()
    from_year = int(now.year) - 1911 - 3
    url = 'https://fubon-ebrokerdj.fbs.com.tw/z/zc/zch/zch_%s.djhtm' %(obj.code)
    txt = xurl.load(url)
    for m in re.finditer(r'<td class="t3n0">(\d+)/(\d+)</td>(.*?)</tr>', txt, re.MULTILINE | re.DOTALL):
        Y, M = m.group(1), m.group(2)
        if int(Y) <= from_year:
            break
        m2 = re.findall(r'>([^<]+)</td>', m.group(3))
        if len(m2) > 0:
            obj.revenue.insert(0, (Y, M, m2[0].replace(',','')))
    return

def update_stock_report_news(obj):
    for i in range(1, 3):
        url = 'https://fubon-ebrokerdj.fbs.com.tw/Z/ZC/ZCV/ZCV_%s_E_%d.djhtm' %(obj.code, i)
        txt = xurl.load(url)
        for m in re.finditer(r'<tr><td class="t3t1">([^<]*)</td>\s*<td class="t3t1"><a href="([^"]*)">([^<]*)</a>', txt):
            date = m.group(1)
            link = 'https://fubon-ebrokerdj.fbs.com.tw' + m.group(2)
            title = m.group(3).decode('big5', 'replace').encode('utf8')
            if re.search(r'(每股稅後|每股盈餘)', title):
                obj.news.append((date, title, link))
    return

def update_stock_report_eps_from_news(obj):
    if not len(obj.eps):
        return
    eps = obj.eps[len(obj.eps) - 1]
    if eps[1] == '4':
        Y = str(int(eps[0]) + 1)
        Q = '1'
    else:
        Y = eps[0]
        Q = str(int(eps[1]) + 1)
    for n in obj.news:
        # 自結第一季合併獲利229.4億元，每股稅後2.24元
        # 富邦金前三季合併獲利682.06億元，每股稅後6.38元
        # 富邦金自結108年合併獲利587.3億元，每股稅後5.48元
        m = re.search(r'(第1季|第一季|上半年|前3季|前三季|\d+年)合併.*?每股稅後(.*?)元', n[1])
        if m:
            if (Q == '1' and m.group(1) in ['第1季', '第一季']) \
                or (Q == '2' and m.group(1) in ['上半年']) \
                or (Q == '3' and m.group(1) in ['前3季', '前三季']) \
                or (Q == '4' and re.search(r'\d+年', m.group(1))):
                x = float(m.group(2))
                for i in range(1, int(Q)):
                    x = x - float(obj.eps[len(obj.eps) - i][3])
                obj.eps.append((Y, Q, '-', str(x)))
            break
    return

def get_stock_report(code):
    obj = stock_report(code)
    info = get_stock_info_by_code(code)
    obj.z = info.z
    obj.n = info.msg['n']
    obj.nf = info.msg['nf']
    obj.ex = info.msg['ex']
    obj.pz_vol_pairs = info.avg['30d_pz_vol_pairs']
    if obj.ex == 'otc':
        update_stock_report_wap_otc(obj)
    else:
        update_stock_report_wap(obj)
    update_stock_report_eps(obj)
    update_stock_report_dividend(obj)
    update_stock_report_revenue(obj)
    update_stock_report_news(obj)
    update_stock_report_eps_from_news(obj)
    return obj

def init():
    xurl.addDelayObj(r'fbs.com.tw', 0.1)
    xurl.addDelayObj(r'goodinfo.tw', 2)
    xurl.addDelayObj(r'twse.com.tw', 0.5)
    xurl.addDelayObj(r'cnyes.com', 0.5)
    return

def main():
    parser = OptionParser()
    parser.add_option("-i", "--input", dest="input")
    parser.add_option("-c", "--codes", dest="codes")
    parser.add_option("-s", "--stat", dest="stat", action="store_true", default=False)
    parser.add_option("-r", "--report", dest="report", action="store_true", default=False)
    (options, args) = parser.parse_args()
    stock_infos = []
    init()
    if options.report:
        if options.codes:
            for code in options.codes.split(','):
                rpt = get_stock_report(code)
                rpt.show()
        return
    if options.codes:
        data = get_stock_json_by_codes(options.codes)
        stock_infos.extend(get_stock_infos(data))
    if options.input:
        data = get_json_from_file(options.input)
        stock_infos.extend(get_stock_infos(data))
    update_stock_stats(stock_infos, not options.stat)
    for info in stock_infos:
        show_stock_info(info)
    exr_infos = get_exchange_rate_infos(data)
    for info in exr_infos:
        show_exr_info(info)
    return

if __name__ == '__main__':
    main()
