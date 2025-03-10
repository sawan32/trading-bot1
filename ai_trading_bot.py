import time
import os
import json
import numpy as np
import tensorflow as tf
import matplotlib.pyplot as plt  # ✅ Added visualization support
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.layers import LSTM, Dense, Dropout
from tensorflow.keras.callbacks import EarlyStopping
from sklearn.preprocessing import MinMaxScaler

# ✅ Import all necessary modules
from ai_core.past_data_ai import integrate_past_data_with_main_ai
from ai_core.backtest_ai import run_full_backtest  # ✅ Backtesting module
from data_feeds.news_sentiment import fetch_news_sentiment
from data_feeds.order_flow_analysis import fetch_order_flow
from trade_execution.trade_execution import execute_trade
from trade_execution.risk_management import calculate_lot_size
from maths_engine.maths import calculate_volatility, adaptive_risk_factor
from visualizations.pattern_recognition import plot_patterns
from logs.logger import log_message

CONFIG_FILE = "config.json"
TRADE_HISTORY_FILE = "logs/trade_history.json"
MODEL_FILE = "ai_models/ai_model.keras"
SCALER_FILE = "ai_models/scaler.npy"

prev_confidence = 0.5  # Initial value for EMA smoothing

# ✅ Load Configurations
def load_config():
    try:
        with open(CONFIG_FILE, "r") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        log_message("❌ ERROR: Invalid or missing config.json!", level="error")
        exit()

config = load_config()

# ✅ AI Training Function
def train_ai():
    log_message("🔄 Training AI Model...")
    # Placeholder for AI training function
    log_message("💾 AI Model Training Completed.")

# ✅ AI Confidence Calculation with Market Volatility Integration
def ai_trade_confidence(symbol):
    if not os.path.exists(MODEL_FILE):
        log_message("⚠ No AI model found! Training now...")
        train_ai()
    
    model = load_model(MODEL_FILE)
    order_flow = float(fetch_order_flow(symbol) or 0.0)
    news_sentiment_list = fetch_news_sentiment(symbol)  # Get the list of news
    if isinstance(news_sentiment_list, list) and len(news_sentiment_list) > 0:
        news_sentiment = np.mean([SentimentIntensityAnalyzer().polarity_scores(headline)['compound'] for headline in news_sentiment_list])
    else:
        news_sentiment = 0.0  # Default sentiment score if no news available
    past_insights = np.array(integrate_past_data_with_main_ai(), dtype=np.float32).item()
    
    # ✅ Market Volatility Integration
    market_volatility = calculate_volatility(symbol)
    risk_factor = adaptive_risk_factor(symbol)

    log_message(f"📊 DEBUG: Order Flow = {order_flow}, News Sentiment = {news_sentiment}, Volatility = {market_volatility}")

    if order_flow == 0.0 and news_sentiment == 0.0:
        log_message(f"⚠ No market data for {symbol}. Skipping trade decision.")
        return 0.0

    input_data = np.array([[order_flow, news_sentiment, past_insights, market_volatility, risk_factor]], dtype=np.float32)
    
    # ✅ Reduce TensorFlow retracing warnings
    @tf.function(reduce_retracing=True)
    def ai_predict(model, input_data):
        return model(input_data.reshape(1, 1, -1))

    confidence = ai_predict(model, input_data)
    log_message(f"🔍 DEBUG: AI Confidence for {symbol} = {confidence.numpy()[0][0]}")
    return confidence.numpy()[0][0]

# ✅ AI Trading Decision with Dynamic Lot Sizing
def ai_trade_decision(symbol):
    confidence = ai_trade_confidence(symbol)
    lot_size = calculate_lot_size(symbol)

    spread = fetch_order_flow(symbol)
    log_message(f"🔍 DEBUG: Market Spread for {symbol} = {spread}")

    if confidence > 0.5:
        log_message(f"✅ AI Confident: Executing BUY for {symbol}")
        execute_trade(symbol, "BUY", lot_size)
        return "BUY"

# ✅ AI Learning & Visualization Loop
def run_ai_learning():
    log_message("🤖 AI Learning Module Running...")
    all_trades = []

    while True:
        log_message("🔄 DEBUG: AI training iteration started")
        train_ai()
        log_message("🔄 DEBUG: AI training iteration completed")

        for symbol in config.get("trading_pairs", []):
            log_message(f"📈 DEBUG: Checking AI trade decision for {symbol}")
            trade_action = ai_trade_decision(symbol)

            if trade_action:
                all_trades.append((symbol, trade_action))

        # ✅ Generate Trade Visualization Every 10 Iterations
        if len(all_trades) % 10 == 0:
            plot_trade_signals(all_trades)

        time.sleep(300)

if __name__ == "__main__":
    run_ai_learning()
