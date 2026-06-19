"""
Fixed Timing Agent
A simple baseline agent that cycles through signal phases on a fixed schedule.
"""

from .base_agent import TrafficAgent

class FixedTimingAgent(TrafficAgent):
    """
    Cycles through phases based on a fixed duration schedule.
    In SUMO, this is usually handled natively by the default logic,
    but this agent provides a way to explicitly control it for comparison.
    """
    
    def __init__(self, tls_id, phase_durations=None):
        """
        Args:
            tls_id: Traffic light ID
            phase_durations: List of integers representing durations for each phase.
                             If None, defaults to [40, 5, 40, 5] (Green, Yellow, Green, Yellow)
        """
        super().__init__(tls_id)
        self.phase_durations = phase_durations or [40, 5, 40, 5]
        self.num_phases = len(self.phase_durations)
        self.current_phase = 0
        self.time_in_phase = 0
        
    def act(self, observation=None):
        """
        Return the current phase if duration not met, or next phase if duration met.
        """
        if self.time_in_phase >= self.phase_durations[self.current_phase]:
            # Move to next phase
            self.current_phase = (self.current_phase + 1) % self.num_phases
            self.time_in_phase = 0
            
        return self.current_phase
        
    def step(self):
        """Increment time spent in current phase."""
        self.time_in_phase += 1
