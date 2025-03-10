import logging
import os
import datetime

LOG_FILE = "logs/ai_logs.txt"

LOGS_DIR = "logs"
if not os.path.exists(LOGS_DIR):
    os.makedirs(LOGS_DIR)

AI_LOG_FILE = os.path.join(LOGS_DIR, "ai_logs.txt")
TRADE_LOG_FILE = os.path.join(LOGS_DIR, "trade_history.json")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(AI_LOG_FILE),
        logging.StreamHandler()
    ]
)

def log_ai_decision(symbol, confidence, action):
    log_message = f"AI Decision - {symbol} | Confidence: {confidence:.2f} | Action: {action}"
    logging.info(log_message)

def log_trade_execution(symbol, trade_type, lot_size, price, stop_loss, take_profit):
    log_message = (
        f"Trade Executed - {symbol} | Type: {trade_type} | Lot: {lot_size} | "
        f"Price: {price} | SL: {stop_loss} | TP: {take_profit}"
    )
    logging.info(log_message)

def log_risk_evaluation(symbol, risk_score):
    log_entry = f"{datetime.datetime.now()} - RISK EVALUATION: {symbol} | Risk Score: {risk_score}\n"
    with open(AI_LOG_FILE, "a") as log_file:
        log_file.write(log_entry)
    print(log_entry)

def log_error(error_message):
    logging.error(f"ERROR: {error_message}")

def log_backtest_results(strategy_name, profit, win_rate, drawdown):
    log_message = (
        f"Backtest Result - Strategy: {strategy_name} | Profit: {profit} | "
        f"Win Rate: {win_rate}% | Max Drawdown: {drawdown}%"
    )
    logging.info(log_message)

def get_last_logs(n=10):
    try:
        with open(AI_LOG_FILE, "r") as file:
            lines = file.readlines()
            return "".join(lines[-n:])
    except FileNotFoundError:
        return "No logs found."

def log_message(message, level="info"):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] [{level.upper()}] {message}\n"

    with open(LOG_FILE, "a", encoding="utf-8") as log_file:
        log_file.write(log_entry)

    print(f"📝 {log_entry.strip()}")
