ACCOUNT = {
    "START_BALANCE": 10000,
    "RISK_PER_TRADE": 0.005, # 0.5%
    "MAX_OPEN_TRADES": 3,
    "MAX_DAILY_LOSS_PCT": 0.02, # 2%
    "MIN_SCORE": 75
}

PAIRS = [
    "EURUSD=X", "GBPUSD=X", "USDJPY=X", "USDCHF=X",
    "AUDUSD=X", "USDCAD=X", "NZDUSD=X", "EURGBP=X",
    "EURJPY=X", "GBPJPY=X"
]

NAMES = {
    "EURUSD=X":"EUR/USD", "GBPUSD=X":"GBP/USD", "USDJPY=X":"USD/JPY",
    "USDCHF=X":"USD/CHF", "AUDUSD=X":"AUD/USD", "USDCAD=X":"USD/CAD",
    "NZDUSD=X":"NZD/USD", "EURGBP=X":"EUR/GBP", "EURJPY=X":"EUR/JPY",
    "GBPJPY=X":"GBP/JPY"
}

# Correlation groups - don't take 2 buys in same group if >2 exposure
CORR_GROUPS = {
    "USD_STRONG": ["USDJPY=X", "USDCAD=X", "USDCHF=X"],
    "EUR": ["EURUSD=X", "EURGBP=X", "EURJPY=X"],
    "GBP": ["GBPUSD=X", "EURGBP=X", "GBPJPY=X"],
    "JPY": ["USDJPY=X", "EURJPY=X", "GBPJPY=X"]
}
