import xml.etree.ElementTree as ET
import os
import pandas as pd

# Configuration
SCENARIOS_DIR = "scenarios"
OUTPUT_REPORT = "simulation_report.md"
OUTPUT_CSV = "simulation_results.csv"

# Constants
GRID_COST_PER_KWH = 0.20  # EUR per kWh
ICE_TOLL_BASE = 1.0       # Multiplier for toll revenue (simplified)

def parse_tripinfo(tripinfo_file):
    """
    Parses SUMO tripinfo output XML to calculate total CO2 and Energy.
    """
    total_co2_mg = 0.0
    total_energy_wh = 0.0
    ice_count = 0
    ev_count = 0
    
    try:
        context = ET.iterparse(tripinfo_file, events=("end",))
        for event, elem in context:
            if elem.tag == "tripinfo":
                # Extract emissions from the nested <emissions> child element
                vtype = elem.get("vType", "")
                emissions_elem = elem.find("emissions")
                
                if emissions_elem is not None:
                    co2 = float(emissions_elem.get("CO2_abs", 0))
                    electricity = float(emissions_elem.get("electricity_abs", 0))
                    
                    if co2 > 0:
                        total_co2_mg += co2
                        ice_count += 1
                    elif electricity > 0:
                        total_energy_wh += electricity
                        ev_count += 1
                    else:
                        # Fallback: check vType if emissions are zero
                        if "ICE" in vtype:
                            ice_count += 1
                        elif "EV" in vtype:
                            ev_count += 1
                else:
                    # No emissions element - fallback to vType
                    if "ICE" in vtype:
                        ice_count += 1
                    elif "EV" in vtype:
                        ev_count += 1
                
                elem.clear()
    except Exception as e:
        print(f"Error parsing {tripinfo_file}: {e}")
        return 0, 0, 0, 0

    return total_co2_mg, total_energy_wh, ice_count, ev_count

def analyze_scenarios():
    results = []
    
    # Find all tripinfo files
    for filename in os.listdir(SCENARIOS_DIR):
        if filename.startswith("tripinfo_toll_") and filename.endswith(".xml"):
            # Extract toll price from filename: "tripinfo_toll_0_5.xml" -> 0.5
            try:
                # Get the part after "tripinfo_toll_" and before ".xml"
                toll_part = filename.replace("tripinfo_toll_", "").replace(".xml", "")
                # Replace underscore back to decimal: "0_5" -> "0.5"
                toll_price = float(toll_part.replace("_", "."))
            except ValueError:
                continue
                
            print(f"Analyzing scenario: Toll {toll_price}")
            file_path = os.path.join(SCENARIOS_DIR, filename)
            
            # Parse Tripinfo
            total_co2_mg, total_energy_wh, ice_count, ev_count = parse_tripinfo(file_path)
            
            # Calculate KPIs
            total_co2_kg = total_co2_mg / 1_000_000
            total_energy_kwh = total_energy_wh / 1000
            grid_cost = total_energy_kwh * GRID_COST_PER_KWH
            
            revenue = ice_count * toll_price
            total_vehicles = ice_count + ev_count
            ev_share = ev_count / total_vehicles if total_vehicles > 0 else 0
            
            results.append({
                "Toll Price (EUR)": toll_price,
                "EV Share": ev_share,
                "Total CO2 (kg)": total_co2_kg,
                "Grid Cost (EUR)": grid_cost,
                "Toll Revenue (EUR)": revenue,
                "Total Vehicles": total_vehicles
            })

    # Create DataFrame
    df = pd.DataFrame(results)
    if not df.empty:
        df = df.sort_values("Toll Price (EUR)")
        
        # Save CSV
        df.to_csv(OUTPUT_CSV, index=False)
        print(f"Results saved to {OUTPUT_CSV}")
        
        # Generate Markdown Report
        markdown = f"# Simulation Results\n\n"
        markdown += df.to_markdown(index=False)
        
        with open(OUTPUT_REPORT, "w") as f:
            f.write(markdown)
        print(f"Report saved to {OUTPUT_REPORT}")
    else:
        print("No results found.")

if __name__ == "__main__":
    analyze_scenarios()
