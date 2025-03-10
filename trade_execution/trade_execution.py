import json
import MetaTrader5 as mt5
import os
import time
from trade_execution.risk_management import validate_trade_risk, calculate_lot_size
from logs.logger import log_message
from trade_execution.mt5_bridge import send_trade_action

CONFIG_FILE = "config.json"

# ✅ Load Configurations
def load_config():
    try:
        with open(CONFIG_FILE, "r") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        log_message("❌ ERROR: Invalid or missing config.json!", level="error")
        exit()

config = load_config()

# ✅ Open Trade
def open_trade(symbol, trade_type):
    """ Sends Open Trade request via MT5 Bridge """
    lot_size = calculate_lot_size(config["account_balance"], config["risk_percentage"])
    
    if not validate_trade_risk(symbol, trade_type, lot_size):
        log_message(f"❌ Trade Risk Validation Failed for {symbol}. Skipping trade.", level="error")
        return False

    send_trade_action(action=trade_type, symbol=symbol, lot=lot_size)
    return True

# ✅ Modify Trade (SL/TP Update)
def modify_trade(ticket, sl, tp):
    """ Sends Modify Trade request via MT5 Bridge """
    send_trade_action(action="MODIFY", symbol=None, sl=sl, tp=tp, ticket=ticket)

# ✅ Close Trade
def close_trade(ticket):
    """ Sends Close Trade request via MT5 Bridge """
    send_trade_action(action="CLOSE", symbol=None, ticket=ticket)

# ✅ Manage Trades (Trailing SL, SL/TP adjustments)
def manage_trade(ticket, action, sl=None, tp=None, trail=None):
    """Handles trade modifications (Trailing, SL/TP updates)"""
    send_trade_action(action=action, symbol=None, sl=sl, tp=tp, trail=trail, ticket=ticket)

# ✅ AI Trade Signal Monitoring
def monitor_trade_signals():
    """ Monitors AI trading signals and executes trades """
    signals_file = "ai_signals.json"
    
    while True:
        if os.path.exists(signals_file):
            with open(signals_file, "r") as file:
                signals = json.load(file)
            
            for signal in signals:
                if "action" in signal and "symbol" in signal:
                    open_trade(signal["symbol"], signal["action"])
                
                if "sl" in signal and "tp" in signal:
                    modify_trade(signal["ticket"], signal["sl"], signal["tp"])
                
                if "trail" in signal and signal["trail"]:
                    manage_trade(signal["ticket"], "TRAIL", trail=True)

        time.sleep(config["trading_interval"])  # Wait before checking again

if __name__ == "__main__":
    monitor_trade_signals()
