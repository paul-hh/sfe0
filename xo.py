from pymgrid import MicrogridGenerator

# Création d'un objet MicrogridGenerator
mg = MicrogridGenerator(nb_microgrid=1)

# Définition des paramètres du micro-réseau
timestep = 60  # durée d'un pas de temps (en secondes)
nb_timesteps = 24*60*60//timestep  # nombre de pas de temps sur une journée
pv_capacity = 10  # capacité du panneau solaire (en kW)
battery_capacity = 50  # capacité de la batterie (en kWh)
charge_power = 5  # puissance de la charge (en kW)

# Définition des modules du micro-réseau
pv = mg.add_renewable_module(pv_capacity, nb_timesteps)
battery = mg.add_battery_module(battery_capacity, battery_capacity, nb_timesteps, battery_type='discharge')
charge = mg.add_load_module(nb_timesteps)

# Connexion des modules
mg.connect(pv, battery, charge)

# Création d'un objet Control
control = Control(mg)

# Définition des règles de contrôle
control.set_renewable_production_limits(pv, 0, pv_capacity)  # limite de production du panneau solaire
control.set_battery_discharge_limit(battery, -battery_capacity)  # limite de décharge de la batterie
control.set_battery_charge_limit(battery, battery_capacity)  # limite de charge de la batterie
control.set_load_forecast(charge, [charge_power]*nb_timesteps)  # prévision de la charge

# Exécution de la simulation
mg.run(control)

# Récupération des résultats
pv_production = pv.get_production()
battery_charge = battery.get_charge()
battery_discharge = battery.get_discharge()
charge_consumption = charge.get_consumption()

# Affichage des résultats
import matplotlib.pyplot as plt

plt.plot(pv_production, label='PV production')
plt.plot(battery_charge, label='Battery charge')
plt.plot(battery_discharge, label='Battery discharge')
plt.plot(charge_consumption, label='Charge consumption')
plt.legend()
plt.show()
