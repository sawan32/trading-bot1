import os
import json
import numpy as np
import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt
from tensorflow.keras.models import load_model
from sklearn.preprocessing import MinMaxScaler
from datetime import datetime, timedelta

CONFIG_FILE = os.path.join(os.path.dirname(__file__), "..", "config.json")
BACKTEST_RESULTS_FILE = "../logs/backtest_results.json"

# ✅ Load Configurations
def load_config():
    with open(CONFIG_FILE, "r") as file:
        return json.load(file)

config = load_config()

# ✅ Automatically Fetch Historical Data
def fetch_historical_data(symbol):
    print(f"📊 Fetching Historical Data for {symbol}...")
    end_date = datetime.today().strftime('%Y-%m-%d')
    start_date = (datetime.today() - timedelta(days=5*365)).strftime('%Y-%m-%d')  # Last 5 years
    
    try:
        df = yf.download(symbol, start=start_date, end=end_date)
        if df.empty:
            print(f"⚠ No data found for {symbol}.")
            return None
        df.reset_index(inplace=True)
        df.to_csv(f"../data_feeds/historical_data/{symbol}.csv", index=False)
        return df
    except Exception as e:
        print(f"⚠ Error fetching data: {e}")
        return None

# ✅ AI Model Prediction
def ai_predict(symbol, data):
    model_path = f"../ai_models/ai_model.keras"
    if not os.path.exists(model_path):
        print(f"⚠ AI Model not found! Train AI before running backtest.")
        return None

    model = load_model(model_path)
    scaler = MinMaxScaler()
    scaled_data = scaler.fit_transform(data)
    predictions = model.predict(scaled_data.reshape(len(data), 1, -1))

    return predictions.flatten()

# ✅ Automated Backtesting Function
def run_backtest(symbol):
    df = fetch_historical_data(symbol)
    if df is None:
        return
    
    print(f"📊 Running Backtest on {symbol}...")
    
    features = df[['Open', 'High', 'Low', 'Close', 'Volume']].values
    df['AI_Signal'] = ai_predict(symbol, features)

    df['Trade'] = np.where(df['AI_Signal'] > 0.7, 'BUY',
                           np.where(df['AI_Signal'] < 0.3, 'SELL', 'HOLD'))

    df['PnL'] = np.where(df['Trade'] == 'BUY', df['Close'].shift(-1) - df['Close'],
                         np.where(df['Trade'] == 'SELL', df['Close'] - df['Close'].shift(-1), 0))

    df[['Date', 'Close', 'Trade', 'PnL']].to_csv(f"../logs/backtest_{symbol}.csv", index=False)

    results = {
        "symbol": symbol,
        "total_trades": len(df[df['Trade'] != 'HOLD']),
        "total_profit": df['PnL'].sum(),
        "win_rate": (df['PnL'] > 0).sum() / max(1, len(df[df['Trade'] != 'HOLD'])),
        "average_pnl": df['PnL'].mean()
    }

    with open(BACKTEST_RESULTS_FILE, "w") as file:
        json.dump(results, file, indent=4)

    print(f"✅ Backtest Completed for {symbol}! Results saved.")

# ✅ Self-Running Backtesting for All Trading Pairs
if __name__ == "__main__":
    trading_pairs = config["trading_pairs"]
    for symbol in trading_pairs:
        run_backtest(symbol)
