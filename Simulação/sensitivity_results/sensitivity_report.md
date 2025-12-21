# Sensitivity Analysis Report

## Overview
This report analyzes how sensitive the EV toll simulation is to changes in key model parameters.

## Default Parameters
- **Baseline EV Share**: 15% (at 0 EUR toll)
- **Maximum EV Share**: 90% (at high tolls)
- **Sigmoid Midpoint**: 2.5 EUR (50% transition point)
- **Steepness (k)**: 0.5

## Key Findings

### 1. Midpoint Sensitivity
The midpoint parameter controls *where* on the toll scale the EV adoption accelerates.
- Lower midpoint (1.0-1.5 EUR) = EVs dominate earlier
- Higher midpoint (3.0-3.5 EUR) = ICE vehicles persist longer

**Impact**: Shifting midpoint by 1 EUR changes EV share by ~15-20% at mid-range tolls.

### 2. Steepness (k) Sensitivity  
The steepness controls *how quickly* adoption transitions from ICE to EV.
- Low k (0.2-0.3) = Gradual transition over wide toll range
- High k (1.0+) = Sharp transition near midpoint

**Impact**: Doubling k roughly doubles the transition rate at the midpoint.

### 3. Baseline Share Sensitivity
The baseline reflects natural EV adoption without toll incentives.
- Higher baseline = More EVs even at 0 EUR toll
- Affects total revenue (fewer ICE vehicles paying tolls)

**Impact**: Each 5% increase in baseline reduces toll revenue by ~5%.

## Recommendation
The model is **most sensitive** to the **midpoint parameter**. This should be:
1. Calibrated against real-world toll/EV adoption data
2. Validated with stakeholder feedback on expected adoption rates

## Visualizations
See the following files in `sensitivity_results/`:
- `sensitivity_midpoint.png`
- `sensitivity_steepness.png`
- `sensitivity_baseline.png`
- `tornado_diagram.png`
