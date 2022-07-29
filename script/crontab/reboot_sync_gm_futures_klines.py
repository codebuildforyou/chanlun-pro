#:  -*- coding: utf-8 -*-
import datetime

from chanlun.exchange.exchange_db import ExchangeDB
import traceback
import time
import pandas as pd
from gm.api import *

"""
同步期货到数据库中

使用的是 掘金量化 API 获取
"""

# 可以直接提取数据，掘金终端需要打开，接口取数是通过网络请求的方式，效率一般，行情数据可通过subscribe订阅方式
# 设置token， 查看已有token ID,在用户-秘钥管理里获取
set_token('7eb4ebc68c8aaa69261b9e9d01541a6067cc7453')

db_ex = ExchangeDB('futures')

# 获取所有主连合约数据，用于数据回测
run_codes = [
    'CFFEX.IC', 'CFFEX.IF', 'CFFEX.IH', 'CFFEX.T', 'CFFEX.TF', 'CFFEX.TS',
    'CZCE.AP', 'CZCE.CF', 'CZCE.CJ', 'CZCE.CY', 'CZCE.FG', 'CZCE.JR', 'CZCE.LR', 'CZCE.MA', 'CZCE.OI', 'CZCE.PF',
    'CZCE.PM', 'CZCE.RI', 'CZCE.RM', 'CZCE.RS', 'CZCE.SA', 'CZCE.SF', 'CZCE.SM', 'CZCE.SR', 'CZCE.TA', 'CZCE.UR',
    'CZCE.WH', 'CZCE.ZC',
    'DCE.A', 'DCE.B', 'DCE.BB', 'DCE.C', 'DCE.CS', 'DCE.EB', 'DCE.EG', 'DCE.FB', 'DCE.I', 'DCE.J', 'DCE.JD',
    'DCE.JM', 'DCE.L', 'DCE.LH', 'DCE.M', 'DCE.P', 'DCE.PG', 'DCE.PP', 'DCE.RR', 'DCE.V', 'DCE.Y',
    'INE.BC', 'INE.LU', 'INE.NR', 'INE.SC',
    'SHFE.AG', 'SHFE.AL', 'SHFE.AU', 'SHFE.BU', 'SHFE.CU', 'SHFE.FU', 'SHFE.HC', 'SHFE.NI',
    'SHFE.PB', 'SHFE.RB', 'SHFE.RU', 'SHFE.SN', 'SHFE.SP', 'SHFE.SS', 'SHFE.WR', 'SHFE.ZN'
]

print(len(run_codes))

# 创建表
db_ex.create_tables(run_codes)

# 当前时间
now_datetime = datetime.datetime.now()

# 默认第一次同步的起始时间，后续则进行增量更新
sync_frequencys = {
    'd': {'start': '2005-01-01 00:00:00'},
    '60m': {'start': '2005-01-01 00:00:00'},
    '30m': {'start': '2005-01-01 00:00:00'},
    '15m': {'start': '2005-01-01 00:00:00'},
    '5m': {'start': '2016-01-01 00:00:00'},
    '1m': {'start': '2016-01-01 00:00:00'},
}
# 本地周期与掘金周期对应关系
fre_maps = {
    '1m': '60s', '5m': '300s', '15m': '900s', '30m': '1800s', '60m': '3200s', 'd': '1d'
}

for code in run_codes:
    for f, dt in sync_frequencys.items():
        try:
            time.sleep(3)
            last_dt = db_ex.query_last_datetime(code, f)
            if last_dt is None:
                last_dt = dt['start']
            klines = history(code, fre_maps[f], start_time=last_dt, end_time=now_datetime, df=True)
            klines.loc[:, 'code'] = klines['symbol']
            klines.loc[:, 'date'] = pd.to_datetime(klines['bob'])
            klines = klines[['code', 'date', 'open', 'close', 'high', 'low', 'volume']]
            print('Run code %s frequency %s klines len %s' % (code, f, len(klines)))
            db_ex.insert_klines(code, f, klines)
        except Exception as e:
            print('执行 %s 同步K线异常' % code)
            print(traceback.format_exc())
            time.sleep(10)
