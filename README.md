# EV Adoption & Toll Simulation (VCI Network)

This project simulates the impact of toll pricing on Electric Vehicle (EV) adoption and CO2 emissions using [SUMO](https://eclipse.dev/sumo/) traffic simulator. It focuses on the VCI (Via de Cintura Interna) network.

## 📋 Prerequisites

### 1. SUMO Traffic Simulator
You must have SUMO installed and the `bin` folder added to your system `PATH`.
- **Download**: [Eclipse SUMO](https://eclipse.dev/sumo/download/)
- **Version**: Tested with 1.25.0

### 2. Python Environment
Python 3.x is required. Install the necessary dependencies:

```bash
pip install pandas matplotlib numpy tabulate
```

## 🚀 How to Run

### 1. Run Simulations
The main script generates scenarios for different toll prices (€0 to €5) and runs the SUMO simulations automatically.

```bash
python run_scenarios.py
```
*   Generates configuration files in `scenarios/`
*   Runs SUMO for each toll increment (0, 0.5, 1.0, ... 5.0)
*   Outputs trip data to `scenarios/tripinfo_toll_*.xml`

### 2. Analyze Results
After simulations complete, parse the results to calculate EV share, CO2 emissions, and revenue.

```bash
python analyze_results.py
```
*   Generates a report: `simulation_report.md`
*   Saves data to: `simulation_results.csv`

### 3. Sensitivity Analysis (Optional)
Test how sensitive the model is to changes in parameters (sigmoid midpoint, strictness, baseline).

```bash
python sensitivity_test.py
```
*   Generates analysis plots in `sensitivity_results/`

## 📂 Project Structure

*   **`run_scenarios.py`**: Orchestrator script. Runs `generate_scenario.py` then executes SUMO.
*   **`generate_scenario.py`**: Creates SUMO config and route files. Implements the **Sigmoid Function** for EV adoption probability based on toll price.
*   **`analyze_results.py`**: Processes simulation outputs to compute KPIs (CO2, Grid Cost, Revenue).
*   **`create_vci_demand.py`**: (Setup) Generates the initial random traffic demand (`trips_vci_generated.xml`) compatible with the VCI network.
*   **`sensitivity_test.py`**: Performs one-at-a-time sensitivity analysis on model parameters.
*   **`vci.net.xml`**: The SUMO road network file.
*   **`scenarios/`**: Contains generated config files, routes, and simulation output (`tripinfo`).

## ⚙️ Model Details

**EV Adoption Model:**
The probability of a vehicle being an EV is determined by a Sigmoid function of the toll price:
$$ P(EV) = \text{Baseline} + (\text{Max} - \text{Baseline}) \times \frac{1}{1 + e^{-k(Cost - \text{Midpoint})}} $$

*   **Baseline**: 15% (at €0)
*   **Saturation (Max)**: 90%
*   **Midpoint**: €2.5
