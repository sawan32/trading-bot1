import MetaTrader5 as mt5
import json
import time
from trade_execution.risk_management import validate_trade_risk, calculate_lot_size
from logs.logger import log_message

# ✅ Load Configuration
def load_config():
    try:
        with open("config.json", "r") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        log_message("❌ ERROR: Invalid or missing config.json!", level="error")
        exit()

config = load_config()

# ✅ Initialize MT5
def initialize_mt5():
    """Connect to MetaTrader 5"""
    if not mt5.initialize(login=config["mt5_login"], server=config["mt5_server"], password=config["mt5_password"]):
        log_message("❌ Failed to connect to MT5!", level="error")
        return False
    return True

# ✅ Fetch Current Price for a Symbol
def get_current_price(symbol):
    """ Fetches current price for the given symbol """
    if not initialize_mt5():
        return None

    symbol_info = mt5.symbol_info_tick(symbol)
    if not symbol_info:
        log_message(f"❌ ERROR: Failed to get market data for {symbol}", level="error")
        return None

    return symbol_info.ask if symbol_info.ask else None

# ✅ Send Trade Action to MT5 EA (No Direct Execution)
def send_trade_action(action, symbol, sl=None, tp=None, trail=False, ticket=None):
    """ Sends trade instructions to MT5 EA via Global Variables """
    if not initialize_mt5():
        return False

    lot = calculate_lot_size(config["account_balance"], config["risk_percentage"])  # AI-based lot size
    price = get_current_price(symbol)

    if not price:
        log_message(f"❌ ERROR: Cannot execute trade, price fetch failed for {symbol}", level="error")
        return False

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

# ✅ Monitor AI Signals and Execute Trades
def monitor_ai_signals():
    """ Monitors AI trading signals and sends them to MT5 """
    while True:
        try:
            with open("ai_signals.json", "r") as file:
                signals = json.load(file)
        except Exception as e:
            log_message(f"❌ ERROR: Failed to read AI signals: {str(e)}", level="error")
            time.sleep(config["trading_interval"])
            continue

        for signal in signals:
            send_trade_action(
                action=signal["action"],
                symbol=signal["symbol"],
                sl=signal.get("sl"),
                tp=signal.get("tp"),
                trail=signal.get("trail", False),
                ticket=signal.get("ticket")
            )

        time.sleep(config["trading_interval"])  # Wait before checking again

if __name__ == "__main__":
    monitor_ai_signals()
