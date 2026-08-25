from flask import Flask
import threading, time, datetime, pytz, math, random
from config import ACCOUNT, PAIRS, NAMES
from market_data import get_data
from strategy import score_setup

app = Flask(__name__)

balance = ACCOUNT["START_BALANCE"]
open_trades=[]
history=[]
daily_pnl=0
last_day=None
consec_losses=0

def calc_position_size(price, atr, balance):
    risk_dollars = balance * ACCOUNT["RISK_PER_TRADE"]
    sl_dist = atr * 1.5
    if sl_dist==0: return 0
    # pip value approx $10 per lot for most, for simplicity risk/ sl
    # Position size in units = risk / sl_dist * price (forex)
    lots = risk_dollars / sl_dist / 10  # simplified lot calc
    lots = max(0.01, min(lots, 2.0))
    return round(lots,2), risk_dollars

def can_open_pair(symbol):
    for t in open_trades:
        if t['pair']==symbol: return False
    return True

def check_correlation(new_pair, new_dir):
    # count same USD exposure
    if len(open_trades)>=ACCOUNT["MAX_OPEN_TRADES"]: return False
    # simple: don't allow 3 trades same direction on USD majors
    same_dir_usd = sum(1 for t in open_trades if t['direction']==new_dir)
    if same_dir_usd>=2: return False
    return True

def close_expired():
    global balance, daily_pnl, consec_losses
    for t in open_trades[:]:
        # Simulate TP/SL hit with random walk for paper trading
        # In live paper, we check current price
        data = get_data(t['pair'])
        if not data: continue
        price = data['15m']['Close'].iloc[-1]
        # SL/TP check
        hit=False; pnl=0
        if t['direction']=="BUY":
            if price <= t['sl']: pnl = -t['risk_d']; hit="SL"
            elif price >= t['tp']: pnl = t['risk_d']*2; hit="TP"
        else:
            if price >= t['sl']: pnl = -t['risk_d']; hit="SL"
            elif price <= t['tp']: pnl = t['risk_d']*2; hit="TP"
        if hit:
            balance+=pnl
            daily_pnl+=pnl
            open_trades.remove(t)
            t['exit']=price; t['pnl']=pnl; t['result']=hit; t['close_time']=datetime.datetime.now().isoformat()
            history.insert(0,t)
            if pnl<0: consec_losses+=1
            else: consec_losses=0

def bot_loop():
    global daily_pnl, last_day, balance, consec_losses
    while True:
        try:
            ist = pytz.timezone('Asia/Kolkata')
            today = datetime.datetime.now(ist).date()
            if last_day != today:
                daily_pnl=0
                last_day=today
                print(f"New day {today}")
            # Daily loss halt
            if daily_pnl <= -ACCOUNT["START_BALANCE"]*ACCOUNT["MAX_DAILY_LOSS_PCT"]:
                print("Daily loss limit hit, pausing")
                time.sleep(900)
                continue
            if consec_losses>=3:
                print("3 losses, cooldown 30m")
                time.sleep(1800)
                consec_losses=0
                continue
            close_expired()
            candidates=[]
            for sym in PAIRS:
                if not can_open_pair(sym): continue
                data = get_data(sym)
                if not data: continue
                setup = score_setup(data)
                if setup:
                    if not check_correlation(sym, setup['trend']): continue
                    candidates.append((sym, setup))
            # Rank by score
            candidates.sort(key=lambda x: x[1]['score'], reverse=True)
            for sym, setup in candidates[:ACCOUNT["MAX_OPEN_TRADES"]-len(open_trades)]:
                price = setup['price']
                atr = setup['atr']
                lots, risk_d = calc_position_size(price, atr, balance)
                sl = price - atr*1.5 if setup['trend']=="BULLISH" else price + atr*1.5
                tp = price + atr*3 if setup['trend']=="BULLISH" else price - atr*3
                direction = "BUY" if setup['trend']=="BULLISH" else "SELL"
                trade={
                    "pair":sym, "name":NAMES[sym], "direction":direction,
                    "entry":price, "sl":sl, "tp":tp, "atr":atr,
                    "lots":lots, "risk_d":risk_d, "score":setup['score'],
                    "reasons":",".join(setup['reasons']), "open_time":datetime.datetime.now().isoformat()
                }
                open_trades.append(trade)
                print(f"OPEN {NAMES[sym]} {direction} Score {setup['score']}")
            time.sleep(900) # every 15 min as per spec
        except Exception as e:
            print("Loop error", e)
            time.sleep(60)

threading.Thread(target=bot_loop, daemon=True).start()

@app.route('/')
def dash():
    win = sum(1 for h in history if h['pnl']>0)
    total = len(history)
    wr = f"{win/total*100:.1f}%" if total else "0%"
    dd = min(0, daily_pnl)
    html=f"""
    <h2>FOREX 10-PAIR PAPER BOT - ${balance:.2f}</h2>
    <p>Daily PnL: ${daily_pnl:.2f} | Open: {len(open_trades)}/3 | WR: {wr} | Balance: ${balance:.2f}</p>
    <h3>Open Trades</h3>
    {'<br>'.join([f"{t['name']} {t['direction']} Entry {t['entry']:.5f} SL {t['sl']:.5f} TP {t['tp']:.5f} Score {t['score']} Lots {t['lots']}" for t in open_trades]) or 'None'}
    <h3>Last 20 History</h3>
    {'<br>'.join([f"{h['name']} {h['direction']} {h['result']} PnL ${h['pnl']:.2f} Score {h['score']}" for h in history[:20]])}
    <p>Scanning every 15min - 4H/1H/15M strategy</p>
    """
    return html

if __name__=="__main__":
    app.run(host="0.0.0.0", port=10000)
