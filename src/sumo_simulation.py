"""
SUMO Simulation Wrapper
Provides an easy-to-use Python interface to run SUMO simulations via TraCI
and collect performance metrics (delay, emissions).
"""

import os
import sys
from pathlib import Path
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import config

try:
    import traci
    import sumolib
except ImportError:
    print("Warning: SUMO tools not found. Simulation will not run.")


class SUMOSimulation:
    """Wrapper class for running SUMO simulations via TraCI."""
    
    def __init__(self, use_gui=False, config_file=None):
        self.use_gui = use_gui
        self.config_file = config_file or config.SUMO_CFG_FILE
        self.step_data = []
        
        if not os.environ.get("SUMO_HOME"):
            if os.path.exists(config.SUMO_HOME):
                os.environ["SUMO_HOME"] = config.SUMO_HOME
            else:
                raise EnvironmentError("SUMO_HOME not set and default path invalid.")

    def start(self):
        """Start the TraCI connection."""
        sumo_binary = sumolib.checkBinary('sumo-gui') if self.use_gui else sumolib.checkBinary('sumo')
        
        cmd = [
            sumo_binary,
            "-c", str(self.config_file),
            "--waiting-time-memory", "10000",
        ]
        
        traci.start(cmd)
        self.step_data = []
        print(f"Started SUMO simulation: {'GUI' if self.use_gui else 'Headless'}")

    def run(self, max_steps=None):
        """Run the simulation to completion or max_steps."""
        max_steps = max_steps or config.SUMO_SIM_STEPS
        
        step = 0
        while step < max_steps and traci.simulation.getMinExpectedNumber() > 0:
            traci.simulationStep()
            self._collect_metrics(step)
            step += 1
            
            if step % 500 == 0:
                print(f"Simulation step {step}/{max_steps}")
                
        self.close()
        return self.get_results_df()

    def _collect_metrics(self, step):
        """Collect network-wide metrics for the current step."""
        # Vehicles currently in the network
        veh_ids = traci.vehicle.getIDList()
        
        if not veh_ids:
            return
            
        total_waiting_time = sum(traci.vehicle.getWaitingTime(v) for v in veh_ids)
        total_co2 = sum(traci.vehicle.getCO2Emission(v) for v in veh_ids)
        avg_speed = sum(traci.vehicle.getSpeed(v) for v in veh_ids) / len(veh_ids) if veh_ids else 0
        
        self.step_data.append({
            "step": step,
            "vehicle_count": len(veh_ids),
            "avg_speed_ms": avg_speed,
            "avg_speed_kmh": avg_speed * 3.6,
            "total_waiting_time_s": total_waiting_time,
            "total_co2_mg": total_co2,
            "total_co2_g": total_co2 / 1000.0
        })

    def get_results_df(self):
        """Return collected metrics as a pandas DataFrame."""
        if not self.step_data:
            return pd.DataFrame()
        return pd.DataFrame(self.step_data)

    def close(self):
        """Close TraCI connection."""
        try:
            traci.close()
            print("Closed SUMO simulation.")
        except traci.exceptions.FatalTraCIError:
            pass

    def run_quick_test(self):
        """Run a short simulation test without GUI."""
        print("Running quick SUMO test...")
        self.start()
        df = self.run(max_steps=100)
        
        if not df.empty:
            print("\nTest simulation complete. Summary:")
            print(df.mean())
            return True
        else:
            print("\nTest simulation yielded no data.")
            return False


if __name__ == "__main__":
    sim = SUMOSimulation()
    sim.run_quick_test()
