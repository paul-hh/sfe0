import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from pymgrid import Microgrid
from pymgrid.modules import (
    BatteryModule,
    GridModule
)

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
                          init_soc=0.2)

grid_ts = [0.2, 0.1, 0.5] * np.ones((24*90, 3))
grid = GridModule(max_import=100,
                  max_export=100,
                  time_series=grid_ts)

# Création de la microgrille avec les modules
modules = [battery_0, battery_1, grid]
microgrid = Microgrid(modules)

# Initialisation des listes pour stocker les données
time = []
battery_0_soc = []
battery_1_soc = []
grid_import = []

# Boucle de simulation sur une période de 24 heures
for t in range(24):
    # Calcul du déficit de charge
    net_load = -1 * (100 - np.random.randint(0, 50))  # Charge aléatoire entre 50 et 100 kW
    net_load += battery_0.max_production + battery_1.max_production

    # Dispatch de la charge sur les batteries et la grille électrique
    battery_0_discharge = min(-1 * net_load / 2, battery_0.max_production)
    net_load += battery_0_discharge

    battery_1_discharge = min(-1 * net_load / 2, battery_1.max_production)
    net_load += battery_1_discharge

    grid_import_value = min(-1 * net_load, grid.max_production)
    net_load += grid_import_value

    control = {"battery": [battery_0_discharge, battery_1_discharge],
               "grid": [grid_import_value]}

    # Exécution de la simulation
    obs, reward, done, info = microgrid.run(control)

    # Stockage des données
    time.append(t)
    battery_0_soc.append(battery_0.soc)
    battery_1_soc.append(battery_1.soc)
    grid_import.append(grid_import_value)

# Affichage des données
df = pd.DataFrame({"Time (h)": time,
                   "Battery 0 SoC": battery_0_soc,
                   "Battery 1 SoC": battery_1_soc,
                   "Grid Import": grid_import})

# Tracé des courbes de SoC des batteries et des importations de la grille électrique
fig, ax1 = plt.subplots()

color = 'tab:red'
ax1.set_xlabel('Time (h)')
ax1.set_ylabel('Battery SoC', color=color)
ax1.plot(time, battery_0_soc, label="Battery 0", color=color)
ax1.plot(time, battery_1_soc, label="Battery 1", linestyle='dashed', color=color)
ax1.tick_params(axis='y', labelcolor=color)

ax2 = ax1.twinx()  # instanciation d'un deuxième axe y partageant le même axe x

color = 'tab:blue'
ax2.set_ylabel('Grid Import (kW)', color=color)
ax2.set_ylabel('Grid Import (kW)', color=color)
ax2.plot(time, grid_import, label="Grid Import", color=color)
ax2.tick_params(axis='y', labelcolor=color)

plt.title("Battery SoC and Grid Import")
fig.legend(loc="upper left")
plt.show()
