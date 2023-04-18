import numpy as np
from scipy.integrate import odeint
import matplotlib.pyplot as plt

# Définition des constantes du modèle de circuit équivalent de la batterie
R0 = 0.1  # résistance interne de la batterie
C1 = 100  # capacité de la batterie
C2 = 50   # capacité de surface de la batterie
V0 = 48   # tension de la source

# Définition de la fonction de décharge de la batterie
def battery_model(x, t, R0, C1, C2, V0):
    V1, V2, Q = x
    I = (V0 - V1 - V2 - Q/C1 * R0) / (R0 + (C1 + C2) * Q / (C1 * C2))
    dV1 = - I - V1 / R0
    dV2 = - I - V2 / (R0 * C2)
    dQ = - I * C1
    return [dV1, dV2, dQ]

# Conditions initiales de la simulation de la charge de la batterie
x0 = [0, 0, 0.5 * C1]  # V1, V2, Q
t = np.linspace(0, 3600, 100)  # temps en secondes

# Simulation de la charge de la batterie
x = odeint(battery_model, x0, t, args=(R0, C1, C2, V0))

# Tracé des résultats de la simulation
plt.plot(t, x[:, 2] / C1 * 100)  # pourcentage de la capacité de la batterie
plt.xlabel('Temps (s)')
plt.ylabel('Charge de la batterie (%)')
plt.show()
