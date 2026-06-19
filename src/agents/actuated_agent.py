"""
Actuated Agent
A baseline agent that extends green time if vehicles are present, 
mimicking standard loop-detector actuated signals.
"""

from .base_agent import TrafficAgent

class ActuatedAgent(TrafficAgent):
    """
    Acts like a standard actuated signal. In SUMO, setting type='actuated'
    in the network generation handles this natively. This python wrapper
    simply allows us to use it within our experiment framework.
    """
    
    def __init__(self, tls_id):
        super().__init__(tls_id)
        
    def act(self, observation):
        """
        For a true actuated signal in SUMO, the logic is internal to SUMO.
        When using sumo-rl, we don't manually control the actuated signal
        step-by-step through Python unless we implement the gap-out logic here.
        
        To keep it simple, returning -1 or letting SUMO handle it natively 
        is the preferred way, but this class serves as a placeholder for 
        experiment tracking.
        """
        pass
