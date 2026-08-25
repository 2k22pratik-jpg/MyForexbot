def check_4h_trend(df):
    last = df.iloc[-1]
    prev = df.iloc[-2]
    if last['Close'] > last['EMA200'] and last['EMA50'] > last['EMA200'] and last['EMA50'] > prev['EMA50']:
        return "BULLISH"
    if last['Close'] < last['EMA200'] and last['EMA50'] < last['EMA200'] and last['EMA50'] < prev['EMA50']:
        return "BEARISH"
    return "NONE"

def check_1h_setup(df, trend4h):
    last = df.iloc[-1]
    score = 0
    details = []
    # Pullback to EMA20/50 but above/below EMA200
    if trend4h=="BULLISH":
        pullback = abs(last['Close']-last['EMA20']) < last['ATR']*0.8 or abs(last['Close']-last['EMA50']) < last['ATR']*0.8
        above200 = last['Close'] > last['EMA200']
        rsi_ok = 40 <= last['RSI'] <= 60
        if pullback and above200 and rsi_ok:
            return True, 20+15, ["1H confirmed","EMA pullback"]
    if trend4h=="BEARISH":
        pullback = abs(last['Close']-last['EMA20']) < last['ATR']*0.8 or abs(last['Close']-last['EMA50']) < last['ATR']*0.8
        below200 = last['Close'] < last['EMA200']
        rsi_ok = 40 <= last['RSI'] <= 60
        if pullback and below200 and rsi_ok:
            return True, 20+15, ["1H confirmed","EMA pullback"]
    return False, 0, []

def check_15m_entry(df, trend):
    last = df.iloc[-1]
    prev = df.iloc[-2]
    # Swing high/low breakout
    swing_high = df['High'].iloc[-6:-1].max()
    swing_low = df['Low'].iloc[-6:-1].min()
    if trend=="BULLISH":
        breakout = last['Close'] > swing_high
        rsi_up = last['RSI'] > 50 and prev['RSI'] <= 55
        reversal = last['Close'] > last['Open'] and last['Close'] > prev['High']
        if breakout and rsi_up and reversal:
            return True, 15+10, ["15M breakout","RSI confirm"]
    if trend=="BEARISH":
        breakout = last['Close'] < swing_low
        rsi_down = last['RSI'] < 50 and prev['RSI'] >= 45
        reversal = last['Close'] < last['Open'] and last['Close'] < prev['Low']
        if breakout and rsi_down and reversal:
            return True, 15+10, ["15M breakout","RSI confirm"]
    return False, 0, []

def score_setup(data):
    df4h, df1h, df15 = data['4h'], data['1h'], data['15m']
    trend4h = check_4h_trend(df4h)
    if trend4h=="NONE": return None
    score = 0
    reasons=[]
    # 4H +25
    score+=25; reasons.append("4H trend")
    # 1H
    ok1h, s1h, r1h = check_1h_setup(df1h, trend4h)
    if not ok1h: return None
    score+=s1h; reasons+=r1h
    # 15M
    ok15, s15, r15 = check_15m_entry(df15, trend4h)
    if not ok15: return None
    score+=s15; reasons+=r15
    # ATR volatility +10
    atr_ok = df15['ATR'].iloc[-1] > df15['ATR'].iloc[-20:].mean()*0.7
    if atr_ok: score+=10; reasons.append("Good ATR")
    # RR +5 (we guarantee 1:2)
    score+=5; reasons.append("RR 1:2")
    
    if score < 75: return None
    return {"trend":trend4h, "score":score, "reasons":reasons, "atr":df15['ATR'].iloc[-1], "price":df15['Close'].iloc[-1]}
