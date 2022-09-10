#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Aug 21 22:25:06 2022
Modificed on Tue Sept 6 2022

@author: pss
"""
#%% Import libraries
# import pandas as pd
import numpy as np
import time
import cantera as ct # import cantera https://cantera.org/
print(f"Runnning Cantera version: {ct.__version__}")
import matplotlib.pyplot as plt
#%% Configure plot properties
plt.rcParams["axes.labelsize"] = 18
plt.rcParams["xtick.labelsize"] = 10
plt.rcParams["ytick.labelsize"] = 10
plt.rcParams["figure.autolayout"] = True
plt.rcParams["figure.dpi"] = 120

#%% Class ignition_delay

class reactor:
    # Constructor
    def __init__(self, mechanism = 'gri30.yaml', 
                 fuel_inp = 'C8H18', oxidizer_inp ={"O2": 1.0, "N2": 3.76}, phi_inp = 0.6,
                 temp = 1000, press = 1.01325*1e5 * 20):
        
        self.mechanism = mechanism
        self.gas   = ct.Solution(mechanism)
        self.gas.TP = temp, press        
        self.gas.set_equivalence_ratio(phi=phi_inp, fuel=fuel_inp, oxidizer=oxidizer_inp)

    
    # set temperature and pressure
    def set_temp_press(self,temp, press):
        self.gas.TP = temp, press
        
    # set fuel, oxidizer and equivalence ratio
    def set_mixture_properties(self,phi_inp, fuel_inp, oxidizer_inp):
        self.gas.set_equivalence_ratio(phi=phi_inp, fuel=fuel_inp, oxidizer=oxidizer_inp)

    # print igniotion delay object output
    def __str__(self):
        return f"Mechanism: {self.mechanism}, Temperature: {self.gas.T} K, Pressure: {self.gas.P} Pa"
    
    
    def init_batch(self, name1="Batch Reactor"):
        self.r = ct.IdealGasReactor(contents=self.gas, name=name1)
        self.reactor_network = ct.ReactorNet([self.r])
        self.time_history = ct.SolutionArray(self.gas, extra="t")
        
    def ignition_delay(self, species):
        """
        This function computes the ignition delay from the occurence of the
        peak in species' concentration.
        """
        # Tic
        t0 = time.time()

        # This is a starting estimate. If you do not get an ignition within this time, increase it
        estimated_ignition_delay_time = 100
        t = 0

        counter = 1
        while t < estimated_ignition_delay_time:
            t = self.reactor_network.step()
            if not counter % 10:
                # We will save only every 10th value. Otherwise, this takes too long
                # Note that the species concentrations are mass fractions
                self.time_history.append(self.r.thermo.state, t=t)
            counter += 1

        # We will use the 'oh' species to compute the ignition delay
        i_ign = self.time_history(species).Y.argmax()
        self.tau = self.time_history.t[i_ign]

        # Toc
        t1 = time.time()

        # print(f"Computed Ignition Delay: {self.tau:.3e} seconds. Took {t1-t0:3.2f}s to compute")
        
        return self.tau, t1-t0
        
    
    def print_species_evolution(self, species):
        
        if hasattr(self, 'tau'):
            plt.figure()
            plt.plot(self.time_history.t, self.time_history(reference_species).Y)
            plt.xlabel("Time (s)")
            plt.ylabel("$Y_{OH}$")

            plt.xlim([0, 0.01])
            plt.arrow(
                0,
                0.008,
                self.tau,
                0,
                width=0.0001,
                head_width=0.0005,
                head_length=0.001,
                length_includes_head=True,
                color="r",
                shape="full",
            )
            plt.grid()
            plt.annotate('Ignition Delay: ' + str(round(self.tau,6)) + ' seconds', 
            xy=(0.007, 0.008), size=10, color = 'k',
            ha='center', va="center")


        
        else:
            self.ignition_delay(species)
            plt.figure()
            plt.plot(self.time_history.t, self.time_history(reference_species).Y)
            plt.xlabel("Time (s)")
            plt.ylabel("$Y_{OH}$")
           
            plt.xlim([0, 0.01])
            plt.arrow(
                0,
                0.008,
                self.tau,
                0,
                width=0.0001,
                head_width=0.0005,
                head_length=0.001,
                length_includes_head=True,
                color="r",
                shape="full",
            )
            plt.grid()
            plt.annotate('Ignition Delay: ' + str(round(self.tau,6)) + ' seconds', 
            xy=(0.007, 0.008), size=10, color = 'k',
            ha='center', va="center")
            


#%%
# Initialize a constant volume reactor
cv_react = reactor(mechanism = 'Nissan_chem.yaml')
# Initialize a batch of constant volume reactors
cv_react.init_batch(name1="Batch Reactor")
#%%
reference_species = "oh"

# tau, t_compute = cv_react.ignition_delay(reference_species)

#%%
cv_react.print_species_evolution(reference_species)

#%%
# # Make a list of all the temperatures we would like to run simulations at
# T = np.hstack((np.arange(1300, 900, -100), np.arange(975, 475, -25)))

# estimated_ignition_delay_times = np.ones_like(T, dtype=float)

# # Make time adjustments for the highest and lowest temperatures. This we do empirically
# estimated_ignition_delay_times[:6] = 6 * [0.1]
# estimated_ignition_delay_times[-4:-2] = 10
# estimated_ignition_delay_times[-2:] = 100

# # Now create a SolutionArray out of these
# ignition_delays = ct.SolutionArray(
#     gas, shape=T.shape, extra={"tau": estimated_ignition_delay_times}
# )
# ignition_delays.set_equivalence_ratio(
#     0.6, fuel="C7H16", oxidizer={"O2": 1.0, "N2": 3.76}
# )
# ignition_delays.TP = T, reactor_pressure
# #%%
# tau = np.zeros([len(T),1], dtype=float)
# for i, state in enumerate(ignition_delays):
#     # Setup the gas and reactor
#     gas.TPX = state.TPX
#     r = ct.IdealGasReactor(contents=gas, name="Batch Reactor")
#     reactor_network = ct.ReactorNet([r])

#     reference_species_history = []
#     time_history = []

#     t0 = time.time()

#     t = 0
#     while t < estimated_ignition_delay_times[i]:
#         t = reactor_network.step()
#         time_history.append(t)
#         reference_species_history.append(gas[reference_species].X[0])

#     i_ign = np.array(reference_species_history).argmax()
#     tau[i,0] = time_history[i_ign]
#     t1 = time.time()

#     # print(
#     #     f"Computed Ignition Delay: {tau:.3e} seconds for T={state.T}K. Took {t1 - t0:3.2f}s to compute"
#     # )
    
#%%
# fig = plt.figure()
# ax = fig.add_subplot(111)
# ax.semilogy(1000 / ignition_delays.T, tau, "o-")
# ax.set_ylabel("Ignition Delay (s)")
# ax.set_xlabel(r"$\frac{1000}{T (K)}$", fontsize=18)

# # Add a second axis on top to plot the temperature for better readability
# ax2 = ax.twiny()
# ticks = ax.get_xticks()
# ax2.set_xticks(ticks)
# ax2.set_xticklabels((1000 / ticks).round(1))
# ax2.set_xlim(ax.get_xlim())
# ax2.set_xlabel("Temperature: $T(K)$");