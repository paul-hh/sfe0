# HENON-HILAIRE PAUL
# Mars 2023

# Code python de la méthode Round Robin appliquée à N batteries. À chaque tour de boucle les batteries sont organisées
# dans l'ordre croissant de leur soc. La batterie ayant le plus de soc donne à celle en ayant le moins. Une batterie ne
# peut donner qu'une fois tous les N tour.

import pandapower as pp
import numpy as np
import random
from random import *
import matplotlib.pyplot as plt
from matplotlib.pyplot import *
from tqdm import tqdm
from multiprocessing import cpu_count, Pool

nombre = 4
nombre_simu = 10
nombre_de_foyers_max = 10


moyenne_coupure = 0
moyenne_nrj = 0
liste_coupure_moyenne = []
liste_energie_perdue = []
liste_moyenne_soc = []
liste_moyenne_std = []

# Création des temporalitées :
Temps = 24 * 3600  # (en s)
dt = (1 / 6) * 3600  # (pas de temps en s)
nbr_pas_temps = int(Temps / dt)
timesteps = [k for k in range(0, nbr_pas_temps)]


def mo_var_ecartype(liste):
    return np.average(liste), np.var(liste), np.std(liste)


def list_gaussienne(amplitude, centre, ecart_type, t):
    x = t.copy()
    y = x.copy()
    for k in range(len(x)):
        y[k] = amplitude * np.exp(-(x[k] - centre) ** 2 / (2 * ecart_type ** 2)) + (random() / 10) * amplitude
    return y


def list_charges(mini, list_temps, num_charge):
    charge = []
    for temps in range(0, len(list_temps)):
        charge.append(np.random.uniform(mini, net.load.at[num_charge, 'p_mw']))
    return charge


# Tableau des échanges entre batteries

tab_n_donne = []
tab_n_recoit = []
for k in range(0, nombre):
    tab_n_donne.append(0)
    tab_n_recoit.append(0)
tab_n_donne = np.asarray(tab_n_donne)
tab_n_recoit = np.asarray(tab_n_recoit)


# tableaux des taux de variations du soc
tab_taux_var = []
for k in range(0, nombre):
    tab_taux_var.append([])
    for tps in range(0, len(timesteps)):
        tab_taux_var[k].append(0)
tab_taux_var = np.asarray(tab_taux_var)

# for nombre in range(2, nombre_de_foyers_max + 1):
#     moyenne_nrj = 0
#     moyenne_coupure = 0
#     moyenne_soc = 0
#     moyenne_std = 0
for time in tqdm(range(0, nombre_simu)):
    net = pp.create_empty_network()

    n_donne = []
    n_recoit = []  # listes des nombres de donations et receptions de chaque batterie
    for k in range(0, nombre):
        n_donne.append(0)
        n_recoit.append(0)

    energie_perdue = 0
    nbr_coupure = 0
    nombre_de_foyers = 4  # chaque foyer dispose de sa batterie et son PV et les batteries sont reliées entre elles.

    liste_taux_var = []
    for k in range(0, nombre):
        liste_taux_var.append([])

    # Création des bus : # Numérotés de [0, nombre_de_foyers - 1] = pvs, puis les batteries et ensuite les charges.
    bus = []
    for buses in range(0, 3 * nombre_de_foyers):
        bus.append(pp.create_bus(net, vn_kv=0.4, name='bus' + str(buses)))

    # Création des composants :
    pvs = []
    batteries = []
    charges = []

    for composants in range(nombre_de_foyers):

        pvs.append(pp.create_sgen(net, bus=bus[composants], p_mw=0.003, index=composants, q_mvar=0, type='PV', slack=True))

        batteries.append(pp.create_storage(net, bus=bus[nombre_de_foyers + composants], p_mw=0.00,
                                           index=nombre_de_foyers + composants, min_p_mw=0.0064, max_p_mw=0.018,
                                           min_e_mwh=0, max_e_mwh=0.0144, q_mvar=0, min_q_mvar=-0.1, max_q_mvar=0.1
                                           , soc_percent=50, controllable=True))

        charges.append(pp.create_load(net, bus=bus[2 * nombre_de_foyers + composants], p_mw=0.00350, index=2 *
                                      nombre_de_foyers + composants, q_mvar=0.1))

    # Creation des PVs, charges et socs :

    puissances_pvs = []
    puissances_loads = []
    mini = 0  # minimum de charge
    liste_soc = []  # liste des socs par batterie à un instant t
    liste_soc_temps = []  # liste des socs par batterie dans le temps

    for pv in range(0, nombre_de_foyers):
        tirage = random()
        if tirage >= 0.5:
            decalage = - 4 * tirage
        else:
            decalage = 4 * (1 - tirage)
        puissances_pvs.append(list_gaussienne(net.sgen.at[pv, 'p_mw'], len(timesteps) / 2 + decalage, len(timesteps) / 6,
                                              timesteps))
        puissances_loads.append(list_charges(mini, timesteps, 2 * nombre_de_foyers + pv))
        liste_soc.append(net.storage.at[nombre_de_foyers + pv, 'soc_percent'])
        liste_soc_temps.append([])

    liste_des_index = []
    p_max_e = net.storage.at[nombre_de_foyers + 1, 'min_p_mw']
    p_max_s = net.storage.at[nombre_de_foyers + 1, 'max_p_mw']
    capacite = net.storage.at[nombre_de_foyers + 1, 'max_e_mwh']

    for timestep in range(0, len(timesteps)):

        tx1 = []
        for batterie in range(0, nombre_de_foyers):
            liste_soc[batterie] = net.storage.at[nombre_de_foyers + batterie, 'soc_percent']
            tx1.append(liste_soc[batterie])

        tab_soc = np.asarray(liste_soc)
        index_trier = tab_soc.argsort()  # renvoie la liste des indices dans l'ordre des socs
        index_max = index_trier[nombre_de_foyers - 1]

        if len(liste_des_index) == nombre_de_foyers - 1:
            liste_des_index = []

        compt = 2

        while index_max in liste_des_index:
            index_max = index_trier[nombre_de_foyers - compt]
            compt += 1

        index_min = index_trier[0]

        if index_max != index_min:

            liste_des_index.append(index_max)
            min_soc = liste_soc[index_trier[index_min]]
            max_soc = liste_soc[index_trier[index_max]]

            liste_soc[index_trier[index_min]] += 0.1 * liste_soc[index_trier[index_max]]
            n_recoit[index_trier[index_min]] += 1

            liste_soc[index_trier[index_max]] -= 0.1 * liste_soc[index_trier[index_max]]
            n_donne[index_trier[index_max]] += 1

        for batterie in range(0, nombre_de_foyers):
            net.storage.at[nombre_de_foyers + batterie, 'soc_percent'] = liste_soc[batterie]

        # On actualise ensuite les socs après avoir fait les opérations de transfert entre batteries
        for composant in range(0, nombre_de_foyers):
            soc = net.storage.at[nombre_de_foyers + composant, 'soc_percent']
            surplu = puissances_pvs[composant][timestep] - puissances_loads[composant][timestep]  # surplu de puissance
            if surplu > 0:  # on charge la batterie
                soc_mod = soc + min(p_max_e, surplu) * dt / 3600 / capacite * 100
            if surplu <= 0:  # on décharge la batterie
                soc_mod = soc + max(- p_max_s, surplu) * dt / 3600 / capacite * 100
            if soc_mod < 0:  # on ne descend pas en dessous de 0%
                energie_perdue += (-soc_mod / 100) * capacite
                soc_mod = 0
                nbr_coupure += 1
            if soc_mod > 100:  # on ne monte pas au-dessus de 100%
                energie_perdue += ((soc_mod - 100) / 100) * capacite
                soc_mod = 100

            net.storage.at[nombre_de_foyers + composant, 'soc_percent'] = soc_mod  # on met à jour la liste des SOC
            tab_soc[composant] = soc_mod
            liste_soc_temps[composant].append(soc_mod)

            liste_taux_var[composant].append(soc_mod - tx1[composant])

    liste_taux_var = np.array(liste_taux_var)
    tab_taux_var = np.add(tab_taux_var, liste_taux_var)

    tab_n_donne += np.asarray(n_donne)
    tab_n_recoit += np.asarray(n_recoit)

    moyenne_coupure += nbr_coupure
    moyenne_nrj += energie_perdue

for k in range(0, nombre_de_foyers):
    tab_n_donne[k] = tab_n_donne[k] / nombre_simu
    tab_n_recoit[k] = tab_n_recoit[k] / nombre_simu  # Tableaux des nbr de dons, donations par batteries en moyenne


moyenne_coupure = moyenne_coupure / nombre_simu
moyenne_nrj = moyenne_nrj / nombre_simu

tab_taux_var = tab_taux_var / nombre_simu

liste_taux_pos, liste_taux_neg = [], []
for batterie in range(0, nombre_de_foyers):
    liste_taux_pos.append([])
    liste_taux_neg.append([])
    for tps in range(0, len(timesteps)):
        if tab_taux_var[batterie][tps] >= 0:
            liste_taux_pos[batterie].append(tab_taux_var[batterie][tps])
        if tab_taux_var[batterie][tps] < 0:
            liste_taux_neg[batterie].append(tab_taux_var[batterie][tps])

print(liste_taux_pos)
print(liste_taux_neg)
print(sum(liste_taux_pos[0]), sum(liste_taux_neg[0]))

#     moyenne_soc += mo_var_ecartype(liste_soc_temps)[0]
#     for nano in range(0, nombre_de_foyers):  # Retourne le soc moyen de tous les nano-grids
#         moyenne_std += mo_var_ecartype(liste_soc_temps[nano])[2]
# moyenne_std = moyenne_std / nombre_de_foyers
#

# moyenne_soc = moyenne_soc / nombre_simu
# moyenne_std = moyenne_std / nombre_simu
#
# liste_coupure_moyenne.append(moyenne_coupure)
# liste_energie_perdue.append(moyenne_nrj)
# liste_moyenne_soc.append(moyenne_soc)
# liste_moyenne_std.append(moyenne_std)


# print('moyenne coupure : ' + str(moyenne_coupure / nombre_simu))
# print('moyenne énergie perdue : ' + str(moyenne_nrj / nombre_simu) + ' (MW)')

liste_temps = [k * dt / 3600 for k in range(len(timesteps))]
colors = ['blue', 'green', 'red', 'orange', 'darkblue', 'yellow', 'black', 'grey', 'cyan']
line_styles = ['-', '--', ':', 'o']

for composant in range(0, nombre_de_foyers):
    plt.subplot(3, 1, 1)
    plt.plot(liste_temps, puissances_pvs[composant], label='PV ' + str(composant), color=colors[composant],
             linestyle=line_styles[0])
    plt.xlabel('Temps (en h)')
    plt.ylabel('Puissance (MW)')
    plt.legend(loc='upper left', prop={'size': 8})
    plt.subplot(3, 1, 2)
    plt.plot(liste_temps, puissances_loads[composant], label='Charge ' + str(composant), color=colors[composant],
             linestyle=line_styles[1])
    plt.xlabel('Temps (en h)')
    plt.ylabel('Puissance (MW)')
    plt.legend(loc='upper left', prop={'size': 8})
    plt.subplot(3, 1, 3)
    plt.plot(liste_temps, liste_soc_temps[composant], label='SOC ' + str(composant), color=colors[composant],
             linestyle=line_styles[0])
    plt.xlabel('Temps (en h)')
    plt.ylabel('SOC (en %)')
    plt.legend(loc='upper left', prop={'size': 8})

plt.tight_layout()
plt.show()

# l_nombre = [k for k in range(2, nombre_de_foyers_max + 1)]
# liste_coupure_moyenne = np.asarray(liste_coupure_moyenne)
# liste_energie_perdue = np.asarray(liste_energie_perdue)
# liste_moyenne_soc = np.asarray(liste_moyenne_soc)
# liste_moyenne_std = np.asarray(liste_moyenne_std)
#
# plt.subplot(2, 2, 1)
# plt.bar(l_nombre, liste_coupure_moyenne / l_nombre, color='red')
# plt.xlabel('Nombre de nano-grid')
# plt.ylabel('Nombre de coupures par jour')
#
# plt.subplot(2, 2, 2)
# plt.bar(l_nombre, 1000 * liste_energie_perdue / l_nombre, color='green')
# plt.xlabel('Nombre de nano-grid')
# plt.ylabel('Energie perdue par jour en kW')
#
# plt.subplot(2, 2, 3)
# plt.bar(l_nombre, liste_moyenne_soc, color='orange')
# plt.xlabel('Nombre de nano-grid')
# plt.ylabel('Moyenne des SOC')
#
# plt.subplot(2, 2, 4)
# plt.bar(l_nombre, liste_moyenne_std, color='blue')
# plt.xlabel('Nombre de nano-grid')
# plt.ylabel('ecart-type moyen')
#
# plt.show()

