# Importation des classes
from Classes import Battery, Source, Resistor
import matplotlib.pyplot as plt

# Création des composants
battery1 = Battery(capacity=100, voltage=48, charge=0.3)
battery2 = Battery(capacity=100, voltage=48, charge=0.5)
source = Source(voltage=48)
resistor1 = Resistor(resistance=20)
resistor2 = Resistor(resistance=10)

# Définition du temps de charge en secondes
time = 3 * 3600  # 3 heures en secondes

# Initialisation des listes pour le suivi de la charge des batteries
time_list = [0]  # liste pour le temps
charge_list1 = [battery1.get_charge()]  # liste pour la charge de la batterie1
charge_list2 = [battery2.get_charge()]  # liste pour la charge de la batterie2

# Charge des batteries
for t in range(time):
    # Calcul du courant de charge
    current1 = source.get_voltage() / resistor1.get_resistance()
    current2 = source.get_voltage() / resistor2.get_resistance()

    # Charge de la batterie 1
    charged1 = battery1.recharge(current=current1, time=1)
    # Charge de la batterie 2
    charged2 = battery2.recharge(current=current2, time=1)

    # Mise à jour des listes
    time_list.append(t+1)
    charge_list1.append(battery1.get_charge())
    charge_list2.append(battery2.get_charge())

# Affichage des graphes
plt.plot(time_list, charge_list1, label='Battery 1')
plt.plot(time_list, charge_list2, label='Battery 2')
plt.xlabel('Time (s)')
plt.ylabel('Charge (%)')
plt.title('Charge of batteries over time')
plt.legend()
plt.show()
