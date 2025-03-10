import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

# ✅ Function to Visualize AI Trading Predictions
def plot_trade_predictions(predictions, actual_values):
    plt.figure(figsize=(12, 6))
    plt.plot(actual_values, label='Actual Prices', color='blue')
    plt.plot(predictions, label='AI Predictions', linestyle='dashed', color='red')
    plt.xlabel('Time')
    plt.ylabel('Price')
    plt.title('AI Trade Predictions vs Actual Market Data')
    plt.legend()
    plt.grid()
    plt.show()

# ✅ Function to Show AI Confidence Levels
def plot_ai_confidence(confidences):
    plt.figure(figsize=(10, 5))
    plt.bar(range(len(confidences)), confidences, color='green')
    plt.xlabel('Trade Index')
    plt.ylabel('Confidence Level')
    plt.title('AI Confidence in Trade Decisions')
    plt.show()

# ✅ Function to Generate Heatmap for Trading Data
def plot_heatmap(trade_data):
    plt.figure(figsize=(10, 6))
    sns.heatmap(trade_data.corr(), annot=True, cmap='coolwarm', linewidths=0.5)
    plt.title('Trading Data Correlation Heatmap')
    plt.show()

# ✅ Function to Visualize AI Learning Progress
def plot_training_progress(history):
    plt.figure(figsize=(10, 5))
    plt.plot(history.history['loss'], label='Loss', color='red')
    plt.plot(history.history['accuracy'], label='Accuracy', color='green')
    plt.xlabel('Epochs')
    plt.ylabel('Metrics')
    plt.title('AI Training Progress')
    plt.legend()
    plt.show()

if __name__ == "__main__":
    print("🔍 AI Visualization Module Ready!")
