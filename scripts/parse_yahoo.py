#!/usr/bin/env python3
"""从Yahoo Finance JSON中提取收盘价和涨跌幅"""
import sys, json

try:
    d = json.load(sys.stdin)
    q = d['chart']['result'][0]['indicators']['quote'][0]
    closes = [c for c in q['close'] if c is not None]
    if len(closes) >= 2:
        curr, prev = closes[-1], closes[-2]
        change = ((curr - prev) / prev) * 100
        print(f'{curr:.2f}|{change:.2f}')
    elif len(closes) == 1:
        print(f'{closes[0]:.2f}|0.00')
except:
    pass
