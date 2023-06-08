# HENON-HILAIRE PAUL
# Avril 2023

# Code python d'optimisation générale des paramètres du système. Les paramètres sont alpha_i : puissance du PV vers
# sa batterie si >0 et puissance de la batterie vers sa demande si <0. (1 - alpha_i) la puissance du PV vers sa demande
# et gamma_ij la puissance de la batterie i vers la batterie j. On nota les alpha_i : a_i et gamma_ij : g_ij


# Importation des librairies :

import pandapower as pp
import numpy as np
import itertools
import random
from random import *
import matplotlib.pyplot as plt
from tqdm import tqdm

# Importation des fonctions utiles :


def list_gaussienne(amplitude, centre, ecart_type, t):
    x = t.copy()
    y = x.copy()
    for k in range(len(x)):
        y[k] = amplitude * np.exp(-(x[k] - centre)**2 / (2 * ecart_type**2)) + (random() / 10) * amplitude
    return y


# Création des temporalitées :

Temps = 24 * 3600  # (en s)
dt = 12 * 3600  # (pas de temps en s, ici 10min)
nbr_pas_temps = int(Temps / dt)
timesteps = [k for k in range(0, nbr_pas_temps)]

# Pas des paramètres :

n_para = 2  # nombre de différentes valeurs pouvant prendre les paramèteres

# Paramètres de simulation :

nombre_nanos_grid = 3

# Initialisation des paramètres du système :

#  Matrice temporelle des paramètres :  [ [a_0 ,  0  , ..., ... , ... ,  0 ]      taille : (n * n * T )
#                                         [g_01, a_1 , 0  , ... , ... ,  0 ]
#                                         [g_02, g_12, a_2, 0  ,  ... ,  0 ]
#                                         [           ...         0        ]
#                                         [           ...               0  ]
#                                         [           ...                  ]
#                                         [g_0n, g1n , ..., ... ,g_nn-1,a_n] ]


nombre_parametres = int(nombre_nanos_grid + (nombre_nanos_grid * (nombre_nanos_grid - 1)) / 2) * nbr_pas_temps
matrice_parametres = np.zeros((nombre_nanos_grid, nombre_nanos_grid, len(timesteps)))


# Creation des PVs, batteries et demandes :

net = pp.create_empty_network()

# Création des bus, , numerotés de [0, nombre_de_foyers - 1] = pvs, puis les batteries et ensuite les charges :

bus = []
for buses in range(0, 3 * nombre_nanos_grid):
    bus.append(pp.create_bus(net, vn_kv=0.4, name='bus' + str(buses)))

# Création des composants :

pvs = []
batteries = []
charges = []

for composants in range(nombre_nanos_grid):

    pvs.append(pp.create_sgen(net, bus=bus[composants], p_mw=3.00, index=composants, q_mvar=0, type='PV', slack=True))

    batteries.append(pp.create_storage(net, bus=bus[nombre_nanos_grid + composants], p_mw=0.00,
                                       index=nombre_nanos_grid + composants, min_p_mw=6.4, max_p_mw=18,
                                       min_e_mwh=0, max_e_mwh=14.4, q_mvar=0, min_q_mvar=-0.1, max_q_mvar=0.1
                                       , soc_percent=50, controllable=True))

    charges.append(pp.create_load(net, bus=bus[2 * nombre_nanos_grid + composants], p_mw=3.5, index=2 *
                                  nombre_nanos_grid + composants, q_mvar=0.1))

# Creation des PVs, charges et socs :

puissances_pvs = []
puissances_loads = []
mini = 0  # minimum de charge
liste_soc = []  # liste des socs par batterie à un instant t
liste_soc_temps = []  # liste des socs par batterie dans le temps


def list_charges(minim, list_temps, num_charge):
    charge = []
    for tem in range(0, len(list_temps)):
        charge.append(np.random.uniform(minim, net.load.at[num_charge, 'p_mw']))
    return charge


for pv in range(0, nombre_nanos_grid):
    tirage = random()
    if tirage >= 0.5:
        decalage = - 4 * tirage
    else:
        decalage = 4 * (1 - tirage)

    puissances_pvs.append(list_gaussienne(net.sgen.at[pv, 'p_mw'], len(timesteps) / 2 + decalage, len(timesteps) / 6,
                                          timesteps))
    puissances_loads.append(list_charges(mini, timesteps, 2 * nombre_nanos_grid + pv))
    liste_soc.append(net.storage.at[nombre_nanos_grid + pv, 'soc_percent'])
    liste_soc_temps.append([])


p_max_e = net.storage.at[nombre_nanos_grid + 1, 'min_p_mw']
p_max_s = net.storage.at[nombre_nanos_grid + 1, 'max_p_mw']
capacite = net.storage.at[nombre_nanos_grid + 1, 'max_e_mwh']


# Boucle en brute force :


def convertisseur_parametre(para):
    """Convertie l'entier para en sa valeur de parametre comprise entre -1 et 1"""
    return -1 + (2 / (n_para - 1)) * para


# Exemple de matrice 3x3 dont chaque élément peut prendre 2 valeurs
valeurs_possibles = [k for k in range(0, n_para)]  # valeurs possibles pour chaque élément de la matrice

# Générer toutes les combinaisons possibles de valeurs pour chaque élément de la matrice
combinaisons = list(itertools.product(*([valeurs_possibles] * len(matrice_parametres[0][0]))))

# Liste contenant les matrices ayant la meilleure fonction d'optimisation :

liste_matrices = [1000, 1000]

# Afficher toutes les combinaisons possibles
for comb in tqdm(itertools.product(combinaisons, repeat=int(len(matrice_parametres) * (len(matrice_parametres) + 1) / 2))):
    matrice = list(comb)

    for k in range(0, len(matrice)):
        matrice[k] = list(matrice[k])

    # Complete la matrice pour faire une triangulaire inferieure :
    for elt in range(0, nombre_nanos_grid):
        c = 0
        for nbr in range(int(nombre_nanos_grid - elt - 1)):
            matrice.insert((nombre_nanos_grid + 1) * elt + c + 1, [0 for m in range(0, len(timesteps))])
            c += 1

    liste_aplatie = [element for sous_liste in matrice for element in sous_liste]
    matrice = np.reshape(matrice, (nombre_nanos_grid, nombre_nanos_grid, len(timesteps)))

    # On regarde si la matrice est compatible avec nos conditions
    flag1, flag2 = True, True

    for ligne in range(0, len(matrice)):
        for colonne in range(0, len(matrice)):
            if ligne >= colonne:
                for temps in range(0, len(timesteps)):
                    matrice[ligne][colonne][temps] = convertisseur_parametre(matrice[ligne][colonne][temps])

    for ligne in range(0, len(matrice)):
        for colonne in range(0, len(matrice)):
            if ligne >= colonne:
                for temps in range(0, len(timesteps)):
                    # Conditions :
                    valeur = matrice[ligne][colonne][temps]

                    if ligne == colonne:  # on regarde un alpha, il doit être du même signe que les gammas de sa colonne
                        for lignes in range(ligne + 1, nombre_nanos_grid):
                            if np.sign(matrice[lignes][colonne][temps]) != np.sign(valeur):
                                flag1 = False

                    if ligne != colonne:  # on regarde un gamma, il doit être du même signe que son
                        # alpha de colonne ie > 0
                        if np.sign(matrice[colonne][colonne][temps]) != np.sign(valeur):
                            flag2 = False
    if flag1 and flag2:
        # Calcul des SOCs et du nombre de coupures :

        tab_soc = np.zeros((nombre_nanos_grid, len(timesteps)))  # Tableaux des SOCs vide

        # Fonctions objectif :
        n_coupures = 0  # Caractérise le nombre de coupures de courant

        for temp in range(1, len(timesteps)):
            for nano in range(0, nombre_nanos_grid):

                alpha = matrice[nano][nano][temp]

                don_alpha = 0
                don_gamma = 0
                surplu = 0

                if np.sign(alpha) > 0:
                    beta = 1 - alpha
                    don_alpha = alpha * min(p_max_e, puissances_pvs[nano][temp]) * dt / 3600 / capacite * 100
                    surplu = puissances_pvs[nano][temp] * beta - puissances_loads[nano][temp]

                if np.sign(alpha) < 0:
                    beta = 1
                    don_alpha_neg = alpha * p_max_s * dt / 3600 / capacite * 100
                    surplu = puissances_pvs[nano][temp] * beta - puissances_loads[nano][temp] - p_max_s * alpha

                for ligne in range(nano, len(matrice)):
                    don_gamma += matrice[ligne][nano][temp] * p_max_s * dt / 3600 / capacite * 100

                tab_soc[temp] = tab_soc[temp - 1] + don_alpha + don_gamma

                if surplu < 0:
                    n_coupures += 1
        print(matrice, 'nombre de coupres = ' + str(n_coupures))
#         if n_coupures < liste_matrices[1]:
#             liste_matrices[0] == matrice
#             n_coupures = liste_matrices[1]
#
#         if n_coupures == liste_matrices[1]:
#             liste_matrices.append([matrice, n_coupures])
#
#
# print(liste_matrices)

