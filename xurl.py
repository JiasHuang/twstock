#!/usr/bin/python3

import os
import sys
import re
import hashlib
import time

from urllib.parse import urlparse, quote, unquote, unquote_plus, urljoin

class defvals:
    workdir             = '/var/tmp/'
    ua                  = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36'
    expiration          = 14400

class delayObj:
    def __init__(self, flt, delay):
        self.flt = flt
        self.delay = delay
        self.time = None
    objs = []

class xurlObj:
    def __init__(self, url, cookies=None, ref=None):
        self.url = url
        self.cookies = cookies
        self.ref = ref

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

def saveM3U8(local, result):
    fd = open(local, 'w')
    fd.write('#EXTM3U\n')
    for r in result:
        fd.write('#EXTINF:-1,0\n')
        fd.write(r+'\n')
    fd.write('#EXT-X-ENDLIST\n')
    fd.close()
    return

def checkExpire(local, expiration=None):
    if not os.path.exists(local):
        return True
    if os.path.getsize(local) <= 0:
        return True
    expiration = expiration or defvals.expiration
    t0 = int(os.path.getmtime(local))
    t1 = int(time.time())
    if (t1 - t0) > expiration:
        return True
    return False

def genLocal(url, prefix='vod_load_', suffix='', opts=None):
    if opts and isinstance(opts, list):
        for opt in opts:
            if opt.startswith('--data-raw'):
                url = url + opt
    local = os.path.join(defvals.workdir, prefix + hashlib.md5(url.encode('utf8')).hexdigest() + suffix)
    return local

def getContentType(url):
    local = genLocal(url, suffix='.hdr')
    txt = load(url, local, opts=['--head'], cmd='curl')
    m = re.search(r'Content-Type: (.*?)(;|\s)', txt, re.IGNORECASE)
    if m:
        return m.group(1)
    return None

# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------

def curl(url, local, opts, ref, encoding):
    opts = opts or []
    if ref:
        opts.append('-e \'%s\'' %(ref))
    opts.append('-H \'User-Agent: %s\'' %(defvals.ua))
    opts.append('-H \'Accept-Encoding: gzip, deflate\'')
    opts.append('--compressed')
    cmd = 'curl -kLsf -o %s %s \'%s\'' %(local, ' '.join(opts), url)
    try:
        os.system(cmd)
    except:
        print('Exception:\n' + cmd)
    return readLocal(local, encoding)

def load(url, local=None, opts=None, ref=None, cache=True, cacheOnly=False, expiration=None, cmd='curl', verbose=True, encoding=None):
    local = local or genLocal(url, opts=opts)
    expiration = expiration or defvals.expiration
    if cacheOnly or (cache and not checkExpire(local, expiration)):
        if verbose:
            print('[xurl] %s -> %s (cache)' %(url, local))
        return readLocal(local)
    checkDelay(url)
    t0 = time.time()
    ret = eval('%s(url, local, opts=opts, ref=ref, encoding=encoding)' %(cmd))
    t1 = time.time()
    if verbose:
        print('[xurl] %s -> %s (%.2f)' %(url, local, t1 - t0))
    return ret

def addDelayObj(flt, delay):
    delayObj.objs.append(delayObj(flt, delay))
    return

def checkDelay(url):
    now = time.time()
    for obj in delayObj.objs:
        if re.search(obj.flt, url):
            if not obj.time:
                obj.time = now
            else:
                delta = now - obj.time
                if delta < obj.delay:
                    time.sleep(obj.delay - delta)
                    obj.time = time.time()
            return

