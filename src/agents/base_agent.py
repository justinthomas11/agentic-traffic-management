"""
Base Agent Interface
Defines the standard interface that all traffic signal agents must implement.
"""

from abc import ABC, abstractmethod


class TrafficAgent(ABC):
    """Abstract base class for all traffic signal agents."""
    
    def __init__(self, tls_id):
        """
        Initialize the agent.
        
        Args:
            tls_id (str): The ID of the traffic light system in SUMO.
        """
        self.tls_id = tls_id
        
    @abstractmethod
    def act(self, observation):
        """
        Choose an action based on the current observation.
        
        Args:
            observation: The current state of the intersection.
            
        Returns:
            int: The index of the chosen signal phase.
        """
        pass
        
    def step(self):
        """
        Called every simulation step if the agent needs to track internal state.
        Default implementation does nothing.
        """
        pass
