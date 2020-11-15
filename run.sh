#!/bin/sh

DEFAULTVALUE=jsons/stocks.json

PYTHONIOENCODING=utf-8 watch -c -n 5 ./twstock.py -i ${1:-$DEFAULTVALUE}
