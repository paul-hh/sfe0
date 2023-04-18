import pymgrid
from pymgrid import *
import random
import numpy as np
from pymgrid.modules import LoadModule, RenewableModule, BatteryModule

timesteps = 24*6  # 24h avec une résolution de 10 minutes

load = [random.randint(0, 10) in range(0, 24)]
pv = [0, 0, 0, 0, 0, 0, 0, 4, 4, 7, 7, 10, 10, 12, 12, 10, 7, 7, 5, 0, 0, 0, 0, 0] #Puissance en kW

battery_0 = BatteryModule(min_capacity=0,
                          max_capacity=1000,
                          max_charge=5,
                          max_discharge=10,
                          efficiency=0.9,
                          init_soc=0.5)

battery_1 = BatteryModule(min_capacity=0,
                          max_capacity=1000,
                          max_charge=5,
                          max_discharge=10,
                          efficiency=0.9,
                          init_soc=0.5)

#mg = Microgrid(modules=[load, ('pv', pv), battery_0, battery_1])


# Boucle de simulation actualisée toute les 10 min

# intelligence : on vide complètelement les batteries puis on les remplies
k = 0
for t in range(0, 24):
    heure = t // 6
    battery_0.soc += ((pv[t] - load[t]) * 1000 * 600) / 2
    battery_1.soc += ((pv[t] - load[t]) * 1000 * 600) / 2

print(battery_1.soc, battery_0.soc)

