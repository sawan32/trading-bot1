import pandas as pd
import matplotlib.pyplot as plt

def plot_trade_history(trade_history_file, mode="pnl"):
    df = pd.read_json(trade_history_file)
    df["trade_index"] = range(len(df))
    
    plt.figure(figsize=(12, 6))
    
    if mode == "pnl":
        # ✅ Rolling average for trend line
        window_size = 20  # Adjust for smoothing
        df["profit_smoothed"] = df["profit"].rolling(window=window_size, min_periods=1).mean()

        # ✅ Profit/Loss Bars
        plt.bar(df["trade_index"], df["profit"], color=['green' if x > 0 else 'red' for x in df["profit"]], alpha=0.5)
        
        # ✅ Trend line
        plt.plot(df["trade_index"], df["profit_smoothed"], color='blue', linewidth=1.5, label="Trend (Rolling Avg)")
        
        plt.xlabel("Trade Index")
        plt.ylabel("Profit/Loss (USD)")
        plt.title("AI Trading Performance Over Time")
        plt.legend()
    
    elif mode == "market":
        # ✅ Market price trend
        plt.plot(df["trade_index"], df["market_price"], color='cyan', linewidth=1.5)
        plt.xlabel("Time")
        plt.ylabel("Market Price (USD)")
        plt.title("Market Price Trend Over Time")
    
    # ✅ Smarter X-axis labels
    plt.xticks(df["trade_index"][::max(1, len(df) // 10)], rotation=45)
    
    plt.show()

# Run the visualization
if __name__ == "__main__":
    trade_history_file = r"C:\Users\Lenovo\Desktop\Trading bot\logs\trade_history.json"
    mode = "pnl"  # Change to "market" for market trend
    plot_trade_history(trade_history_file, mode)
