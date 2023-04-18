import numpy as np
import matplotlib.pyplot as plt
import random


def Vect(alpha1, alpha2, alpha3, alpha4, beta1, beta2, gamma):
    return [alpha1, alpha2, alpha3, alpha4, beta1, beta2, gamma]


temps = [k for k in range(0, 10000)]


def pv__power(amplitude, centre, ecart_type, t):
    x = t
    y = x
    for k in range(len(x)):
        y[k] = amplitude * np.exp(-(x[k] - centre)**2 / (2 * ecart_type**2))
    return y


soc1 = [50 for k in range(0, len(temps))]
soc2 = [50 for k in range(0, len(temps))]
load1 = []
load2 = []
pv_power = []

parametres = Vect(0.25, 0.25, 0.25, 0.25, 0.1, 0.1, 0)

alpha1, alpha2, alpha3, alpha4, beta1, beta2, gamma = parametres[0], parametres[1], parametres[2], parametres[3], \
    parametres[4], parametres[5], parametres[6]

p_bat1 = [0 for k in range(0, len(temps))]
p_bat2 = [0 for k in range(0, len(temps))]

for t in range(1, len(temps)):
    load1.append([random.uniform(0.01, 0.07)])
    load2.append([random.uniform(0.01, 0.07)])
    pv_power.append([pv__power(0.05, 5000, 2500, t)])
    p_bat1[t] = pv_power[t] * (alpha2 * (1 + beta2) + gamma * alpha3) / ((1 + beta1) * (1 + beta2) + gamma**2)
    p_bat2[t] = pv_power[t] * (alpha3 * (1 + beta1) - gamma * alpha2) / ((1 + beta1) * (1 + beta2) + gamma**2)
    soc1[t] = soc1[t-1] + parametres[1] * pv_power[t] - parametres[4] * p_bat1[t]
    soc2[t] = soc2[t-1] + parametres[1] * pv_power[t] - parametres[4] * p_bat1[t]

