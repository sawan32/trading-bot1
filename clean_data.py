import os
import pandas as pd
import json

# ✅ Define Data Storage Folder
DATA_STORAGE_FOLDER = "data_storage"

# ✅ Load Configuration
CONFIG_FILE = "config.json"
def load_config():
    with open(CONFIG_FILE, "r") as file:
        return json.load(file)
config = load_config()

# ✅ Fix Header Issues & Clean CSV Data
def clean_and_save(symbol):
    file_path = os.path.join(DATA_STORAGE_FOLDER, f"{symbol}.csv")

    if not os.path.exists(file_path):
        print(f"⚠ Data file missing for {symbol}! Skipping...")
        return

    try:
        # ✅ Read CSV File (Skip First Two Rows to Fix Headers)
        df = pd.read_csv(file_path, skiprows=2)  # Skip first 2 rows (Remove 'Price' & 'Ticker' rows)

        # ✅ Rename Columns to Standard Format
        rename_dict = {
            df.columns[0]: "time",
            df.columns[1]: "close",
            df.columns[2]: "high",
            df.columns[3]: "low",
            df.columns[4]: "open",
            df.columns[5]: "volume"
        }
        df.rename(columns=rename_dict, inplace=True)

        # ✅ Ensure `time` Column Exists & Convert to Datetime
        df["time"] = pd.to_datetime(df["time"], errors="coerce")

        # ✅ Select Only Required Columns
        required_cols = ["time", "open", "high", "low", "close", "volume"]
        df = df[required_cols]

        # ✅ Save Cleaned Data Back
        df.to_csv(file_path, index=False)
        print(f"✅ Cleaned & Saved: {file_path}")

    except Exception as e:
        print(f"⚠ Error processing data for {symbol}: {e}")

# ✅ Process All Symbols
for symbol in config["trading_pairs"]:
    clean_and_save(symbol)
