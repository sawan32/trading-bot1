import os
import pandas as pd
import ta  # ✅ Install using: pip install ta
import json

# ✅ Define Data Storage Folder
DATA_STORAGE_FOLDER = "data_storage"

# ✅ Load Configuration
CONFIG_FILE = "config.json"
def load_config():
    with open(CONFIG_FILE, "r") as file:
        return json.load(file)
config = load_config()

# ✅ Add Technical Indicators
def add_technical_indicators(symbol):
    file_path = os.path.join(DATA_STORAGE_FOLDER, f"{symbol}.csv")

    if not os.path.exists(file_path):
        print(f"⚠ Data file missing for {symbol}! Skipping...")
        return

    try:
        # ✅ Load the Cleaned CSV Data
        df = pd.read_csv(file_path)

        # ✅ Ensure `time` is in Datetime Format
        df["time"] = pd.to_datetime(df["time"])

        # ✅ Add RSI (Relative Strength Index)
        df["rsi"] = ta.momentum.RSIIndicator(df["close"], window=14).rsi()

        # ✅ Add MACD & MACD Signal
        macd = ta.trend.MACD(df["close"])
        df["macd"] = macd.macd()
        df["macd_signal"] = macd.macd_signal()

        # ✅ Add Bollinger Bands
        bollinger = ta.volatility.BollingerBands(df["close"], window=20, window_dev=2)
        df["boll_upper"] = bollinger.bollinger_hband()
        df["boll_lower"] = bollinger.bollinger_lband()

        # ✅ Fill Missing Values (NaN)
        df.fillna(method="bfill", inplace=True)

        # ✅ Save Updated Data with Indicators
        df.to_csv(file_path, index=False)
        print(f"✅ Indicators Added & Saved: {file_path}")

    except Exception as e:
        print(f"⚠ Error processing indicators for {symbol}: {e}")

# ✅ Process All Symbols
for symbol in config["trading_pairs"]:
    add_technical_indicators(symbol)
