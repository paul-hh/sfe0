from Classes import *
import matplotlib.pyplot as plt

# Création des batteries
battery1 = Battery(capacity=500, voltage=48, charge=0.3 * 500)
battery2 = Battery(capacity=500, voltage=48, charge=0.5 * 500)

# Création de la source
source = Source(voltage=48)

# Création des résistances
resistance1 = Resistor(resistance=20)  # Résistance de 20 Ohms
resistance2 = Resistor(resistance=10)  # Résistance de 10 Ohms

# Initialisation des variables de temps et de niveau de charge minimum
time = 0  # temps en secondes
min_charge = 0  # charge minimum avant de s'arrêter la simulation
charge_history1 = []
charge_history2 = []
time_history = []

while True:
    # Calcul du courant total fourni par la source
    current_total = source.get_current([resistance1, resistance2])

    # Charge des batteries
    charged1 = battery1.recharge(current_total, 1)
    charged2 = battery2.recharge(current_total, 1)
    charge_history1.append(battery1.charge / battery1.capacity * 100)
    charge_history2.append(battery2.charge / battery2.capacity * 100)

    # Mise à jour du temps
    time += 1
    time_history.append(time / 3600)  # conversion en heures

    # Vérification si les batteries sont complètement chargées
    if battery1.get_charge() >= 500 and battery2.get_charge() >= 500:
        break

# Décharge des batteries jusqu'à ce que l'une atteigne un niveau de charge minimum
while battery1.get_charge() > min_charge and battery2.get_charge() > min_charge:
    # Calcul du courant total fourni par les batteries
    current_total = -(battery1.voltage + battery2.voltage) / resistance1.get_resistance()

    # Décharge des batteries
    discharged1 = battery1.discharge(current_total, 1)
    discharged2 = battery2.discharge(current_total, 1)
    charge_history1.append(battery1.charge / battery1.capacity * 100)
    charge_history2.append(battery2.charge / battery2.capacity * 100)

    # Mise à jour du temps
    time += 1
    time_history.append(time / 3600)  # conversion en heures

# Affichage des niveaux de charge finaux
print(f"Battery 1: {battery1.get_charge() / 5:.2f}%")
print(f"Battery 2: {battery2.get_charge() / 5:.2f}%")
plt.plot(time_history, charge_history1, label='Batterie 1')
plt.plot(time_history, charge_history2, label='Batterie 2')
plt.xlabel('Temps (h)')
plt.ylabel('Charge (%)')
plt.title('Niveau de charge des batteries')
plt.legend()
plt.show()
