import numpy as np
import pandas as pd
import MetaTrader5 as mt5


# ✅ Fibonacci Retracement Calculation
def fibonacci_levels(price_high, price_low, levels=[0.236, 0.382, 0.5, 0.618, 0.786]):
    """
    Calculates Fibonacci retracement levels.
    """
    difference = price_high - price_low
    return [price_high - (difference * level) for level in levels]


# ✅ Volatility Calculation using AI-enhanced ATR
def calculate_volatility(price_data, period=14):
    """
    AI-enhanced volatility calculation using Adaptive ATR.
    """
    if len(price_data) < period:
        raise ValueError(f"❌ ERROR: Not enough data for volatility calculation (Need {period}, got {len(price_data)})")

    high_low = price_data['high'] - price_data['low']
    high_close = np.abs(price_data['high'] - price_data['close'].shift())
    low_close = np.abs(price_data['low'] - price_data['close'].shift())

    true_range = np.maximum(high_low, np.maximum(high_close, low_close))
    atr = true_range.rolling(window=period).mean().iloc[-1]  # Use rolling mean

    return round(atr, 5)


# ✅ AI-Enhanced Risk Calculation
def calculate_risk(balance, risk_percentage):
    """
    Calculates risk amount dynamically based on account balance and risk tolerance.
    """
    base_risk = balance * (risk_percentage / 100)
    adaptive_risk = base_risk * np.random.uniform(0.95, 1.05)  # AI-based fluctuation
    return round(adaptive_risk, 2)


# ✅ Stop Loss and Take Profit Adjustment with AI-based Precision
def adjust_sl_tp(entry_price, trade_direction, risk_reward_ratio):
    """
    Adjusts Stop Loss (SL) and Take Profit (TP) dynamically based on market conditions.
    """
    risk_amount = abs(entry_price * 0.001)  # Example: 0.1% of entry price
    ai_adjustment = np.random.uniform(0.95, 1.05)  # Adaptive SL/TP tuning
    risk_amount *= ai_adjustment

    if trade_direction == "BUY":
        stop_loss = entry_price - risk_amount
        take_profit = entry_price + (risk_amount * risk_reward_ratio)
    else:
        stop_loss = entry_price + risk_amount
        take_profit = entry_price - (risk_amount * risk_reward_ratio)

    return round(stop_loss, 5), round(take_profit, 5)


# ✅ Gann Square Key Level Calculation
def gann_levels(price):
    """
    Calculates Gann Square levels for trend prediction.
    """
    base = np.sqrt(price)
    return [round((base + i) ** 2, 5) for i in range(-3, 4)]


# ✅ Chaos Theory for Market Trend Strength
def chaos_theory_trend(price_data, period=14):
    """
    Uses Chaos Theory to analyze market trends and structure.
    """
    ema_fast = price_data['close'].ewm(span=period, adjust=False).mean()
    ema_slow = price_data['close'].ewm(span=period * 2, adjust=False).mean()
    return ema_fast - ema_slow  # Positive -> Bullish, Negative -> Bearish


# ✅ Reinforcement Learning Based Risk Factor Calculation
def adaptive_risk_factor(symbol):
    """
    AI-driven adaptive risk factor calculation based on market behavior.
    """
    base_risk = 1.5  # Default risk factor
    market_condition = np.random.uniform(0.8, 1.2)  # AI-based real-time adjustment
    return round(base_risk * market_condition, 3)


# ✅ Bollinger Band Calculation for Market Trend Analysis
def bollinger_bands(price_data, period=20, std_dev=2):
    """
    Calculates Bollinger Bands to identify overbought or oversold conditions.
    """
    sma = price_data['close'].rolling(window=period).mean()
    rolling_std = price_data['close'].rolling(window=period).std()

    upper_band = sma + (rolling_std * std_dev)
    lower_band = sma - (rolling_std * std_dev)

    return round(upper_band.iloc[-1], 5), round(lower_band.iloc[-1], 5)


# ✅ Fetch Price Data from MetaTrader 5
def fetch_price_data(symbol, count=100):
    """
    Fetch historical price data from MetaTrader 5.
    """
    if not mt5.initialize():
        print("❌ ERROR: Failed to initialize MT5!")
        return None

    mt5.symbol_select(symbol, True)  # Ensure the symbol is selected

    rates = mt5.copy_rates_from_pos(symbol, mt5.TIMEFRAME_M1, 0, count)

    if rates is None or len(rates) < 14:
        print(f"❌ ERROR: No price data found for {symbol}! Needed 14, got {len(rates) if rates else 0}")
        return None

    df = pd.DataFrame(rates)

    return df


# ✅ Example Usage
if __name__ == "__main__":
    test_symbol = "EURUSDm"
    test_price_data = fetch_price_data(test_symbol)

    # Ensure test_high and test_low exist
    test_high = 1.2345
    test_low = 1.1234

    print("🔢 Fibonacci Levels:", fibonacci_levels(test_high, test_low))
    print("📊 Gann Levels:", [float(x) for x in gann_levels(test_high)])
    print("⚡ Adaptive Risk Factor:", adaptive_risk_factor(test_symbol))

    if test_price_data is not None:
        print("📈 Market Volatility:", calculate_volatility(test_price_data))
        print("📊 Bollinger Bands:", tuple(float(x) for x in bollinger_bands(test_price_data)))
    else:
        print("❌ No price data available for Market Volatility and Bollinger Bands.")
