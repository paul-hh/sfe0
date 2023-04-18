import matplotlib.pyplot as plt
from Classes import *

# Création des composants
battery1 = Battery(capacity=100, voltage=48, charge=0.3*100)
battery2 = Battery(capacity=100, voltage=48, charge=0.5*100)
source1 = Source(voltage=48)
resistor1 = Resistor(resistance=10)
resistor2 = Resistor(resistance=20)

# Charge des batteries pendant 3h
time = 3 * 3600  # temps en secondes
dt = 1  # pas de temps en secondes
charge_history1 = []
charge_history2 = []
time_history = []

for t in range(0, time, dt):
    current1 = source1.get_voltage() / resistor1.get_resistance()
    current2 = source1.get_voltage() / resistor2.get_resistance()
    charged1 = battery1.recharge(current1, dt)
    charged2 = battery2.recharge(current2, dt)
    charge_history1.append(battery1.charge / battery1.capacity * 100)
    charge_history2.append(battery2.charge / battery2.capacity * 100)
    time_history.append(t / 3600)

# Affichage du graphe
plt.plot(time_history, charge_history1, label='Batterie 1')
plt.plot(time_history, charge_history2, label='Batterie 2')
plt.xlabel('Temps (h)')
plt.ylabel('Charge (%)')
plt.title('Niveau de charge des batteries')
plt.legend()
plt.show()
