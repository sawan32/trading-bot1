import numpy as np
import random
import json

CONFIG_FILE = "config.json"

# ✅ Load Configurations
def load_config():
    with open(CONFIG_FILE, "r") as file:
        return json.load(file)

config = load_config()

# ✅ Q-Learning Algorithm for AI Trade Optimization
class QLearningAgent:
    def __init__(self, actions, learning_rate=0.1, discount_factor=0.95, exploration_rate=0.1):
        self.actions = actions
        self.learning_rate = learning_rate
        self.discount_factor = discount_factor
        self.exploration_rate = exploration_rate
        self.q_table = {}

    def get_q_value(self, state, action):
        return self.q_table.get((state, action), 0.0)

    def choose_action(self, state):
        if random.uniform(0, 1) < self.exploration_rate:
            return random.choice(self.actions)  # Explore
        q_values = [self.get_q_value(state, a) for a in self.actions]
        return self.actions[np.argmax(q_values)]  # Exploit

    def update_q_value(self, state, action, reward, next_state):
        max_future_q = max([self.get_q_value(next_state, a) for a in self.actions], default=0.0)
        current_q = self.get_q_value(state, action)
        new_q = current_q + self.learning_rate * (reward + self.discount_factor * max_future_q - current_q)
        self.q_table[(state, action)] = new_q

# ✅ Monte Carlo Simulation for Market Uncertainty Analysis
def monte_carlo_simulation(trials=10000, initial_balance=1000, risk_factor=0.02):
    """
    AI को estimate करने में मदद करता है कि risk लेने से कितना potential profit या loss हो सकता है।
    """
    outcomes = []
    for _ in range(trials):
        simulated_balance = initial_balance
        for _ in range(100):  # 100 trades simulation
            trade_outcome = np.random.choice([-1, 1], p=[risk_factor, 1 - risk_factor])
            simulated_balance += trade_outcome * np.random.uniform(10, 50)
        outcomes.append(simulated_balance)
    
    return np.mean(outcomes), np.std(outcomes)  # Returns expected balance & standard deviation

# ✅ Reinforcement Learning-Based Risk-Reward Calculation
def rl_risk_reward_analysis(trades, discount_factor=0.9):
    """
    AI trade history से सीखकर risk-reward ratio optimize करता है।
    """
    total_reward = 0
    for i, trade in enumerate(reversed(trades)):
        reward = trade["profit"] if trade["profit"] > 0 else -trade["stop_loss"]
        total_reward += (discount_factor ** i) * reward
    return total_reward / len(trades) if trades else 0

# ✅ Example Usage
if __name__ == "__main__":
    # Initialize Reinforcement Learning Agent
    actions = ["BUY", "SELL", "HOLD"]
    agent = QLearningAgent(actions)

    # Simulated Trade Data
    test_trades = [{"profit": np.random.uniform(-50, 100), "stop_loss": np.random.uniform(10, 30)} for _ in range(10)]

    print("🎮 Monte Carlo Expected Balance:", monte_carlo_simulation())
    print("📈 RL-Based Risk-Reward Score:", rl_risk_reward_analysis(test_trades))
    
    # AI Choosing an Action
    state = "Bullish"
    chosen_action = agent.choose_action(state)
    print(f"🤖 AI Chose Action: {chosen_action}")
