"""
Custom Reward Functions for RL Agents
"""

import numpy as np


def emission_decoupling_reward(traffic_signal):
    """
    Custom reward function that penalizes waiting time AND emissions,
    but provides a bonus if decoupling is occurring (emissions dropping 
    faster than congestion).
    
    Args:
        traffic_signal (sumo_rl.environment.traffic_signal.TrafficSignal): 
            The traffic signal object.
            
    Returns:
        float: The calculated reward.
    """
    # 1. Congestion penalty (waiting time)
    wait_time = traffic_signal.get_total_queued()
    
    # 2. Emission penalty (CO2)
    # SUMO-RL doesn't expose emissions directly by default, 
    # we estimate it based on queue and speed, or pull from traci if accessible.
    try:
        import traci
        # Get vehicles on incoming lanes
        vehicles = []
        for lane in traffic_signal.lanes:
            vehicles.extend(traci.lane.getLastStepVehicleIDs(lane))
            
        co2_emission = sum(traci.vehicle.getCO2Emission(v) for v in vehicles)
    except:
        # Fallback if traci not directly accessible or fails
        co2_emission = wait_time * 1.5  # Rough heuristic: queued vehicles emit idling CO2
        
    # Scale to reasonable ranges
    scaled_wait = wait_time * 0.5
    scaled_co2 = co2_emission / 1000.0  # mg to g
    
    # Base penalty
    reward = -(scaled_wait + scaled_co2)
    
    # Decoupling bonus: If wait is high but emissions are low, 
    # or if we are improving flow efficiently.
    # (Simplified proxy for RL state step)
    if scaled_wait > 0 and scaled_co2 / scaled_wait < 0.8:
        reward += 5.0  # Decoupling bonus
        
    return reward


def throughput_reward(traffic_signal):
    """Reward based on number of vehicles passing through."""
    # This requires tracking previous step vehicles, which SUMO-RL does 
    # internally or via traci.edge.getLastStepVehicleNumber
    return -traffic_signal.get_total_queued()
