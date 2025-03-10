# Ignition Delay Calculation Using Cantera

This repository contains a Python-based tool for calculating ignition delays of fuel-oxidizer mixtures in a constant volume reactor using Cantera. The tool is based on the batch reactor example from [Cantera](https://cantera.org/) and provides a flexible framework for analyzing ignition characteristics of various fuel mixtures.

## Features

- Calculate ignition delays for different fuel-oxidizer mixtures
- Support for various chemical mechanisms (e.g., GRI-Mech 3.0, custom mechanisms)
- Temperature and pressure sweep capabilities
- Visualization of species evolution and ignition delay trends
- Engine cycle simulation with piston motion
- Easy-to-use Python interface

## Installation

1. Clone this repository:
```bash
git clone https://github.com/yourusername/ignition_delay.git
cd ignition_delay
```

2. Create and activate the conda environment:
```bash
conda env create -f environment.yaml
conda activate ct-env
```

## Usage

### Basic Example

```python
from ignition_del import reactor

# Initialize a constant volume reactor with default settings
cv_react = reactor(mechanism='gri30.yaml',  # Chemical mechanism
                  fuel_inp='C8H18',         # Fuel
                  oxidizer_inp={"O2": 1.0, "N2": 3.76},  # Oxidizer composition
                  phi_inp=0.6,              # Equivalence ratio
                  temp=1000,                # Initial temperature (K)
                  press=1.01325e5 * 20)    # Initial pressure (Pa)

# Initialize the batch reactor
cv_react.init_batch()

# Calculate ignition delay using OH radical as reference species
tau, compute_time = cv_react.ignition_delay("oh")

# Plot species evolution
cv_react.print_species_evolution("oh")
```

### Temperature Sweep Example

```python
# Create temperature sweep
T = np.hstack((np.arange(2000, 900, -100), np.arange(975, 475, -25)))
tau = np.zeros([len(T), 1])

for i, temp in enumerate(T):
    cv_react.set_temp_press(temp, press)
    tau[i, 0], _ = cv_react.ignition_delay("oh")

# Plot ignition delay vs. temperature
plt.figure()
plt.semilogy(1000/T, tau, 'o-')
plt.xlabel('1000/T (K⁻¹)')
plt.ylabel('Ignition Delay (s)')
plt.grid(True)
plt.show()
```

### Engine Cycle Simulation Example
```
# The simulation will generate a plot showing:
# - Pressure vs. time during the complete cycle
# - Temperature vs. time during the complete cycle
# - Volume vs. time during the complete cycle
# - Ignition point marked on the plots
# - Example filename: 'engine_cycle_bdc_to_bdc.png'
```

![Engine Cycle Simulation](Screenshot from 2025-03-09 22-48-08.png)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- [Cantera](https://cantera.org/) for providing the chemical kinetics framework
- The combustion community for developing and maintaining chemical mechanisms
