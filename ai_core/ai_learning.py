import os
import json
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.layers import LSTM, Dense, Dropout
from sklearn.preprocessing import MinMaxScaler
from data_feeds.news_sentiment import fetch_news_sentiment
from data_feeds.order_flow_analysis import fetch_order_flow
from trade_execution.trade_execution import execute_trade
from ai_core.past_data_ai import integrate_past_data_with_main_ai
from visualization.plot_results import plot_model_performance  # ✅ Ensured exists
from logs.logger import log_message

CONFIG_FILE = "config.json"
TRADE_HISTORY_FILE = "logs/trade_history.json"
MODEL_FILE = "ai_models/ai_model.keras"
SCALER_FILE = "ai_models/scaler.npy"

# ✅ Load Configurations
def load_config():
    """ Loads bot configurations from config.json """
    try:
        with open(CONFIG_FILE, "r") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        log_message("❌ ERROR: Invalid or missing config.json!", level="error")
        exit()

config = load_config()

# ✅ Load Trade History
def load_trade_history():
    """ Loads previous trade data to train AI. """
    try:
        with open(TRADE_HISTORY_FILE, "r", encoding="utf-8") as file:
            trade_data = json.load(file)
            if len(trade_data) >= 50:
                return trade_data
    except (FileNotFoundError, json.JSONDecodeError):
        pass
    log_message("⚠ Warning: Not enough trade data available. AI training might be skipped.")
    return []

# ✅ AI Trade Confidence Calculation
def ai_trade_confidence(symbol):
    """ Predicts trade confidence based on AI model """
    if not os.path.exists(MODEL_FILE):
        log_message("⚠ No AI model found! Training now...")
        train_ai()

    model = load_model(MODEL_FILE)
    order_flow = fetch_order_flow(symbol)
    news_sentiment = fetch_news_sentiment(symbol)

    order_flow = float(order_flow) if isinstance(order_flow, (int, float)) else 0.0
    news_sentiment = float(news_sentiment) if isinstance(news_sentiment, (int, float)) else 0.0

    past_insights_raw = integrate_past_data_with_main_ai()
    past_insights = float(np.array(past_insights_raw, dtype=np.float32).item())  # ✅ Fixed SymbolicTensor issue

    input_data = np.array([[order_flow, news_sentiment, past_insights, 1.0, 0.8]], dtype=np.float32)

    prediction = model.predict(input_data.reshape(1, 1, -1))
    confidence = prediction[0][0] if isinstance(prediction, np.ndarray) else float(prediction.numpy()[0][0])

    log_message(f"🔍 AI Confidence for {symbol}: {confidence}")
    return confidence

# ✅ AI Trade Decision Making
def ai_trade_decision(symbol):
    """ AI decides whether to trade based on confidence score """
    confidence = ai_trade_confidence(symbol)
    base_lot_size = config["base_lot_size"]  # ✅ Used from config.json

    if confidence > 0.6:
        log_message(f"✅ AI Confident: Executing BUY for {symbol}")
        execute_trade(symbol, "BUY", base_lot_size)
        return "BUY"

    elif confidence < 0.4:
        log_message(f"⚠ AI Bearish: Executing SELL for {symbol}")
        execute_trade(symbol, "SELL", base_lot_size)
        return "SELL"

    else:
        log_message(f"🔹 AI Neutral: No Trade for {symbol}")
        return "NEUTRAL"

# ✅ AI Model Training
def train_ai():
    """ Trains the AI model """
    trades = load_trade_history()
    X, y = prepare_data(trades)

    if len(y) < 50:
        log_message("⚠ Not enough real trade data. Training skipped.")
        return

    model = build_lstm_model() if not os.path.exists(MODEL_FILE) else load_model(MODEL_FILE)
    model.fit(X, y, epochs=200, batch_size=32, verbose=1)
    model.save(MODEL_FILE)

    plot_model_performance(MODEL_FILE)  # ✅ Ensuring visualization is implemented
    log_message(f"💾 Model Trained & Saved Successfully as {MODEL_FILE}")

# ✅ Prepare AI Training Data
def prepare_data(trades):
    """ Processes trade data for AI model """
    X, y = [], []
    scaler = MinMaxScaler()

    past_insights_raw = integrate_past_data_with_main_ai()
    past_insights = float(np.array(past_insights_raw, dtype=np.float32).item())  # ✅ Fixed SymbolicTensor issue

    for trade in trades:
        features = [
            trade.get("lot_size", 0),
            trade.get("stop_loss", 0),
            trade.get("take_profit", 0),
            trade.get("market_volatility", 0),
            past_insights
        ]
        X.append(features)
        y.append(1 if trade.get("profit", 0) > 0 else 0)

    if not X:
        log_message("⚠ No valid trade data found. Using dummy values...", level="warning")
        X = [[0, 0, 0, 0, past_insights]]
        y = [0]

    X_scaled = scaler.fit_transform(X)
    np.save(SCALER_FILE, scaler)
    return np.array(X_scaled).reshape(len(X_scaled), 1, -1), np.array(y)

# ✅ Build AI Model
def build_lstm_model():
    """ Builds an LSTM-based AI model for trading """
    model = Sequential([
        LSTM(128, return_sequences=True, input_shape=(1, 5)),
        Dropout(0.3),
        LSTM(128, return_sequences=False),
        Dropout(0.3),
        Dense(64, activation="relu"),
        Dense(1, activation="sigmoid")
    ])
    model.compile(optimizer="adam", loss="binary_crossentropy", metrics=["accuracy"])
    return model

# ✅ AI Learning Loop
def run_ai_learning():
    """ AI continuously learns and retrains every 5 minutes """
    log_message("🤖 AI Learning Module Running...")
    while True:
        train_ai()
        log_message("🔄 AI Updated & Learning Complete!")
        tf.keras.backend.clear_session()
        np.random.seed()
        time.sleep(300)

if __name__ == "__main__":
    run_ai_learning()
