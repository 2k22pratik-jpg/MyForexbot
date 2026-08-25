import yfinance as yf
import pandas as pd
from indicators import ema, rsi, atr

def get_data(symbol):
    try:
        # Get 1h and 15m data
        df_15 = yf.download(symbol, period="20d", interval="15m", progress=False, auto_adjust=True)
        df_1h = yf.download(symbol, period="60d", interval="1h", progress=False, auto_adjust=True)
        df_4h = yf.download(symbol, period="730d", interval="1h", progress=False, auto_adjust=True)
        if df_15.empty or df_1h.empty: return None
        if isinstance(df_15.columns, pd.MultiIndex): df_15.columns = df_15.columns.get_level_values(0)
        if isinstance(df_1h.columns, pd.MultiIndex): df_1h.columns = df_1h.columns.get_level_values(0)
        if isinstance(df_4h.columns, pd.MultiIndex): df_4h.columns = df_4h.columns.get_level_values(0)
        # Resample 1h -> 4H
        df_4h = df_4h.resample('4h').agg({'Open':'first','High':'max','Low':'min','Close':'last','Volume':'sum'}).dropna()
        
        for df in [df_15, df_1h, df_4h]:
            df['EMA20']=ema(df['Close'],20)
            df['EMA50']=ema(df['Close'],50)
            df['EMA200']=ema(df['Close'],200)
            df['RSI']=rsi(df['Close'],14)
            df['ATR']=atr(df,14)
        return {"15m":df_15, "1h":df_1h, "4h":df_4h}
    except Exception as e:
        print(f"Data error {symbol}: {e}")
        return None
