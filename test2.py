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
    charge_production.append(load_value_0 + load_value_1)

    # Calcul de la production des batteries
    battery_0_discharge = min(-1 * (load_value_0 - pv_prod / 2), battery_0.max_production)
    battery_1_discharge = min(-1 * (load_value_1 - pv_prod / 2), battery_1.max_production)

    # Dispatch de la charge sur les batteries et la grille électrique
    grid_import_value = min(-1 * (load_value_0 - battery_0_discharge - load_value_1 - battery_1_discharge - pv_prod), grid.max_production)

    control = {"battery": [battery_0_discharge, battery_1_discharge],
               "grid": [grid_import_value]}

    # Exécution de la simulation
    obs, reward, done, info = microgrid.run(control)

    # Stockage des données
    time.append(t)
    battery_0_production.append(battery_0_discharge)
    battery_1_production.append(battery_1_discharge)
    battery_0_soc.append(battery_0.soc)
    battery_1_soc.append(battery_1.soc)

# Affichage des données
df = pd.DataFrame({"Time (h)": time,
                   "PV Production (kW)": pv_production,
                   "Load 0 (kW)": load_0,
                   "Load 1 (kW)": load_1,
                   "Battery 0 Production (kW)": battery_0_production,
                   "Battery 1 Production (kW)": battery_1_production,
                   "Battery 0 SOC": battery_0_soc,
                   "Battery 1 SOC": battery_1_soc
                   })


# Plot power flows
fig, ax = plt.subplots(figsize=(12, 8))

ax.plot(pv_production, label='PV Production')
ax.plot(load_0, label='Load 0')
ax.plot(load_1, label='Load 1')
ax.plot(battery_0_production, label='Battery 0 Production')
ax.plot(battery_1_production, label='Battery 1 Production')

ax.set_xlabel('Hour of Year')
ax.set_ylabel('Power (kW)')
ax.set_title('Power Flows')

ax.legend(loc='upper center', ncol=4)
plt.show()

# Plot SoC
fig, ax = plt.subplots(figsize=(12,8))

ax.plot(battery_0_soc, label='Battery 0 SOC')
ax.plot(battery_1_soc, label='Battery 1 SOC')

ax.set_xlabel('Hour of Year')
ax.set_ylabel('State of Charge')
ax.set_title('State of Charge')

ax.legend(loc='upper center', ncol=2)
plt.show()


