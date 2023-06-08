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
from tqdm import tqdm
from manip_csv import extraction_donnee
from datetime import datetime, timedelta

moyenne_coupure = 0
moyenne_nrj = 0
liste_coupure_moyenne = []
liste_energie_perdue = []
liste_moyenne_soc = []
liste_moyenne_std = []

nombre_simu = 1
nombre = 4
nombre_de_foyers_max = 10

# Création des temporalitées :
Temps = 31 * 24 * 3600  # (en s)
dt = (1 / 6) * 3600  # (pas de temps en s)
nbr_pas_temps = int(Temps / dt)
timesteps = [k for k in range(0, nbr_pas_temps)]


def mo_var_ecartype(liste):
    return np.average(liste), np.var(liste), np.std(liste)


def list_gaussienne(amplitude, centre, ecart_type, t):
    # x = t.copy()
    # y = x.copy()
    # for k in range(len(x)):
    #     y[k] = amplitude * np.exp(-(x[k] - centre) ** 2 / (2 * ecart_type ** 2)) + (random() / 10) * amplitude
    # return y
    charge = []

    # Date de début (aujourd'hui à minuit)
    start_date = datetime(2016, 1, 1)

    # Date de fin (un mois plus tard)
    end_date = start_date + timedelta(days=31)

    # Heures de début et de fin des deux périodes
    day_start = start_date.replace(hour=7, minute=0, second=0, microsecond=0)
    day_end = start_date.replace(hour=21, minute=0, second=0, microsecond=0)

    # Boucle pour remplir la liste avec des valeurs toutes les 10 minutes
    while start_date < end_date:
        if start_date.hour >= 6 and start_date.hour < 22:
            # Ajouter une valeur spécifique pour les heures de jour
            charge.append(np.random.uniform(0, 0.0035))
        else:
            # Ajouter une autre valeur pour les heures de nuit
            charge.append(np.random.uniform(0, 0.00052))
        start_date += timedelta(minutes=10)
    return charge


def list_charges():
    # charge = []
    # for temps in range(0, len(list_temps)):
    #     charge.append(np.random.uniform(mini, maxi))
    # return charge
    charge = []

    # Date de début (aujourd'hui à minuit)
    start_date = datetime(2016, 1, 1)

    # Date de fin (un mois plus tard)
    end_date = start_date + timedelta(days=31)

    # Heures de début et de fin des deux périodes
    day_start = start_date.replace(hour=7, minute=0, second=0, microsecond=0)
    day_end = start_date.replace(hour=21, minute=0, second=0, microsecond=0)

    # Boucle pour remplir la liste avec des valeurs toutes les 10 minutes
    while start_date < end_date:
        if start_date.hour >= 6 and start_date.hour < 22:
            # Ajouter une valeur spécifique pour les heures de jour
            charge.append(np.random.uniform(0, 0.0035))
        else:
            # Ajouter une autre valeur pour les heures de nuit
            charge.append(np.random.uniform(0, 0.00052))
        start_date += timedelta(minutes=10)
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

for nombre in range(2, nombre_de_foyers_max + 1):
    moyenne_nrj = 0
    moyenne_coupure = 0
    moyenne_soc = 0
    moyenne_std = 0
#for time in tqdm(range(0, nombre_simu)):
net = pp.create_empty_network()

energie_perdue = 0
nbr_coupure = 0
nombre_de_foyers = 4  # chaque foyer dispose de sa batterie et son PV et les batteries sont reliées entre elles.

liste_taux_var = []
for k in range(0, nombre):
    liste_taux_var.append([])

n_donne = []
n_recoit = []  # listes des nombres de donations et receptions de chaque batterie
for k in range(0, nombre):
    n_donne.append(0)
    n_recoit.append(0)

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

    puissances_pvs.append(extraction_donnee()[0] * (1 / 1000))
    # puissances_pvs.append(list_gaussienne(net.sgen.at[pv, 'p_mw'], len(timesteps) / 2 + decalage, len(timesteps) / 5,
    # timesteps))
    # puissances_loads.append(list_charges(mini, timesteps, 2 * nombre_de_foyers + pv))
    puissances_loads.append(list_charges())
    liste_soc_temps.append([])

liste_des_index = []
p_max_e = net.storage.at[nombre_de_foyers + 1, 'min_p_mw']
p_max_s = net.storage.at[nombre_de_foyers + 1, 'max_p_mw']
capacite = net.storage.at[nombre_de_foyers + 1, 'max_e_mwh']

for timestep in range(0, len(timesteps)):
    for batterie in range(0, nombre_de_foyers):
        liste_soc[batterie] = net.storage.at[nombre_de_foyers + batterie, 'soc_percent']

    tab_soc = np.asarray(liste_soc)
    list_load_timestep = []

    for load in range(0, nombre_de_foyers):
        list_load_timestep.append(puissances_loads[load][timestep])

    tableau_load_timestep = np.asarray(list_load_timestep)
    index_trier = tableau_load_timestep.argsort()
    lowest_demand = index_trier[0]  # c'est le smart grid ayant la demande la plus faible
    don = 0.1 * tab_soc[lowest_demand]
    tab_soc[lowest_demand] -= don
    n_donne[lowest_demand] += 1

    for load in range(0, nombre_de_foyers):

        if load != lowest_demand:
            tab_soc[load] += don / (nombre_de_foyers - 1)  # on donne 1/N de l'énergie donnée par le min demande
            n_recoit[load] += 1

    for composant in range(0, nombre_de_foyers):  # calcul de la quantité d'énergie que recoit chaque batterie
        net.storage.at[nombre_de_foyers + composant, 'soc_percent'] = tab_soc[composant]

    # On actualise ensuite les socs après avoir fait les opérations de transfert entre batteries
    for composant in range(0, nombre_de_foyers):
        soc = net.storage.at[nombre_de_foyers + composant, 'soc_percent']
        surplu = puissances_pvs[composant][timestep] - puissances_loads[composant][
            timestep]  # surplu de puissance
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
        liste_taux_var[composant].append(soc_mod - liste_soc[composant])

liste_taux_var = np.array(liste_taux_var)
tab_taux_var = np.add(tab_taux_var, liste_taux_var)

tab_n_donne += np.asarray(n_donne)
tab_n_recoit += np.asarray(n_recoit)

moyenne_coupure += nbr_coupure
moyenne_nrj += energie_perdue

# for k in range(0, nombre_de_foyers):
#     tab_n_donne[k] = tab_n_donne[k] / nombre_simu
#     tab_n_recoit[k] = tab_n_recoit[
#                           k] / nombre_simu  # Tableaux des nbr de dons, donations par batteries en moyenne

moyenne_coupure = moyenne_coupure / nombre_simu
moyenne_nrj = moyenne_nrj / nombre_simu

# tab_taux_var = tab_taux_var / nombre_simu
#
# liste_taux_pos, liste_taux_neg = [], []
# for batterie in range(0, nombre_de_foyers):
#     liste_taux_pos.append([])
#     liste_taux_neg.append([])
#     for tps in range(0, len(timesteps)):
#         if tab_taux_var[batterie][tps] >= 0:
#             liste_taux_pos[batterie].append(tab_taux_var[batterie][tps])
#         if tab_taux_var[batterie][tps] < 0:
#             liste_taux_neg[batterie].append(tab_taux_var[batterie][tps])
#
# print(liste_taux_pos)
# print(liste_taux_neg)
# print(sum(liste_taux_pos[0]), sum(liste_taux_neg[0]))

moyenne_soc += mo_var_ecartype(liste_soc_temps)[0]
for nano in range(0, nombre_de_foyers):  # Retourne le soc moyen de tous les nano-grids
    moyenne_std += mo_var_ecartype(liste_soc_temps[nano])[2]
#
# moyenne_std = moyenne_std / nombre_de_foyers
#
# moyenne_coupure = moyenne_coupure / nombre_simu
# moyenne_nrj = moyenne_nrj / nombre_simu
# moyenne_soc = moyenne_soc / nombre_simu
# moyenne_std = moyenne_std / nombre_simu
#
# liste_coupure_moyenne.append(moyenne_coupure)
# liste_energie_perdue.append(moyenne_nrj)
# liste_moyenne_soc.append(moyenne_soc)
# liste_moyenne_std.append(moyenne_std)

liste_temps = [k for k in range(len(extraction_donnee()[0]))]

colors = ['blue', 'green', 'red', 'orange', 'grey', 'cyan', 'black', 'purple', 'blue', 'green', 'red',
          'orange', 'grey', 'cyan', 'black', 'purple']
line_styles = ['-', '--', ':', 'o']
#
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

for pv in range(0, len(puissances_pvs)):
    for tps in range(0, len(puissances_pvs[0])):
        puissances_pvs[pv][tps] = 1000 * puissances_pvs[pv][tps]
        puissances_loads[pv][tps] = 1000 * puissances_loads[pv][tps]

# for composant in range(0, nombre_de_foyers):
#
#     plt.subplot(2, 1, 1)
#     plt.plot(liste_temps, puissances_pvs[composant], label='PV ' + str(composant), color=colors[composant],
#              linestyle=line_styles[0])
#     plt.xlabel('Temps (en h)')
#     plt.ylabel('Puissance RR1 (kW)')
#     plt.legend(loc='upper left', prop={'size': 8})
#
#     plt.subplot(2, 1, 2)
#     plt.plot(liste_temps, liste_soc_temps[composant], label='SOC ' + str(composant), color=colors[composant],
#              linestyle=line_styles[0])
#     plt.xlabel('Temps (en h)')
#     plt.ylabel('SOC (en %)')
#     plt.legend(loc='upper left', prop={'size': 8})
#
#
# plt.show()

for composant in range(0, nombre_de_foyers):

    ax1 = plt.subplot(3, 1, 1)
    ax1.plot(liste_temps, extraction_donnee()[0], label='PV ' + str(composant), color=colors[composant],
             linestyle=line_styles[0])
    plt.xlabel('Temps (en j)')
    plt.ylabel('Puissance LD (kW)')
    plt.legend(loc='upper left', prop={'size': 8})

    lst_position = np.arange(144, len(extraction_donnee()[0]) + 144, 144)
    l_xlabel = np.arange(1, 32)

    ax1.set_xticks(lst_position, l_xlabel)

    ax2 = plt.subplot(3, 1, 2)
    ax2.plot(liste_temps, puissances_loads[composant], label='Charge ' + str(composant), color=colors[composant],
             linestyle=line_styles[1])
    plt.xlabel('Temps (en j)')
    plt.ylabel('Puissance (kW)')
    plt.legend(loc='upper left', prop={'size': 8})

    ax2.set_xticks(lst_position, l_xlabel)

    ax3 = plt.subplot(3, 1, 3)
    ax3.plot(liste_temps, liste_soc_temps[composant], label='SOC ' + str(composant), color=colors[composant],
             linestyle=line_styles[0])
    plt.xlabel('Temps (en j)')
    plt.ylabel('SOC (en %)')
    plt.legend(loc='upper left', prop={'size': 8})

    ax3.set_xticks(lst_position, l_xlabel)

plt.show()