import pandapower as pp
import numpy as np
from pandapower import timeseries as ts
import matplotlib.pyplot as plt
import random
from random import *

net = pp.create_empty_network()

# Création des bus :
bus1 = pp.create_bus(net, vn_kv=0.4, name='Générateur')  # pour le générateur
bus2 = pp.create_bus(net, vn_kv=0.4, name='Stockage')  # pour le stockage
bus3 = pp.create_bus(net, vn_kv=0.4, name='Charge')  # pour la charge


# Création des composants
pv = pp.create_sgen(net, bus=bus1, p_mw=0.05, index=1, q_mvar=0, type='PV')  # Ajouter un générateur photovoltaïque
storage1 = pp.create_storage(net, bus=bus2, p_mw=0.00, index=2, min_p_mw=0.0064, max_p_mw=0.018,
                                       min_e_mwh=0, max_e_mwh=0.0144, q_mvar=0, min_q_mvar=-0.1, max_q_mvar=0.1
                                       , soc_percent=50, controllable=True)

load1 = pp.create_load(net, bus=bus3, p_mw=0.02, index=3,  q_mvar=0.1)  # Ajouter une charge à la maison

#  Création des lignes + switchs entre les composants :

# LINE1 : Ajouter une connexion entre la batterie et le générateur photovoltaïque
line1 = pp.create_line(net, from_bus=bus1, to_bus=bus2, length_km=0.01, std_type='NAYY 4x50 SE', name='line1')
sw1 = pp.create_switch(net, bus=bus1, element=line1, et='l', closed=True)
# LINE2 : Ajouter une connexion entre le générateur photovoltaïque et la charge
line2 = pp.create_line(net, from_bus=bus1, to_bus=bus3, length_km=0.01, std_type='NAYY 4x50 SE', name='line2')
sw2 = pp.create_switch(net, bus=bus1, element=line2, et='l', closed=True)
# LINE3 : Ajouter une connexion entre la batterie et la charge
line3 = pp.create_line(net, from_bus=bus2, to_bus=bus3, length_km=0.01, std_type='NAYY 4x50 SE', name='line3')
sw3 = pp.create_switch(net, bus=bus2, element=line3, et='l', closed=True)


# Initialiser les valeurs de la simulation
timesteps = [k for k in range(0, 24 * 4)]  # 24 heures avec des mises à jour toutes les 15 minutes
pv_power = net.sgen.at[1, 'p_mw']  # Puissance fixe du générateur photovoltaïque
soc = net.storage.at[2, 'soc_percent']
capacite = net.storage.at[2, 'max_e_mwh']
list_soc = []  # État de charge initial de la batterie
list_demand = []


# Modélisation de la puissance du pv par une Gaussienne
# Définir les paramètres de la gaussienne

def list_gaussienne(amplitude, centre, ecart_type, t):
    x = t.copy()
    y = x.copy()
    for k in range(len(x)):
        y[k] = amplitude * np.exp(-(x[k] - centre)**2 / (2 * ecart_type**2)) + (random() / 10) * amplitude
    return y


list_pv_power = list_gaussienne(0.003, 48, 25, timesteps)
Temps = [k/4 for k in range(len(timesteps))]
plt.plot(Temps, list_pv_power, label='pv_power1')
plt.show()
# Simuler la journée complète
for timestep in range(len(timesteps)):
    # Déterminer la demande actuelle de la charge
    net.load.at[3, 'p_mw'] = np.random.uniform(0, 0.00350)
    demand = net.load.at[3, 'p_mw']
    list_soc.append(soc)
    list_demand.append(demand)
    pv_power = list_pv_power[timestep]
    # Calculer la puissance de charge/décharge de la batterie
    if pv_power >= demand:   # le pv fournie à la charge et recharge la batterie avec le surplus
        pv_exces = pv_power - demand
        soc = min(100, soc + ((pv_exces / 4) / capacite) * 100)  # convertit en W, sec et %
    else:       # la batterie aide le pv à fournir la puissance nécessaire
        if demand > pv_power:
            pv_aide = demand - pv_power
            if (pv_aide / 4 / capacite) * 100 < soc:
                soc = max(0, soc - ((pv_aide / 4) / capacite) * 100)
            else:
                print("pas assez d'énergie pour alimenter sur 15min, on charge la batterie sur 15min")
                soc += ((pv_power / 4) / capacite) * 100

# Affichage des graphes

Temps = [k/4 for k in range(len(timesteps))]

for tps in range(0, len(list_pv_power)):
    list_pv_power[tps] = 1000 * list_pv_power[tps]
    list_demand[tps] = 1000 * list_demand[tps]

plt.subplot(1, 2, 1)
plt.plot(Temps, list_pv_power, label='pv_power')
plt.plot(Temps, list_demand, label='load_power')
plt.xlabel('Temps (en h)')
plt.ylabel('Puissance (kW)')
plt.title('Puissances sur une journée')
plt.legend()

plt.subplot(1, 2, 2)
plt.plot(Temps, list_soc, label='soc')
plt.xlabel('Temps (en h)')
plt.title('Etat de charge en %')
plt.legend()

plt.show()

