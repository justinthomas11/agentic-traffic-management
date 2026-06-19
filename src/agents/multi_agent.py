"""
Multi-Agent RL Coordinator
Handles multiple sumo-rl agents on the grid network.
"""

import os
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
import config

try:
    from sumo_rl import SumoEnvironment
    # Multi-agent environments often use pettingzoo, but for this project 
    # we'll stick to a simplified independent PPO approach for now to avoid
    # massive dependency overhead.
except ImportError:
    print("Warning: sumo-rl not installed.")


class MultiAgentCoordinator:
    """
    Coordinates training and evaluation for a multi-agent grid network.
    
    In sumo-rl, a single-agent environment controls one intersection,
    while a multi-agent environment controls multiple. If we pass a network
    with multiple traffic lights to SumoEnvironment without specifying single-agent,
    it defaults to PettingZoo multi-agent API.
    """
    
    def __init__(self, use_gui=False):
        self.use_gui = use_gui
        
    def setup_env(self):
        """Setup multi-agent environment."""
        from src.agents.reward_functions import emission_decoupling_reward
        
        env = SumoEnvironment(
            net_file=str(config.SUMO_NET_FILE),
            route_file=str(config.SUMO_ROUTE_FILE),
            out_csv_name=str(config.RESULTS_DIR / "multi_agent_logs"),
            use_gui=self.use_gui,
            num_seconds=config.SUMO_SIM_STEPS,
            delta_time=config.RL_CONFIG["delta_time"],
            min_green=config.RL_CONFIG["min_green"],
            max_green=config.RL_CONFIG["max_green"],
            reward_fn=emission_decoupling_reward,
            single_agent=False # Explicitly set to multi-agent
        )
        return env

    def train_independent_ppo(self):
        """
        Train independent PPO agents for each intersection.
        Note: This is a placeholder for standard multi-agent PettingZoo logic.
        For full implementation, one would use SuperSuit + stable-baselines3.
        """
        print("Multi-agent training requires PettingZoo + SuperSuit.")
        print("For this demo, we recommend using the single-agent RL approach")
        print("which optimizes the most central intersection.")
        pass

if __name__ == "__main__":
    mac = MultiAgentCoordinator(use_gui=False)
    # env = mac.setup_env()
