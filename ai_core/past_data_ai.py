import os
import json
import numpy as np
import pandas as pd
import tensorflow as tf
from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.layers import LSTM, Dense, Dropout, BatchNormalization
from sklearn.preprocessing import MinMaxScaler

CONFIG_FILE = "config.json"
PAST_DATA_MODEL_FILE = "ai_models/past_data.keras"
SCALER_FILE = "ai_models/scaler_past.npy"
DATA_STORAGE = "data_storage"  # Folder where CSV files are stored

# ✅ Load Configuration
def load_config():
    with open(CONFIG_FILE, "r") as file:
        return json.load(file)

config = load_config()

# ✅ Load Data from CSV Instead of Fetching Again
def load_csv_data(symbol):
    file_path = os.path.join(DATA_STORAGE, f"{symbol}.csv")

    if not os.path.exists(file_path):
        print(f"⚠ Error: CSV file for {symbol} not found in {DATA_STORAGE} folder.")
        return None

    try:
        df = pd.read_csv(file_path)

        # ✅ Standardize Column Names
        df.columns = [col.lower().strip().replace(" ", "_") for col in df.columns]

        # ✅ Ensure 'time' column exists
        if "time" not in df.columns:
            print(f"⚠ Warning: 'time' column missing for {symbol}. Creating manually...")
            df.insert(0, "time", pd.date_range(start="1993-01-01", periods=len(df), freq="D"))

        # ✅ Convert Time to Unix Timestamp
        df["time"] = pd.to_datetime(df["time"]).astype(np.int64) // 10**9

        print(f"✅ Loaded & Processed Data for {symbol}: {df.shape}")
        return df

    except Exception as e:
        print(f"⚠ Error processing CSV for {symbol}: {e}")
        return None

# ✅ Generate Training Labels (BUY/SELL Signals)
def generate_trade_labels(df):
    df["target"] = np.where(df["close"].shift(-1) > df["close"], 1, 0)  # 1 = Buy, 0 = Sell
    return df

# ✅ Preprocess Data for AI Training
def preprocess_data(df):
    scaler = MinMaxScaler()
    feature_cols = ["time", "open", "high", "low", "close", "volume", "rsi", "macd", "macd_signal", "boll_upper", "boll_lower"]

    df = df[feature_cols + ["target"]]  # Ensure all required columns exist

    X = df[feature_cols].values
    y = df["target"].values  # ✅ Now using real buy/sell signals

    X_scaled = scaler.fit_transform(X)
    np.save(SCALER_FILE, scaler)

    return np.array(X_scaled).reshape(len(X_scaled), 1, -1), y  # Reshape for LSTM

# ✅ Train AI Model
def train_past_data_ai(symbol):
    df = load_csv_data(symbol)
    if df is None:
        print(f"⚠ No Data Available for {symbol}. Skipping Training...")
        return

    df = generate_trade_labels(df)  # ✅ Now using real trade signals
    X, y = preprocess_data(df)

    if os.path.exists(PAST_DATA_MODEL_FILE):
        print("🔄 Loading Existing Past Data Model for Incremental Training...")
        model = load_model(PAST_DATA_MODEL_FILE)
    else:
        print("✅ Training New Past Data Model from Scratch...")
        model = Sequential([
            LSTM(512, return_sequences=True, input_shape=(1, 11)),  # ✅ Adjusted for Large Dataset
            BatchNormalization(),
            Dropout(0.3),

            LSTM(256, return_sequences=False),
            BatchNormalization(),
            Dropout(0.3),

            Dense(128, activation="relu"),
            Dropout(0.2),

            Dense(64, activation="relu"),
            Dropout(0.2),

            Dense(1, activation="sigmoid")
        ])
        model.compile(optimizer=tf.keras.optimizers.Adam(learning_rate=0.0005),
                      loss="binary_crossentropy", metrics=["accuracy"])

    model.fit(X, y, epochs=150, batch_size=64, verbose=1)
    model.save(PAST_DATA_MODEL_FILE)
    print(f"💾 Past Data AI Model for {symbol} Trained & Saved!")

# ✅ Run AI Training Using Stored CSVs
def run_past_data_ai():
    trading_pairs = config["trading_pairs"]
    for symbol in trading_pairs:
        train_past_data_ai(symbol)
    print("✅ AI Successfully Trained Using Past Market Data!")
def integrate_past_data_with_main_ai():
    """
    Loads past AI model and provides insights to the main AI model.
    """
    if not os.path.exists(PAST_DATA_MODEL_FILE):
        print(f"⚠ Past Data Model Not Found! Training Now...")
        return 0.5  # Default neutral prediction
    
    model = load_model(PAST_DATA_MODEL_FILE)
    test_input = np.array([[0.5] * 11]).reshape(1, 1, -1)  # Ensure input shape matches model
    past_insights = model.predict(test_input)
    return past_insights[0][0]

if __name__ == "__main__":
    run_past_data_ai()
