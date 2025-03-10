import requests
import time

# ✅ Binance API Endpoint for Order Book Data
BINANCE_API_URL = "https://api.binance.com/api/v3/depth"

# ✅ Mapping MT5 Symbols to Binance Symbols
SYMBOL_MAP = {
    "EURUSDm": "EURUSDT",
    "GBPUSDm": "GBPUSDT",
    "USDJPYm": "USDJPY",
    "AUDUSDm": "AUDUSDT",
    "USDCADm": "USDCAD",
    "USDCHFm": "USDCHF",
    "NZDUSDm": "NZDUSDT",
}

# ✅ Function to Fetch Order Flow from Binance
def fetch_binance_order_flow(mt5_symbol, limit=10):
    binance_symbol = SYMBOL_MAP.get(mt5_symbol)
    if not binance_symbol:
        print(f"⚠ Invalid Symbol Mapping for {mt5_symbol}")
        return None

    params = {"symbol": binance_symbol, "limit": limit}

    try:
        response = requests.get(BINANCE_API_URL, params=params, timeout=5)
        data = response.json()

        if "bids" not in data or "asks" not in data:
            print(f"⚠ Market Depth unavailable for {mt5_symbol} ({binance_symbol}). Order book is empty.")
            return None

        buy_orders = data["bids"][:limit]  # Top buy orders
        sell_orders = data["asks"][:limit]  # Top sell orders

        best_bid = float(buy_orders[0][0]) if buy_orders else None
        best_ask = float(sell_orders[0][0]) if sell_orders else None

        buy_volume = sum(float(order[1]) for order in buy_orders)
        sell_volume = sum(float(order[1]) for order in sell_orders)

        order_flow_data = {
            "best_bid": best_bid,
            "best_ask": best_ask,
            "buy_volume": round(buy_volume, 2),
            "sell_volume": round(sell_volume, 2),
        }

        return order_flow_data

    except requests.exceptions.RequestException as e:
        print(f"⚠ Binance API error: {e}")
        return None

# ✅ Function to Test Order Flow for All Symbols
def test_binance_order_flow():
    for mt5_symbol in SYMBOL_MAP.keys():
        print(f"📝 [INFO] 🔍 Fetching Order Flow for {mt5_symbol} ({SYMBOL_MAP[mt5_symbol]})...")
        order_flow = fetch_binance_order_flow(mt5_symbol)

        if order_flow:
            print(f"📊 Order Flow for {mt5_symbol}: {order_flow}")
        else:
            print(f"⚠ Market Depth unavailable for {mt5_symbol}.")
        time.sleep(1)  # ✅ Avoid hitting Binance rate limits

# ✅ Run Test When Script is Executed
if __name__ == "__main__":
    test_binance_order_flow()
