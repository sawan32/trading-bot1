import sys
import os
import pandas as pd
import json
import MetaTrader5 as mt5
import numpy as np

# ✅ Ensure modules are correctly loaded
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from maths_engine.maths import calculate_volatility, adaptive_risk_factor, fetch_price_data
from logs.logger import log_message, log_risk_evaluation  # Logs for risk calculations

CONFIG_FILE = "config.json"

# ✅ Load Configurations (Fixed: Ensure Default Values)
def load_config():
    """ Loads bot configurations from config.json with default values """
    try:
        with open(CONFIG_FILE, "r") as file:
            config = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        log_message("❌ ERROR: Invalid or missing config.json!", level="error")
        exit()

    # ✅ Set default values if missing
    config.setdefault("max_risk_per_trade", 2)  # Default risk: 2% per trade
    config.setdefault("account_balance", 10000)  # Default balance if missing
    config.setdefault("min_lot_size", 0.01)  # Min lot size
    config.setdefault("max_lot_size", 5)  # Max lot size
    config.setdefault("min_margin_level", 100)  # Minimum margin level % before rejecting trades

    return config

config = load_config()

# ✅ AI-Based Lot Size Calculation
def calculate_lot_size(account_balance, risk_per_trade):
    """
    AI-based lot sizing based on available balance & risk tolerance.
    """
    lot_size = (account_balance * risk_per_trade) / 100000  # Standard Forex Lot Calculation
    lot_size = max(min(lot_size, config["max_lot_size"]), config["min_lot_size"])  # Ensure lot limits
    return round(lot_size, 2)

# ✅ Validate Trade Risk
def validate_trade_risk(symbol, trade_type, lot_size):
    """ Ensures the trade meets risk management criteria before execution """
    
    account_info = mt5.account_info()
    if account_info is None:
        log_message("❌ ERROR: Unable to fetch account info!", level="error")
        return False

    free_margin = account_info.margin_free
    balance = account_info.balance
    margin_level = (account_info.equity / account_info.margin) * 100 if account_info.margin > 0 else 9999
    risk_percentage = config.get("max_risk_per_trade", 2)  # Default risk per trade: 2%

    # ✅ Calculate maximum risk allowed
    max_risk_amount = (balance * risk_percentage) / 100
    required_margin = lot_size * 1000  # Approximate margin per lot

    # ✅ Check if the trade is within risk limits
    if free_margin < required_margin:
        log_message(f"❌ Trade Rejected: Not enough margin (Free: {free_margin}, Required: {required_margin})", level="error")
        return False

    # ✅ Ensure the trade does not exceed risk tolerance
    if required_margin > max_risk_amount:
        log_message(f"⚠ Trade Warning: Lot size {lot_size} exceeds max risk per trade!", level="warning")
        return False

    # ✅ Ensure margin level is above the minimum requirement
    if margin_level < config["min_margin_level"]:
        log_message(f"⚠ Trade Warning: Margin level {margin_level:.2f}% is too low!", level="warning")
        return False

    log_message(f"✅ Trade Passed Risk Validation: {symbol} ({trade_type}, Lot: {lot_size})")
    return True

# ✅ AI-Based Stop-Loss & Take-Profit Calculation
def adjust_sl_tp(symbol, trade_type):
    """
    AI-based SL/TP adjustment using volatility & market conditions.
    """
    # ✅ Fetch price data
    price_data = fetch_price_data(symbol)

    if price_data is None or len(price_data) < 14:
        log_message(f"❌ ERROR: Not enough data to calculate volatility for {symbol}", level="error")
        return None, None  # Skip SL/TP adjustment

    # ✅ Proceed with calculations
    volatility = calculate_volatility(price_data)
    risk_factor = adaptive_risk_factor(symbol)

    if trade_type == "BUY":
        stop_loss = round(volatility * risk_factor, 5)
        take_profit = round(volatility * risk_factor * 2, 5)  # Risk-Reward Ratio 1:2
    else:
        stop_loss = round(-volatility * risk_factor, 5)
        take_profit = round(-volatility * risk_factor * 2, 5)

    return stop_loss, take_profit

# ✅ Risk Filters for Trade Validation
def apply_risk_filters(symbol, trade_type, lot_size):
    """
    Ensures trade follows proper risk management rules before execution.
    """
    account_balance = config.get("account_balance", 10000)  # Use default if missing
    max_risk_per_trade = config.get("max_risk_per_trade", 2)

    calculated_lot = calculate_lot_size(account_balance, max_risk_per_trade)
    if lot_size > calculated_lot:
        return {"allowed": False, "reason": "Lot size exceeds risk limit"}

    # Log risk evaluation
    log_risk_evaluation(symbol, f"Trade Type: {trade_type} | Lot: {lot_size} | Balance: {account_balance} | Allowed Lot: {calculated_lot}")

    return {"allowed": True}

# ✅ Example Usage
if __name__ == "__main__":
    test_symbol = "USDJPYm"
    test_trade_type = "BUY"
    test_lot_size = 0.2

    print("🔍 Adjusted SL/TP:", adjust_sl_tp(test_symbol, test_trade_type))
    print("⚠️ Risk Validation:", apply_risk_filters(test_symbol, test_trade_type, test_lot_size))
