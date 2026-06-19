"""
Reinforcement Learning Agent
Uses sumo-rl and stable-baselines3 to train an agent.
"""

import os
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
import config

try:
    from sumo_rl import SumoEnvironment
    from stable_baselines3 import PPO, DQN
    from stable_baselines3.common.vec_env import DummyVecEnv
except ImportError:
    print("Warning: sumo-rl or stable-baselines3 not installed.")

from src.agents.reward_functions import emission_decoupling_reward


class RLAgentTrainer:
    """Trains an RL Agent using stable-baselines3 on a SUMO network."""
    
    def __init__(self, use_gui=False, custom_reward=True):
        self.use_gui = use_gui
        self.custom_reward = custom_reward
        self.model = None
        self.env = None

    def create_env(self):
        """Create the sumo-rl Gymnasium environment."""
        reward_fn = emission_decoupling_reward if self.custom_reward else "diff-waiting-time"
        
        env = SumoEnvironment(
            net_file=str(config.SUMO_NET_FILE),
            route_file=str(config.SUMO_ROUTE_FILE),
            out_csv_name=str(config.RESULTS_DIR / "rl_logs"),
            use_gui=self.use_gui,
            num_seconds=config.SUMO_SIM_STEPS,
            delta_time=config.RL_CONFIG["delta_time"],
            min_green=config.RL_CONFIG["min_green"],
            max_green=config.RL_CONFIG["max_green"],
            reward_fn=reward_fn,
        )
        
        # Wrap for stable-baselines3
        self.env = DummyVecEnv([lambda: env])
        return self.env

    def train(self, total_timesteps=None):
        """Train the RL model."""
        if self.env is None:
            self.create_env()
            
        timesteps = total_timesteps or config.RL_CONFIG["total_timesteps"]
        algo = config.RL_CONFIG["algorithm"].upper()
        
        print(f"Training {algo} Agent for {timesteps} timesteps...")
        
        if algo == "PPO":
            self.model = PPO(
                "MlpPolicy", 
                self.env, 
                verbose=1,
                learning_rate=config.RL_CONFIG["learning_rate"],
                n_steps=config.RL_CONFIG["n_steps"],
                batch_size=config.RL_CONFIG["batch_size"],
            )
        else:
            self.model = DQN(
                "MlpPolicy", 
                self.env, 
                verbose=1,
                learning_rate=config.RL_CONFIG["learning_rate"],
            )
            
        self.model.learn(total_timesteps=timesteps)
        print("Training complete!")
        return self.model

    def save(self, filepath=None):
        """Save trained model."""
        if self.model:
            path = filepath or (config.MODELS_DIR / "rl_agent_model")
            self.model.save(str(path))
            print(f"Model saved to {path}")

    def load(self, filepath=None):
        """Load trained model."""
        algo = config.RL_CONFIG["algorithm"].upper()
        path = filepath or (config.MODELS_DIR / "rl_agent_model")
        
        if algo == "PPO":
            self.model = PPO.load(str(path))
        else:
            self.model = DQN.load(str(path))
            
        print(f"Model loaded from {path}")
        return self.model


if __name__ == "__main__":
    trainer = RLAgentTrainer(use_gui=False)
    trainer.train(total_timesteps=1000) # Quick test
    trainer.save()
