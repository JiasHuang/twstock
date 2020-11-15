#!/usr/bin/env python

import re
import sys
import os

import xurl

from mod_python import util

def index(req):
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'jsons/account.json')
    req.content_type = 'application/json'
    req.write(xurl.readLocal(path))
    return

