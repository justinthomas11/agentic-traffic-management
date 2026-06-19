"""
Agentic Traffic Management — SUMO Network Generation
Handles automated creation of grid networks, routes, and configuration files
for SUMO simulations using netgenerate and sumolib.
"""

import os
import subprocess
from pathlib import Path
import xml.etree.ElementTree as ET
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import config


def generate_grid_network(grid_size=None, block_length=None):
    """
    Generate a square grid network using SUMO's netgenerate.
    """
    grid_size = grid_size or config.GRID_SIZE
    block_length = (block_length or config.BLOCK_LENGTH_KM) * 1000  # km to meters
    
    output_file = config.SUMO_NET_FILE
    
    cmd = [
        "netgenerate",
        "--grid",
        "--grid.number", str(grid_size),
        "--grid.length", str(block_length),
        "--default.lanenumber", "2",
        "--default.speed", str(config.GRID_SPEED_LIMIT / 3.6), # km/h to m/s
        "--tls.guess", "true",  # Make intersections signalized
        "--tls.default-type", "actuated", # Use actuated as baseline
        "--output-file", str(output_file)
    ]
    
    print(f"Generating SUMO grid network: {grid_size}x{grid_size}")
    print(f"Command: {' '.join(cmd)}")
    
    try:
        subprocess.run(cmd, check=True, capture_output=True, text=True)
        print(f"Successfully generated network: {output_file.name}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error generating network: {e.stderr}")
        return False
    except FileNotFoundError:
        print("Error: 'netgenerate' command not found. Is SUMO_HOME/bin in your PATH?")
        return False


def generate_routes():
    """
    Generate random trips for the grid network using randomTrips.py
    """
    import sumolib
    random_trips_script = os.path.join(config.SUMO_HOME, "tools", "randomTrips.py")
    
    if not os.path.exists(random_trips_script):
        print(f"Error: Could not find randomTrips.py at {random_trips_script}")
        return False
        
    cmd = [
        sys.executable, random_trips_script,
        "-n", str(config.SUMO_NET_FILE),
        "-r", str(config.SUMO_ROUTE_FILE),
        "-e", str(config.SUMO_SIM_STEPS), # End time
        "-p", "2.0", # Generate a vehicle every 2 seconds (high demand)
        "--fringe-factor", "10", # Prefer edge-to-edge trips
    ]
    
    print(f"Generating vehicle routes...")
    try:
        subprocess.run(cmd, check=True, capture_output=True, text=True)
        print(f"Successfully generated routes: {config.SUMO_ROUTE_FILE.name}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error generating routes: {e.stderr}")
        return False


def generate_detectors():
    """Create additional file for edge data collection (emissions, waiting times)."""
    root = ET.Element("additional")
    
    # Add an edgeData detector to aggregate metrics over the whole simulation
    edge_data = ET.SubElement(root, "edgeData")
    edge_data.set("id", "full_sim_data")
    edge_data.set("file", str(config.RESULTS_DIR / "edge_data.xml"))
    edge_data.set("freq", str(config.SUMO_SIM_STEPS))
    edge_data.set("excludeEmpty", "true")
    
    tree = ET.ElementTree(root)
    tree.write(config.SUMO_ADD_FILE, encoding="utf-8", xml_declaration=True)
    print(f"Successfully generated additional file: {config.SUMO_ADD_FILE.name}")
    return True


def generate_sumo_config():
    """
    Create the .sumocfg file tying the network, routes, and additional files together.
    """
    root = ET.Element("configuration")
    
    input_elem = ET.SubElement(root, "input")
    ET.SubElement(input_elem, "net-file", value=config.SUMO_NET_FILE.name)
    ET.SubElement(input_elem, "route-files", value=config.SUMO_ROUTE_FILE.name)
    ET.SubElement(input_elem, "additional-files", value=config.SUMO_ADD_FILE.name)
    
    time_elem = ET.SubElement(root, "time")
    ET.SubElement(time_elem, "begin", value="0")
    ET.SubElement(time_elem, "end", value=str(config.SUMO_SIM_STEPS))
    ET.SubElement(time_elem, "step-length", value=str(config.SUMO_STEP_LENGTH))
    
    report_elem = ET.SubElement(root, "report")
    ET.SubElement(report_elem, "verbose", value="true")
    ET.SubElement(report_elem, "no-step-log", value="true")
    
    # Enable emission models
    emissions_elem = ET.SubElement(root, "emissions")
    ET.SubElement(emissions_elem, "device.emissions.probability", value="1.0")
    
    tree = ET.ElementTree(root)
    tree.write(config.SUMO_CFG_FILE, encoding="utf-8", xml_declaration=True)
    print(f"Successfully generated SUMO config: {config.SUMO_CFG_FILE.name}")
    return True


def build_full_scenario():
    """Run all generation steps to create a ready-to-run SUMO scenario."""
    print("=" * 60)
    print("Building SUMO Grid Scenario")
    print("=" * 60)
    
    config.SUMO_CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    
    success = True
    success &= generate_grid_network()
    
    if success:
        success &= generate_routes()
        success &= generate_detectors()
        success &= generate_sumo_config()
        
    if success:
        print("\n✅ Scenario build complete!")
    else:
        print("\n❌ Scenario build failed.")
        
    return success


if __name__ == "__main__":
    build_full_scenario()
