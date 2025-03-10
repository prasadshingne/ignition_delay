import cantera as ct
import numpy as np
import matplotlib.pyplot as plt

# ---------------------------
# Engine and cycle parameters
# ---------------------------
compression_ratio = 8.0         # V_max/V_min
V_min = 0.001                   # Minimum volume at TDC (m^3)
V_max = compression_ratio * V_min  # Maximum volume at BDC (m^3)
rpm = 3000.0                    # Engine speed (rev/min)
omega = 2 * np.pi * rpm / 60.0  # Angular speed (rad/s)
T_cycle = 2 * np.pi / omega     # Duration of one cycle (BDC -> TDC -> BDC)

def piston_velocity(t):
    """
    Instantaneous rate of change of the volume (dV/dt) for a cycle starting at BDC.
    The volume variation is given by:
      V(t) = V_min + 0.5*(V_max-V_min)*(1 + cos(omega*t))
    Hence,
      dV/dt = -0.5*(V_max-V_min)*omega*sin(omega*t)
    """
    return -0.5 * (V_max - V_min) * omega * np.sin(omega * t)

# ---------------------------
# Set up the gas and reactor
# ---------------------------
gas = ct.Solution('gri30.xml')
gas.TPX = 670, ct.one_atm, 'CH4:1, O2:2, N2:7.52'
# Start at BDC so that the initial volume is V_max (1 atm)
reactor = ct.IdealGasReactor(gas, volume=V_max)

# ---------------------------
# Set up the moving wall with a reservoir
# ---------------------------
# Create a reservoir with the same underlying gas state as the reactor.
reservoir = ct.Reservoir(ct.Solution('gri30.xml'))
reservoir.thermo.TPX = 300.0, ct.one_atm, 'CH4:1, O2:2, N2:7.52'

wall = ct.Wall(reactor, reservoir)
wall.area = 0.01  # Cross-sectional area of the piston in m^2
wall.heat_transfer_coeff = 0.0  # Adiabatic wall

sim = ct.ReactorNet([reactor])

# ---------------------------
# Time integration (simulate one full cycle: BDC -> TDC -> BDC)
# ---------------------------
t_end = T_cycle
dt = T_cycle / 1000.0
t = 0.0

time_data = []
pressure_data = []
temperature_data = []
volume_data = []

while t < t_end:
    # Calculate piston velocity (m/s) from dV/dt and wall area
    current_velocity = piston_velocity(t) / wall.area
    wall.set_velocity(current_velocity)
    
    sim.advance(t)
    time_data.append(t)
    pressure_data.append(reactor.thermo.P)
    temperature_data.append(reactor.thermo.T)
    volume_data.append(reactor.volume)
    
    t += dt

plt.figure(figsize=(10, 8))

plt.subplot(3, 1, 1)
plt.plot(time_data, pressure_data)
plt.ylabel('Pressure (Pa)')
plt.xlabel('Time (s)')
plt.title('Engine Cycle Simulation (BDC to BDC)')

plt.subplot(3, 1, 2)
plt.plot(time_data, temperature_data)
plt.ylabel('Temperature (K)')
plt.xlabel('Time (s)')

plt.subplot(3, 1, 3)
plt.plot(time_data, volume_data)
plt.ylabel('Volume (m^3)')
plt.xlabel('Time (s)')

plt.tight_layout()
plt.show()
