#!/usr/bin/python3
# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
from utils.diff import add_diff,eps


def signal(*args):
    # TmaBias
    df = args[0]
    n = args[1]
    diff_num = args[2]
    factor_name = args[3]
    
    """
    N=20
    CLOSE_MA=MA(CLOSE,N)
    TMA=MA(CLOSE_MA,N)
    TMA 均线与其他的均线类似，不同的是，像 EMA 这类的均线会赋予
    越靠近当天的价格越高的权重，而 TMA 则赋予考虑的时间段内时间
    靠中间的价格更高的权重。如果收盘价上穿/下穿 TMA 则产生买入/
    卖出信号。
    """
    ma = df['close'].rolling(n, min_periods=1).mean()  # CLOSE_MA=MA(CLOSE,N)
    tma = ma.rolling(n, min_periods=1).mean()  # TMA=MA(CLOSE_MA,N)
    df[factor_name] = df['close'] / (tma + eps) - 1

    if diff_num > 0:
        return add_diff(df, diff_num, factor_name)
    else:
        return df