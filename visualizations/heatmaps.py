import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

def generate_heatmap(order_flow_data):
    """
    Market liquidity & institutional order flow को heatmap में visualize करेगा।
    """
    data_matrix = np.array(order_flow_data).reshape((10, 10))  # ✅ Adjust based on order flow data
    plt.figure(figsize=(8,6))
    sns.heatmap(data_matrix, cmap="coolwarm", annot=True, fmt=".2f")
    plt.title("Market Liquidity & Order Flow Heatmap")
    plt.show()

# ✅ Example Usage
if __name__ == "__main__":
    fake_order_flow = np.random.rand(100) * 2 - 1  # ✅ Generate random order flow data
    generate_heatmap(fake_order_flow)
