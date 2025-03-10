import json
import numpy as np
import optuna
import time
from tensorflow.keras.models import load_model
from sklearn.preprocessing import MinMaxScaler

CONFIG_FILE = "../config.json"
OPTIMIZED_PARAMS_FILE = "../logs/optimized_params.json"

# ✅ Load Configurations
def load_config():
    with open(CONFIG_FILE, "r") as file:
        return json.load(file)

config = load_config()

# ✅ AI Model Prediction
def ai_predict(data):
    model_path = os.path.join(os.path.dirname(__file__), "..", "ai_models", "ai_model.keras")
    if not os.path.exists(model_path):
        print(f"⚠ AI Model not found! Train AI before running optimization.")
        return None
    
    model = load_model(model_path)
    scaler = MinMaxScaler()
    scaled_data = scaler.fit_transform(data)
    predictions = model.predict(scaled_data.reshape(len(data), 1, -1))
    
    return predictions.flatten()

# ✅ AI-Based Trading Strategy Optimization
def objective(trial):
    stop_loss = trial.suggest_float("stop_loss", 0.001, 0.01)
    take_profit = trial.suggest_float("take_profit", 0.002, 0.02)
    position_size = trial.suggest_float("position_size", 0.01, 1.0)

    market_data = np.random.rand(1000, 5)
    ai_signals = ai_predict(market_data)

    profits = np.where(ai_signals > 0.7, take_profit,
                       np.where(ai_signals < 0.3, -stop_loss, 0))

    return profits.mean()

# ✅ Run Optimization Automatically
def optimize_strategy():
    while True:
        print("🚀 Running AI Strategy Optimization...")
        study = optuna.create_study(direction="maximize")
        study.optimize(objective, n_trials=100)

        best_params = study.best_params
        with open(OPTIMIZED_PARAMS_FILE, "w") as file:
            json.dump(best_params, file, indent=4)

        print(f"✅ Best Trading Strategy Parameters Found: {best_params}")
        time.sleep(86400)  # हर 24 घंटे बाद दोबारा optimize होगा

# ✅ Start Auto-Optimizing AI Strategy
if __name__ == "__main__":
    optimize_strategy()
