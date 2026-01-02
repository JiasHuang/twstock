#!/bin/bash

mkdir -p TPE

curl -o TPE/0050.csv "https://docs.google.com/spreadsheets/d/1iRKkanw3P2inOZXrqfZQ_jRjSZkVQhoDdBQPkFMX9JY/gviz/tq?tqx=out:csv&sheet=close_0050"
curl -o TPE/00631L.csv "https://docs.google.com/spreadsheets/d/1iRKkanw3P2inOZXrqfZQ_jRjSZkVQhoDdBQPkFMX9JY/gviz/tq?tqx=out:csv&sheet=close_00631L"
curl -o TPE/00646.csv "https://docs.google.com/spreadsheets/d/1iRKkanw3P2inOZXrqfZQ_jRjSZkVQhoDdBQPkFMX9JY/gviz/tq?tqx=out:csv&sheet=close_00646"
curl -o TPE/00647L.csv "https://docs.google.com/spreadsheets/d/1iRKkanw3P2inOZXrqfZQ_jRjSZkVQhoDdBQPkFMX9JY/gviz/tq?tqx=out:csv&sheet=close_00647L"

