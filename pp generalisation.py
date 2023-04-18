import pandapower as pp
import numpy as np
import random
from random import *
import matplotlib.pyplot as plt

net = pp.create_empty_network()

nombre_de_foyers = 4  # chaque foyer dispose de sa batterie et son PV et les batteries sont reliées entre elles.

# Création des temporalitées :
Temps = 24 * 3600  # (en s)
dt = 0.25 * 3600  # (pas de temps en s)
nbr_pas_temps = int(Temps / dt)
timesteps = [k for k in range(0, nbr_pas_temps)]


# Création des bus : # Numérotés de [0, nombre_de_foyers - 1] = pvs, puis les batteries et ensuite les charges.
bus = []
for buses in range(0, 3 * nombre_de_foyers):
    bus.append(pp.create_bus(net, vn_kv=0.4, name='bus' + str(buses)))

# Création des composants :
pvs = []
batteries = []
charges = []

for composants in range(nombre_de_foyers):

    pvs.append(pp.create_sgen(net, bus=bus[composants], p_mw=0.020, index=composants, q_mvar=0, type='PV', slack=True))

    batteries.append(pp.create_storage(net, bus=bus[nombre_de_foyers + composants], p_mw=0.00, index=nombre_de_foyers +
                                       composants, min_p_mw=-0.015, max_p_mw=0.015, min_e_mwh=0, max_e_mwh=0.00625,
                                       q_mvar=0, min_q_mvar=-0.1, max_q_mvar=0.1, soc_percent=50, controllable=True))

    charges.append(pp.create_load(net, bus=bus[2 * nombre_de_foyers + composants], p_mw=0.0125, index=2 *
                                  nombre_de_foyers + composants, q_mvar=0.1))

# Creation des PVs, charges et socs :


def list_gaussienne(amplitude, centre, ecart_type, t):
    x = t.copy()
    y = x.copy()
    for k in range(len(x)):
        y[k] = amplitude * np.exp(-(x[k] - centre)**2 / (2 * ecart_type**2)) + (random() / 10) * amplitude
    return y


def list_charges(mini, list_temps, num_charge):
    charge = []
    for temps in range(0, len(list_temps)):
        charge.append(np.random.uniform(mini, net.load.at[num_charge, 'p_mw']))
    return charge

puissances_pvs = []
puissances_loads = []
liste_soc = []
for pv in range(0, nombre_de_foyers):
    puissances_pvs.append(list_gaussienne(net.sgen.at[pv, 'p_mw'], len(timesteps) / 2, 20, timesteps))
    puissances_loads.append(list_charges(min, timesteps, 2 * nombre_de_foyers + pv))
    liste_soc.append([])

# Création des variables caractérisants les fluxs :
nombre_variables = int(nombre_de_foyers * 3 + nombre_de_foyers * (nombre_de_foyers - 1) / 2)  # alphas + gammas

variables = np.zeros((nombre_variables, len(timesteps)))
pas_variable = 0.1  # pas entre l'essai de deux variables pour l'optimisation

for timestep in range(0, len(timesteps)):
    for ligne in range(0, len(variables)):
        for colonne in range(0, len(variables)):
            if







