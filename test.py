import MetaTrader5 as mt5
import json
import time
from trade_execution.risk_management import calculate_lot_size
from data_feeds.market_data import get_current_price

# Load Configuration
def load_config():
    with open("config.json", "r") as file:
        return json.load(file)

config = load_config()

def initialize_mt5():
    """ Connect to MetaTrader 5 """
    if not mt5.initialize(login=config["mt5_login"], server=config["mt5_server"], password=config["mt5_password"]):
        print("❌ Failed to connect to MT5!")
        return False
    return True

def send_trade_action(action, symbol, sl=None, tp=None, trail=False, ticket=None):
    """ Sends trade signals to MT5 """
    if not initialize_mt5():
        return False
    
    lot = calculate_lot_size(symbol, config["risk_percentage"])  # AI-based lot size calculation
    price = get_current_price(symbol)
    
    mt5.global_variable_set("Trade_Action", action)
    mt5.global_variable_set("Trade_Symbol", symbol)
    mt5.global_variable_set("Trade_Lot", lot)
    mt5.global_variable_set("Trade_SL", sl if sl else 0)
    mt5.global_variable_set("Trade_TP", tp if tp else 0)
    mt5.global_variable_set("Trade_Trail", int(trail))
    
    if ticket:
        mt5.global_variable_set("Trade_Ticket", ticket)  # Needed for modify/close
    
    print(f"✅ Trade Sent: {action} {symbol}, Lot: {lot}, SL: {sl}, TP: {tp}, Trail: {trail}")
    return True

def monitor_ai_signals():
    """ Monitors AI trading signals and executes trades """
    while True:
        with open("ai_signals.json", "r") as file:
            signals = json.load(file)
        
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
