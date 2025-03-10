import json
import os
import random

TRADE_HISTORY_FILE = "logs/trade_history.json"

def generate_dummy_trades():
    dummy_trades = []
    for _ in range(1000):  # Increased from 100 to 1000
        dummy_trades.append({
            "symbol": random.choice(["EURUSDm", "USDJPYm", "GBPUSDm"]),
            "lot_size": round(random.uniform(0.1, 5), 2),
            "stop_loss": round(random.uniform(10, 50), 2),
            "take_profit": round(random.uniform(10, 50), 2),
            "market_volatility": round(random.uniform(0.1, 1.5), 2),
            "profit": round(random.uniform(-50, 100), 2)  # Mixed profits and losses
        })
    
    os.makedirs("logs", exist_ok=True)
    with open(TRADE_HISTORY_FILE, "w", encoding="utf-8") as file:
        json.dump(dummy_trades, file, indent=4)
    
    print(f"✅ Generated {len(dummy_trades)} Dummy Trades for AI Learning!")

if __name__ == "__main__":
    generate_dummy_trades()
