import subprocess
import os
import sys
import platform

# Configuration
SCENARIOS_DIR = "scenarios"
GENERATE_SCRIPT = "generate_scenario.py"
TOLL_PRICES = [0, 0.5, 1.0, 1.5, 2, 2.5, 3.0, 3.5, 4, 4.5, 5]

# Resolve SUMO binary in a cross-platform way.
# Priority:
#   1. Environment variable SUMO_BIN (user override)
#   2. On Windows: default installed path
#   3. Elsewhere (e.g. WSL/Linux): assume "sumo" is in PATH
SUMO_BIN = os.environ.get("SUMO_BIN")
if not SUMO_BIN:
    if platform.system() == "Windows":
        SUMO_BIN = r"C:\Program Files (x86)\Eclipse\Sumo\bin\sumo.exe"
    else:
        SUMO_BIN = "sumo"

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
        # Format toll to handle decimals consistently with generate_scenario.py:
        # 0.0 -> "0_0", 0.5 -> "0_5", 1.0 -> "1_0", 2.0 -> "2_0"
        toll_str = f"{toll:.1f}"
        scenario_name = f"toll_{toll_str.replace('.', '_')}"
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
