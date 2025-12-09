# SUMO Traffic Simulation - EV Adoption & Toll Impact Study

## Project Overview
This codebase simulates traffic scenarios using SUMO (Simulation of Urban MObility) to analyze the impact of toll pricing on Electric Vehicle (EV) adoption and environmental outcomes. The simulation models a VCI (Viaduto Cidade de Ibadan) network with configurable toll policies.

## Core Architecture

### Three-Stage Workflow
1. **Scenario Generation** (`generate_scenario.py`) - Creates simulation scenarios with varying toll prices and EV adoption rates
2. **Simulation Execution** (`run_scenarios.py`) - Runs SUMO simulations for each scenario
3. **Results Analysis** (`analyze_results.py`) - Processes tripinfo outputs to calculate KPIs (CO2, energy costs, revenue)

### Key Data Flow
```
vci.net.xml (network) + routes_vci_generated.xml (base routes)
  → generate_scenario.py --toll <price>
  → scenarios/routes_toll_X_Y.xml + config_toll_X_Y.sumo.cfg
  → SUMO simulation
  → scenarios/tripinfo_toll_X_Y.xml
  → analyze_results.py
  → simulation_results.csv + simulation_report.md
```

## Critical Implementation Details

### Toll-to-EV Adoption Model
EV adoption follows a **sigmoid function** (in `generate_scenario.py`):
- **0% EV at €0 toll** (baseline with no incentive)
- **50% adoption at €1.5 toll** (midpoint)
- **100% saturation** at high tolls
- Formula: `share = 1.0 / (1 + exp(-0.5 * (toll - 1.5)))`
- EVs get toll exemption (free passage), ICE vehicles pay full toll

### Vehicle Type Assignment
- `generate_scenario.py` randomly assigns each vehicle in `routes_vci_generated.xml` to either:
  - **ICE**: `emissionClass="HBEFA3/PC_G_EU4"`, red color, produces CO2
  - **EV**: `emissionClass="Energy/unknown"`, green color, zero tailpipe emissions
- Requires emission device: `<param key="device.emissions.probability" value="1.0"/>`

### Filename Convention
Decimal toll prices use **underscore notation**: `0.5` → `toll_0_5`, `1.0` → `toll_1_0`
- Routes: `routes_toll_X_Y.xml`
- Configs: `config_toll_X_Y.sumo.cfg`
- Outputs: `tripinfo_toll_X_Y.xml`

## Developer Workflows

### Running Full Experiment
```powershell
# 1. Generate demand (if needed - creates trips_vci_generated.xml)
python create_vci_demand.py

# 2. Run all scenarios (0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0 EUR)
python run_scenarios.py

# 3. Analyze results
python analyze_results.py
```

### SUMO Configuration
- **SUMO binary path**: `C:\Program Files (x86)\Eclipse\Sumo\bin\sumo.exe` (hardcoded in `run_scenarios.py`)
- **Simulation time**: 32400-39600 seconds (9:00 AM - 11:00 AM, 2-hour rush period)
- **Network file**: `vci.net.xml` (VCI network topology)
- All scenario configs disable XML validation: `--xml-validation never`

### Output Files
- `scenarios/tripinfo_toll_X_Y.xml` - Per-vehicle trip data with CO2/energy attributes
- `simulation_results.csv` - Aggregated KPIs across all toll scenarios
- `simulation_report.md` - Markdown table of results (if generated)

## Key Constants & KPIs

### Economic Parameters
- `GRID_COST_PER_KWH = 0.20` EUR (electricity cost for EVs)
- Toll revenue = `ice_count * toll_price` (only ICE vehicles pay)

### Emissions Parsing
- `analyze_results.py` extracts from tripinfo: `CO2_abs` (mg), `electricity_abs` (Wh)
- Converts: mg → kg (÷1,000,000), Wh → kWh (÷1,000)
- Vehicle type detection: checks `vType` attribute or emission presence

## Common Pitfalls

1. **Large XML Files**: `routes_vci_generated.xml` is 54MB - use ElementTree's `ET.parse()` (loads into memory, acceptable for this size)
2. **Edge Connectivity**: `create_vci_demand.py` uses predefined main edges (e.g., `'1135405', '1302641'`) for 70% of trips to avoid routing failures
3. **Absolute Paths**: All file paths are hardcoded with full Windows paths - update if moving workspace
4. **Missing Dependencies**: Requires `pandas`, `matplotlib` (for analysis), and SUMO installation

## Project-Specific Conventions

- **No dependency management**: No `requirements.txt` - manually install `pandas` and `matplotlib`
- **Inline configuration**: Constants defined at top of each script (no config files)
- **Error handling**: Minimal - scripts exit on failure via `subprocess.run(check=True)`
- **XML processing**: Standard library `xml.etree.ElementTree` throughout, no external parsers
