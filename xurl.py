#!/usr/bin/python3

import os
import sys
import re
import hashlib
import time
import json

class delayObj:
    def __init__(self, flt, delay):
        self.flt = flt
        self.delay = delay
        self.time = None

class defvals:
    workdir = '/var/tmp/'
    expiration = 14400
    verbose = False
    delay = [delayObj(r'twse.com.tw', 0.5), delayObj(r'finance.yahoo.com', 1)]

def readLocal(local, encoding=None):
    if os.path.exists(local):
        fd = open(local, 'r', encoding=encoding, errors='replace')
        txt = fd.read()
        fd.close()
        return txt
    return ''

def saveLocal(local, text):
    fd = open(local, 'w')
    fd.write(text)
    fd.close()
    return

def checkCache(local, cache, cacheOnly, expiration):
    if not os.path.exists(local):
        return False
    if cacheOnly:
        return True
    if cache:
        exp = expiration or defvals.expiration
        t0 = int(os.path.getmtime(local))
        t1 = int(time.time())
        return (t1 - t0) < exp
    return False

def genLocal(url, prefix='twstock_load_', suffix=''):
    local = os.path.join(defvals.workdir, prefix + hashlib.md5(url.encode('utf8')).hexdigest() + suffix)
    return local

# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------

def curl(url, local, encoding):
    cmd = 'curl_chrome116 -s -o %s \'%s\'' %(local, url)
    try:
        os.system(cmd)
    except:
        print('Exception:\n' + cmd)
    return readLocal(local, encoding)

def load(url, local=None, cache=True, cacheOnly=False, expiration=None, verbose=False, encoding=None):
    local = local or genLocal(url)
    if checkCache(local, cache, cacheOnly, expiration):
        if defvals.verbose or verbose:
            print('[xurl] %s -> %s (cache)' %(url, local))
        return readLocal(local, encoding)
    checkDelay(url)
    t0 = time.time()
    ret = curl(url, local, encoding)
    t1 = time.time()
    if defvals.verbose or verbose:
        print('[xurl] %s -> %s (%.2f)' %(url, local, t1 - t0))
    return ret

def load_json(url, local=None, cache=True, cacheOnly=False, expiration=None, verbose=False, encoding=None):
    local = local or genLocal(url)
    txt = load(url, local, cache, cacheOnly, expiration, verbose, encoding)
    try:
        obj = json.loads(txt)
        return obj
    except ValueError as e:
        if cacheOnly and re.search('頁面無法執行', txt):
            return load_json(url, local, cache, False, expiration, verbose, encoding)

    if defvals.verbose or verbose:
        print('load_json failed: {} (cache={}, cacheOnly={})'.format(url, cache, cacheOnly))

    return None

def addDelayObj(flt, delay):
    defvals.delay.append(delayObj(flt, delay))
    return

def set_verbose(en):
    defvals.verbose = en
    return

def checkDelay(url):
    now = time.time()
    for obj in defvals.delay:
        if re.search(obj.flt, url):
            if not obj.time:
                obj.time = now
            else:
                delta = now - obj.time
                if delta < obj.delay:
                    time.sleep(obj.delay - delta)
                    obj.time = time.time()
            return

