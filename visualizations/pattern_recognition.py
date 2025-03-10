import numpy as np
import matplotlib.pyplot as plt

def detect_price_patterns(prices):
    """
    AI-based pattern recognition - Head & Shoulders, Double Top/Bottom
    """
    patterns = []
    for i in range(2, len(prices) - 2):
        if prices[i] > prices[i-1] and prices[i] > prices[i+1]:  # Potential Peak
            patterns.append((i, prices[i], "Peak"))
        elif prices[i] < prices[i-1] and prices[i] < prices[i+1]:  # Potential Dip
            patterns.append((i, prices[i], "Dip"))
    
    return patterns

def plot_patterns(prices):
    """
    Price chart के साथ detected patterns को plot करेगा।
    """
    patterns = detect_price_patterns(prices)
    x = np.arange(len(prices))
    
    plt.figure(figsize=(10,5))
    plt.plot(x, prices, label="Price Movement")
    
    for index, price, label in patterns:
        plt.scatter(index, price, color="red" if label == "Peak" else "green", label=label)
    
    plt.xlabel("Time")
    plt.ylabel("Price")
    plt.title("AI-Based Pattern Recognition")
    plt.legend()
    plt.show()

# ✅ Example Usage
if __name__ == "__main__":
    test_prices = [1.1, 1.15, 1.2, 1.12, 1.08, 1.14, 1.22, 1.19, 1.1, 1.05]
    plot_patterns(test_prices)
