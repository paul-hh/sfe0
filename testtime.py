from datetime import datetime, timedelta
import pandapower as pp
import numpy as np
import random
from random import *
import matplotlib.pyplot as plt
from matplotlib.pyplot import *
from tqdm import tqdm


def list_charges(mini, maxi, list_temps):
    charge = []
    for temps in range(0, len(list_temps)):
        charge.append(np.random.uniform(mini, maxi))
    return charge


# Création des temporalitées :
Temps = 31 * 24 * 3600  # (en s)
dt = (1 / 6) * 3600  # (pas de temps en s)
nbr_pas_temps = int(Temps / dt)
timesteps = [k for k in range(0, nbr_pas_temps)]


start_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

# Date de fin (un mois plus tard)
end_date = start_date + timedelta(days=31)

# Heures de début et de fin des deux périodes
day_start = datetime.now().replace(hour=7, minute=0, second=0, microsecond=0)
day_end = datetime.now().replace(hour=21, minute=0, second=0, microsecond=0)


nombre_de_foyers = 4

puissances_pvs = []
puissances_loads = []
mini = 0

if start_date >= day_start and start_date < day_end:
    # Ajouter une valeur spécifique pour les heures de jour
    puissances_loads.append(list_charges(mini, 3.75, timesteps))
else:
    # Ajouter une autre valeur pour les heures de nuit
    puissances_loads.append(list_charges(mini, 0.00052, timesteps))
start_date += timedelta(minutes=10)


liste_temps = [k for k in range(0, 4464)]


ax2 = plt.subplot(3, 1, 2)
ax2.plot(liste_temps, puissances_loads[0])
plt.xlabel('Temps (en j)')
plt.ylabel('Puissance (kW)')
plt.legend(loc='upper left', prop={'size': 8})

plt.show()


