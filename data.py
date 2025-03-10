import os
import yfinance as yf
import json
import pandas as pd

# ✅ Define Folder for Saving Raw Data
RAW_DATA_FOLDER = "data_storage"
os.makedirs(RAW_DATA_FOLDER, exist_ok=True)  # ✅ Ensure Folder Exists

# ✅ Correct Symbol Mapping for Yahoo Finance
YAHOO_SYMBOLS = {
    "EURUSDm": "EURUSD=X",
    "USDJPYm": "USDJPY=X",
    "GBPUSDm": "GBPUSD=X"
}

# ✅ Load Configurations
CONFIG_FILE = "config.json"
def load_config():
    with open(CONFIG_FILE, "r") as file:
        return json.load(file)
config = load_config()

# ✅ Fetch & Save Historical Market Data (RAW)
def fetch_and_save_raw_data(symbol, years=30):
    """
    Fetches 10 years of historical data from Yahoo Finance and saves it as a raw CSV file.
    """
    print(f"📊 Fetching Raw Data for {symbol}...")

    yahoo_symbol = YAHOO_SYMBOLS.get(symbol, symbol)
    file_path = os.path.join(RAW_DATA_FOLDER, f"{symbol}.csv")  # ✅ Save File Path

    try:
        df = yf.download(yahoo_symbol, period="30y", interval="1d")

        if df.empty:
            print(f"⚠ No data found for {symbol}! Check symbol name.")
            return None

        # ✅ Save Raw Data to CSV
        df.to_csv(file_path)
        print(f"💾 Raw Data for {symbol} Saved at: {file_path}")

    except Exception as e:
        print(f"⚠ Error fetching data for {symbol}: {e}")

# ✅ Fetch & Save Data for All Symbols
for symbol in config["trading_pairs"]:
    fetch_and_save_raw_data(symbol)
