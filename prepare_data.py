import os
import pandas as pd
import numpy as np
import json
from sklearn.preprocessing import MinMaxScaler

# ✅ Define Data Storage Folder
DATA_STORAGE_FOLDER = "data_storage"
PROCESSED_DATA_FOLDER = "processed_data"  # Folder to store final AI-ready data

# ✅ Load Configuration
CONFIG_FILE = "config.json"
def load_config():
    with open(CONFIG_FILE, "r") as file:
        return json.load(file)
config = load_config()

# ✅ Ensure Processed Data Folder Exists
if not os.path.exists(PROCESSED_DATA_FOLDER):
    os.makedirs(PROCESSED_DATA_FOLDER)

# ✅ Prepare Data for AI Training
def prepare_data_for_training(symbol):
    file_path = os.path.join(DATA_STORAGE_FOLDER, f"{symbol}.csv")

    if not os.path.exists(file_path):
        print(f"⚠ Data file missing for {symbol}! Skipping...")
        return

    try:
        # ✅ Load Data
        df = pd.read_csv(file_path)

        # ✅ Ensure Required Columns Exist
        required_columns = ["time", "open", "high", "low", "close", "volume", "rsi", "macd", "macd_signal", "boll_upper", "boll_lower"]
        if not all(col in df.columns for col in required_columns):
            print(f"⚠ Missing required columns in {symbol}. Skipping...")
            return

        # ✅ Convert `time` to DateTime format
        df["time"] = pd.to_datetime(df["time"])

        # ✅ Drop Time Column (AI doesn't need it for training)
        df.drop(columns=["time"], inplace=True)

        # ✅ Normalize Data (MinMax Scaling)
        scaler = MinMaxScaler()
        df_scaled = pd.DataFrame(scaler.fit_transform(df), columns=df.columns)

        # ✅ Save Processed Data for AI Training
        processed_file_path = os.path.join(PROCESSED_DATA_FOLDER, f"{symbol}_processed.csv")
        df_scaled.to_csv(processed_file_path, index=False)

        print(f"✅ AI Training Data Saved: {processed_file_path}")

    except Exception as e:
        print(f"⚠ Error processing AI data for {symbol}: {e}")

# ✅ Process All Symbols
for symbol in config["trading_pairs"]:
    prepare_data_for_training(symbol)
