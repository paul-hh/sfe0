from pymgrid import Microgrid
from pymgrid.modules import LoadModule, RenewableModule, BatteryModule
from pymgrid.control import SimpleBatteryController
import numpy as np

timesteps = 24*60  # 24 heures avec un échantillonnage toutes les minutes
load = LoadModule(10*np.random.rand(timesteps))
pv = RenewableModule(10*np.random.rand(timesteps))

battery = BatteryModule(min_capacity=0,
                        max_capacity=1000,
                        max_charge=5,
                        max_discharge=10,
                        efficiency=0.9,
                        init_soc=0.5)

mg = Microgrid(modules=[load, ('pv', pv), battery])

# Contrôle de la batterie : charge si la batterie est déchargée, décharge si la batterie est pleine
battery_controller = SimpleBatteryController(target_battery_soc=0.5)

for i in range(timesteps):
    obs = mg.get_observation()
    control = battery_controller.get_control(obs)
    mg.run(control)

# Récupération des résultats
results = mg.get_formatted_results()
print(results)
