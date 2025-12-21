import argparse
import xml.etree.ElementTree as ET
import random
import math
import os

# Configuration
ORIGINAL_ROUTES_FILE = "routes_vci_generated.xml"
NET_FILE = "vci.net.xml" # VCI network file
OUTPUT_DIR = "scenarios"

# Ensure output directory exists
os.makedirs(OUTPUT_DIR, exist_ok=True)

def calculate_ev_share(toll_price):
    """
    Calculates EV adoption share based on toll price using a sigmoid function
    with a non-zero baseline.

    Intuition (tunable assumptions):
    - Baseline EV share at 0 EUR toll: 15%
    - Midpoint (about 50% EV share): around 1.5 EUR
    - Saturation: values asymptotically approaching ~90% at high tolls
    - Steepness (k): 0.5
    """
    # Baseline EV share even with zero toll (realistic non-zero adoption)
    baseline_share = 0.15  # 15% at toll = 0

    # Sigmoid controls the *additional* adoption above the baseline
    max_share = 0.90       # saturation level for total EV share
    midpoint = 2.5
    k = 0.5

    # Standard sigmoid in [0, 1]
    sigmoid = 1 / (1 + math.exp(-k * (toll_price - midpoint)))

    # Map sigmoid output to [baseline_share, max_share]
    share = baseline_share + (max_share - baseline_share) * sigmoid

    # Safety clamp
    return max(0.0, min(1.0, share))

def generate_scenario(toll_price):
    ev_share = calculate_ev_share(toll_price)
    print(f"Generating scenario for Toll Price: {toll_price} EUR -> EV Share: {ev_share:.2%}")
    
    # Generate filenames - use underscore for decimals: 0.5 -> "toll_0_5"
    scenario_name = f"toll_{str(toll_price).replace('.', '_')}"
    output_routes_file = os.path.join(OUTPUT_DIR, f"routes_{scenario_name}.xml")
    output_config_file = os.path.join(OUTPUT_DIR, f"config_{scenario_name}.sumo.cfg")
    
    # 1. Process Routes File
    # We stream the file to avoid loading the huge XML into memory if possible, 
    # but for simplicity with ElementTree we might load it. 
    # Given the file size (54MB), standard ET parsing should be fine.
    
    try:
        tree = ET.parse(ORIGINAL_ROUTES_FILE)
        root = tree.getroot()
        
        # Add vType definitions
        # ICE Vehicle
        ice_type = ET.Element("vType")
        ice_type.set("id", "ICE")
        ice_type.set("emissionClass", "HBEFA3/PC_G_EU4") # Example ICE emission class
        ice_type.set("color", "1,0,0") # Red
        
        # Add emission device param
        ice_param = ET.SubElement(ice_type, "param")
        ice_param.set("key", "device.emissions.probability")
        ice_param.set("value", "1.0")
        
        root.insert(0, ice_type)
        
        # EV Vehicle
        ev_type = ET.Element("vType")
        ev_type.set("id", "EV")
        ev_type.set("emissionClass", "Energy/unknown") # Zero tailpipe emissions model in SUMO
        ev_type.set("color", "0,1,0") # Green
        
        # Add emission device param
        ev_param = ET.SubElement(ev_type, "param")
        ev_param.set("key", "device.emissions.probability")
        ev_param.set("value", "1.0")
        
        root.insert(1, ev_type)
        
        # Assign types to vehicles
        for vehicle in root.findall("vehicle"):
            if random.random() < ev_share:
                vehicle.set("type", "EV")
            else:
                vehicle.set("type", "ICE")
                
        tree.write(output_routes_file)
        print(f"Routes file created: {output_routes_file}")
        
    except Exception as e:
        print(f"Error processing routes file: {e}")
        return

    # 2. Generate Config File
    config_content = f"""<?xml version="1.0" encoding="iso-8859-1"?>
<configuration xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="http://sumo.sf.net/xsd/sumoConfiguration.xsd">
    <input>
        <net-file value="../vci.net.xml"/>
        <route-files value="{os.path.basename(output_routes_file)}"/>
    </input>

    <time>
        <begin value="32400"/>
        <end value="39600"/>
        <step-length value ="1"/>
    </time>
    
    <output>
        <tripinfo-output value="tripinfo_{scenario_name}.xml"/>
    </output>

    <report>
        <no-step-log value="true"/>
    </report>
</configuration>
"""
    with open(output_config_file, "w") as f:
        f.write(config_content)
    print(f"Config file created: {output_config_file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate SUMO scenario based on toll price.")
    parser.add_argument("--toll", type=float, required=True, help="Toll price in EUR")
    args = parser.parse_args()
    
    generate_scenario(args.toll)
