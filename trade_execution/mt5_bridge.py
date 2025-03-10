import MetaTrader5 as mt5
import json
import time
from trade_execution.risk_management import calculate_lot_size
from data_feeds.market_data import get_current_price
from logs.logger import log_message

# Load Configuration
def load_config():
    try:
        with open("config.json", "r") as file:
            return json.load(file)
    except Exception as e:
        log_message(f"❌ ERROR: Failed to load config.json - {str(e)}", level="error")
        exit()

config = load_config()

def initialize_mt5():
    """ Connect to MetaTrader 5 """
    if not mt5.initialize(login=config["mt5_login"], server=config["mt5_server"], password=config["mt5_password"]):
        log_message("❌ Failed to connect to MT5!", level="error")
        return False
    return True

def send_trade_action(action, symbol, sl=None, tp=None, trail=False, ticket=None):
    """ Sends trade signals to MT5 via global variables """
    if not initialize_mt5():
        return False
    
    lot = calculate_lot_size(config["account_balance"], config["risk_percentage"])  # AI-based lot size calculation
    price = get_current_price(symbol)

    # ✅ Set global variables in MT5 for EA to read
    mt5.global_variable_set("Trade_Action", action)
    mt5.global_variable_set("Trade_Symbol", symbol)
    mt5.global_variable_set("Trade_Lot", lot)
    mt5.global_variable_set("Trade_SL", sl if sl else 0)
    mt5.global_variable_set("Trade_TP", tp if tp else 0)
    mt5.global_variable_set("Trade_Trail", int(trail))
    
    if ticket:
        mt5.global_variable_set("Trade_Ticket", ticket)  # Needed for modify/close

    log_message(f"✅ Trade Sent: {action} {symbol}, Lot: {lot}, SL: {sl}, TP: {tp}, Trail: {trail}")
    return True

def monitor_ai_signals():
    """ Monitors AI trading signals and executes trades via MT5 """
    while True:
        try:
            with open("ai_signals.json", "r") as file:
                signals = json.load(file)

            for signal in signals:
                # ✅ Validate required fields before sending the trade
                if "action" not in signal or "symbol" not in signal:
                    log_message("⚠️ ERROR: Invalid signal structure - Missing 'action' or 'symbol'", level="error")
                    continue

                send_trade_action(
                    action=signal["action"],
                    symbol=signal["symbol"],
                    sl=signal.get("sl"),
                    tp=signal.get("tp"),
                    trail=signal.get("trail", False),
                    ticket=signal.get("ticket")
                )
            
        except Exception as e:
            log_message(f"⚠️ ERROR: Failed to read AI signals - {str(e)}", level="error")

        time.sleep(config["trading_interval"])  # Wait before checking again

if __name__ == "__main__":
    monitor_ai_signals()
