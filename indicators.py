import pandas as pd
import numpy as np

def ema(s, p): return s.ewm(span=p, adjust=False).mean()
def rsi(s, p=14):
    d = s.diff()
    g = d.clip(lower=0).ewm(alpha=1/p, adjust=False).mean()
    l = (-d.clip(upper=0)).ewm(alpha=1/p, adjust=False).mean()
    rs = g / (l + 1e-9)
    return 100 - (100 / (1+rs))
def atr(df, p=14):
    hl = df['High']-df['Low']
    hc = (df['High']-df['Close'].shift()).abs()
    lc = (df['Low']-df['Close'].shift()).abs()
    tr = pd.concat([hl,hc,lc], axis=1).max(axis=1)
    return tr.ewm(alpha=1/p, adjust=False).mean()
