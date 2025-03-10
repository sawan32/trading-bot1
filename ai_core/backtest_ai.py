import sys
import os
import numpy as np
import pandas as pd
import tensorflow as tf
import matplotlib.pyplot as plt
from tensorflow.keras.models import load_model
from sklearn.preprocessing import MinMaxScaler
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from logs.logger import log_message


DATA_STORAGE = "data_storage"
PAST_DATA_MODEL_FILE = "ai_models/past_data.keras"
SCALER_FILE = "ai_models/scaler_past.npy"
INITIAL_BALANCE = 10000  # 💰 Starting capital
TRADE_RISK = 0.03  # 🔥 Risk per trade (3%)
SIGNAL_THRESHOLD = 0.52  # 🔥 Signal threshold for AI predictions

# ✅ Load Data from CSV
def load_backtest_data(symbol):
    file_path = os.path.join(DATA_STORAGE, f"{symbol}.csv")

    if not os.path.exists(file_path):
        log_message(f"⚠ Error: CSV file for {symbol} not found in {DATA_STORAGE} folder.", level="error")
        return None

    df = pd.read_csv(file_path)

    # ✅ Standardize Column Names
    df.columns = [col.lower().strip().replace(" ", "_") for col in df.columns]

    # ✅ Ensure 'time' column exists
    if "time" not in df.columns:
        log_message(f"⚠ Warning: 'time' column missing for {symbol}. Creating manually...", level="warning")
        df.insert(0, "time", pd.date_range(start="1993-01-01", periods=len(df), freq="D"))

    df["time"] = pd.to_datetime(df["time"]).astype(np.int64) // 10**9

    log_message(f"✅ Loaded Backtest Data for {symbol}: {df.shape}")
    return df

# ✅ Preprocess Data for Predictions
def preprocess_backtest_data(df):
    if not os.path.exists(SCALER_FILE):
        log_message("⚠ Error: Missing scaler file for AI model!", level="error")
        return None

    scaler = np.load(SCALER_FILE, allow_pickle=True).item()
    feature_cols = ["time", "open", "high", "low", "close", "volume", "rsi", "macd", "macd_signal", "boll_upper", "boll_lower"]
    
    if not all(col in df.columns for col in feature_cols):
        log_message("⚠ Warning: Missing required columns in dataset. Adjusting feature set.", level="warning")
        feature_cols = [col for col in feature_cols if col in df.columns]

    df = df[feature_cols]
    X = df.values
    X_scaled = scaler.transform(X)

    return np.array(X_scaled).reshape(len(X_scaled), 1, -1)

# ✅ Run Backtest with Optimized Position Sizing
def run_backtest(symbol):
    log_message(f"📊 Running Backtest for {symbol}...")

    df = load_backtest_data(symbol)
    if df is None:
        return

    X = preprocess_backtest_data(df)
    if X is None:
        return

    if not os.path.exists(PAST_DATA_MODEL_FILE):
        log_message(f"⚠ Error: Trained AI Model Not Found!", level="error")
        return

    model = load_model(PAST_DATA_MODEL_FILE)

    # ✅ Predict Buy/Sell Signals
    predictions = model.predict(X)
    signals = (predictions > SIGNAL_THRESHOLD).astype(int).flatten()

    # ✅ Simulate Trading
    balance = INITIAL_BALANCE
    position = 0
    trade_log = []
    trade_results = []

    for i in range(1, len(df)):
        trade_size = (balance * TRADE_RISK) / df["close"][i]  # 🔥 Dynamic Position Sizing  

        if signals[i] == 1 and balance > df["close"][i]:  # Buy condition
            position += trade_size
            balance -= trade_size * df["close"][i]
            trade_log.append((df["time"][i], symbol, "BUY", trade_size, df["close"][i]))
        
        elif signals[i] == 0 and position > 0:  # Sell condition
            balance += position * df["close"][i]
            trade_log.append((df["time"][i], symbol, "SELL", position, df["close"][i]))
            position = 0  # Reset position

    final_balance = balance + (position * df["close"].iloc[-1])

    # ✅ Store trade results
    trade_results.append({
        "symbol": symbol,
        "initial_balance": INITIAL_BALANCE,
        "final_balance": final_balance,
        "profit": final_balance - INITIAL_BALANCE,
        "total_trades": len(trade_log),
    })

    # ✅ Log Results
    log_message(f"💰 Initial Balance: ${INITIAL_BALANCE:.2f}")
    log_message(f"🏁 Final Balance: ${final_balance:.2f}")
    log_message(f"📈 Profit: ${final_balance - INITIAL_BALANCE:.2f}")
    log_message(f"📊 Total Trades: {len(trade_log)}")

    # ✅ Show last 5 trades
    for trade in trade_log[-5:]:
        log_message(f"🔹 Trade: {trade}")

    return trade_results

# ✅ Run Backtest for All Trading Pairs
def run_full_backtest():
    trading_pairs = ["EURUSDm", "USDJPYm", "GBPUSDm"]
    all_results = []
    for symbol in trading_pairs:
        results = run_backtest(symbol)
        if results:
            all_results.extend(results)

    # ✅ Visualize Backtest Results
    plot_backtest_results(all_results)

# ✅ Backtest Visualization
def plot_backtest_results(trade_results):
    """
    Plots the backtest results for analysis.
    """
    if not trade_results:
        log_message("⚠ No trade results available for plotting.", level="warning")
        return

    symbols = [result["symbol"] for result in trade_results]
    profits = [result["profit"] for result in trade_results]

    plt.figure(figsize=(10, 5))
    plt.bar(symbols, profits, color=['green' if p > 0 else 'red' for p in profits])
    plt.xlabel("Trading Pairs")
    plt.ylabel("Profit / Loss ($)")
    plt.title("Backtest Results - AI Trading Bot")
    plt.show()

# ✅ Run backtest on script execution
if __name__ == "__main__":
    run_full_backtest()
