import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from pymgrid import Microgrid
from pymgrid.modules import BatteryModule, GridModule

# Création des modules pour les batteries et la grille électrique
battery_0 = BatteryModule(min_capacity=10,
                          max_capacity=1000,
                          max_charge=10,
                          max_discharge=10,
                          efficiency=0.7,
                          init_soc=0.2)

battery_1 = BatteryModule(min_capacity=10,
                          max_capacity=1000,
                          max_charge=10,
                          max_discharge=10,
                          efficiency=0.7,
                          init_soc=0.6)

grid_ts = [0.2, 0.1, 0.5] * np.ones((24*90, 3))
grid = GridModule(max_import=100,
                  max_export=100,
                  time_series=grid_ts)

# Création de la microgrille avec les modules
modules = [battery_0, battery_1, grid]
microgrid = Microgrid(modules)

# Initialisation des listes pour stocker les données
time = []
pv_production = []
charge_production = []
battery_0_production = []
battery_1_production = []
battery_0_soc = []
battery_1_soc = []
load_0 = []
load_1 = []


def update_battery_soc(soc, discharge_power, charge_power, capacity, time_step):
    """
    Met à jour l'état de charge (SOC) d'une batterie avec les charges et décharges spécifiées
     et la capacité et le temps spécifiés.

     Arguments :
     - soc : l'état de charge actuel de la batterie
     - discharge_power : la puissance de décharge de la batterie
     - charge_power : la puissance de charge de la batterie
     - capacity : la capacité de la batterie
     - time_step : la durée de l'intervalle de temps

     Renvoie :
     - le nouvel état de charge de la batterie
     """
    return max(0, min(soc + (charge_power / capacity) * time_step - (discharge_power / capacity) * time_step, 1))


# Boucle de simulation sur une période de 24 heures
for t in range(24):

    # Production aléatoire du panneau solaire
    pv_prod = np.random.randint(0, 500)
    pv_production.append(pv_prod)

    # Charge aléatoire des résistances
    load_value_0 = np.random.randint(0, 50)
    load_value_1 = np.random.randint(0, 50)
    load_0.append(load_value_0)
    load_1.append(load_value_1)

    # Vérifier si la production dépasse la demande
    excess_power = pv_prod - (load_value_0 + load_value_1)

    # Si la production est supérieure à la demande, alors charger les batteries
    if excess_power > 0:
        # Calculer la puissance disponible pour chaque batterie
        battery_0_charge = min(excess_power / 2, battery_0.max_charge)
        battery_1_charge = min(excess_power / 2, battery_1.max_charge)

        # Dispatch de la charge sur les batteries et la grille électrique
        control = {"battery": [battery_0_charge, battery_1_charge], "grid": 0}
        try:
            battery_0.update(control["battery"][0], pv_prod)
            battery_1.update(control["battery"][1], pv_prod)
        except AssertionError as e:
            print(f"Error: {e}")
            continue

    # Si la demande est supérieure à la production, alors décharger les batteries
    else:
        # Calculer la puissance nécessaire pour satisfaire la demande
        power_needed = abs(excess_power)

        # Calculer la puissance disponible pour chaque batterie
        battery_0_discharge = min(power_needed / 2, battery_0.max_discharge)
        battery_1_discharge = min(power_needed / 2, battery_1.max_discharge)

        # Dispatch de la décharge sur les batteries et la grille électrique
        control = {"battery": [-battery_0_discharge, -battery_1_discharge], "grid": 0}
        try:
            battery_0.update(control["battery"][0], pv_prod)
            battery_1.update(control["battery"][1], pv_prod)
        except AssertionError as e:
            print(f"Error: {e}")
            continue

    # Mettre à jour l'état de charge de chaque batterie
    battery_0_soc.append(battery_0.soc)
    battery_1_soc.append(battery_1.soc)

    # Stocker l'heure actuelle
    time.append(t)

# Affichage des graphes
fig, axs = plt.subplots(4)

axs[0].plot(time, pv_production, label='PV Production')
axs[0].plot(time, load_0, label='Load 0')
axs[0].plot(time, load_1, label='Load 1')
axs[0].set_xlabel('Time (hours)')
axs[0].set_ylabel('Power (W)')
axs[0].legend()

axs[1].plot(time, charge_production, label='Charge Production')
axs[1].plot(time, battery_0_production, label='Battery 0 Production')
axs[1].plot(time, battery_1_production, label='Battery 1 Production')
axs[1].set_xlabel('Time (hours)')
axs[1].set_ylabel('Power (W)')
axs[1].legend()

axs[2].plot(time, battery_0_soc, label='Battery 0 SOC')
axs[2].plot(time, battery_1_soc, label='Battery 1 SOC')
axs[2].set_xlabel('Time (hours)')
axs[2].set_ylabel('State of Charge')
axs[2].legend()

plt.show()
