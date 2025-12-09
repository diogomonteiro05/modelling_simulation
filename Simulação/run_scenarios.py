import subprocess
import os
import sys

# Configuration
SCENARIOS_DIR = "scenarios"
GENERATE_SCRIPT = "generate_scenario.py"
TOLL_PRICES = [0, 0.5, 1.0, 1.5, 2, 2.5, 3.0]

# Set the path to your SUMO executable here if it's not in your PATH
# Example: r"C:\Program Files (x86)\Eclipse\Sumo\bin\sumo.exe"
SUMO_BIN = r"C:\Program Files (x86)\Eclipse\Sumo\bin\sumo.exe" 

def run_command(command):
    print(f"Running: {command}")
    try:
        subprocess.run(command, check=True, shell=True)
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {e}")
        sys.exit(1)

def main():
    for toll in TOLL_PRICES:
        print(f"\n--- Processing Toll Price: {toll} EUR ---")
        
        # 1. Generate Scenario
        cmd_generate = f"python \"{GENERATE_SCRIPT}\" --toll {toll}"
        run_command(cmd_generate)
        
        # 2. Run Simulation
        # Format toll to handle decimals: 0.5 -> "0_5", 1.0 -> "1_0", 2 -> "2_0"
        scenario_name = f"toll_{str(toll).replace('.', '_')}"
        config_file = os.path.join(SCENARIOS_DIR, f"config_{scenario_name}.sumo.cfg")
        
        # Check if config exists
        if not os.path.exists(config_file):
            print(f"Config file not found: {config_file}")
            continue
            
        # Run SUMO
        # Using 'sumo' command. Ensure SUMO_HOME/bin is in PATH.
        # We redirect stderr to stdout to see errors.
        cmd_sumo = f"\"{SUMO_BIN}\" -c \"{config_file}\" --xml-validation never"
        run_command(cmd_sumo)
        
    print("\nAll scenarios completed.")

if __name__ == "__main__":
    main()
