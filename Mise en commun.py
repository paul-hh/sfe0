# HENON-HILAIRE PAUL
# Mars 2023

# Code python regroupant les algorithmes RR1, RR2, WRR, Least Demand, Weighted Least demand. Ce code cherche à comparer
# les algorithmes avec les différents critères de mesures : énergie perdue, nombre de coupures, moyenne et variance des
# socs et le nombre de sollicitations de chaque batterie.

import pandapower as pp
import numpy as np
import random
from random import *
import matplotlib.pyplot as plt
from tqdm import tqdm

# Import des fonctions :


def list_gaussienne(amplitude, centre, ecart_type, t):
    x = t.copy()
    y = x.copy()
    for k in range(len(x)):
        y[k] = amplitude * np.exp(-(x[k] - centre)**2 / (2 * ecart_type**2)) + (random() / 10) * amplitude
    return y


def list_charges(mini, list_temps, num_charge):
    charge = []
    for temps in range(0, len(list_temps)):
        charge.append(np.random.uniform(mini, net.load.at[num_charge, 'p_mw']))
    return charge


def attribution_poids(etat_charge):
    if etat_charge <= 25:
        return 0.015
    if 25 < etat_charge <= 50:
        return 0.1
    if 50 < etat_charge <= 75:
        return 0.285
    if etat_charge > 75:
        return 0.6


def mo_var_ecartype(liste):
    return np.average(liste), np.var(liste), np.std(liste)


def correlation(liste1, liste2):
    coeff = np.corrcoef(liste1, liste2)[0][1]
    return coeff


nombre_de_foyers = 4  # chaque foyer dispose de sa batterie et son PV et les batteries sont reliées entre elles.


liste_moyenne_soc_RR1 = []
liste_moyenne_soc_RR2 = []
liste_moyenne_soc_WRR = []
liste_moyenne_soc_LD = []
liste_moyenne_soc_WLD = []

liste_ecart_soc_RR1 = []
liste_ecart_soc_RR2 = []
liste_ecart_soc_WRR = []
liste_ecart_soc_LD = []
liste_ecart_soc_WLD = []

liste_corr_pv_soc_RR1 = []
liste_corr_pv_soc_RR2 = []
liste_corr_pv_soc_WRR = []
liste_corr_pv_soc_LD = []
liste_corr_pv_soc_WLD = []

liste_corr_load_soc_RR1 = []
liste_corr_load_soc_RR2 = []
liste_corr_load_soc_WRR = []
liste_corr_load_soc_LD = []
liste_corr_load_soc_WLD = []


for batterie in range(0, nombre_de_foyers):

    liste_moyenne_soc_RR1.append([])
    liste_moyenne_soc_RR2.append([])
    liste_moyenne_soc_WRR.append([])
    liste_moyenne_soc_LD.append([])
    liste_moyenne_soc_WLD.append([])

    liste_ecart_soc_RR1.append([])
    liste_ecart_soc_RR2.append([])
    liste_ecart_soc_WRR.append([])
    liste_ecart_soc_LD.append([])
    liste_ecart_soc_WLD.append([])

    liste_corr_pv_soc_RR1.append([])
    liste_corr_pv_soc_RR2.append([])
    liste_corr_pv_soc_WRR.append([])
    liste_corr_pv_soc_LD.append([])
    liste_corr_pv_soc_WLD.append([])

    liste_corr_load_soc_RR1.append([])
    liste_corr_load_soc_RR2.append([])
    liste_corr_load_soc_WRR.append([])
    liste_corr_load_soc_LD.append([])
    liste_corr_load_soc_WLD.append([])


for time in tqdm(range(0, 1000)):
    # Création d'un set up commun (soc initiaux = 50%, même PVs, même loads, même nbr de batteries) :

    net = pp.create_empty_network()

    # Critères de comparaison :
    energie_perdue = 0
    nbr_coupure = 0

    # Création des temporalitées :
    Temps = 24 * 3600  # (en s)
    dt = (1/6) * 3600  # (pas de temps en s)
    nbr_pas_temps = int(Temps / dt)
    timesteps = [k for k in range(0, nbr_pas_temps)]

    # Création des bus : # Numérotés de [0, nombre_de_foyers - 1] = pvs, puis les batteries et ensuite les charges.
    bus = []
    for buses in range(0, 3 * nombre_de_foyers):
        bus.append(pp.create_bus(net, vn_kv=0.4, name='bus' + str(buses)))

    # Création des composants :
    pvs = []
    batteries = []
    charges = []

    for composants in range(0, nombre_de_foyers):

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
    mini_charge = 0  # minimum de charge
    list_soc_ini = [net.storage.at[nombre_de_foyers, 'soc_percent'] for k in range(0, nombre_de_foyers)]

    for pv in range(0, nombre_de_foyers):
        # tirage = random()
        # if tirage >= 0.5:
        #     decalage = - 4 * tirage
        # else:
        #     decalage = 4 * (1 - tirage)
        puissances_pvs.append(list_gaussienne(net.sgen.at[pv, 'p_mw'], len(timesteps) / 2, len(timesteps) / 5,
                                              timesteps))
        puissances_loads.append(list_charges(mini_charge, timesteps, 2 * nombre_de_foyers + pv))

    p_max_e = net.storage.at[nombre_de_foyers + 1, 'min_p_mw']
    p_max_s = net.storage.at[nombre_de_foyers + 1, 'max_p_mw']
    capacite = net.storage.at[nombre_de_foyers + 1, 'max_e_mwh']

    # ALGO 1 : ROUND ROBIN 1

    nbr_coupures_RR1 = 0
    energie_perdue_RR1 = 0
    nbr_solicitations_RR1 = [[0] for k in range(0, nombre_de_foyers)]
    nbr_solicité_RR1 = [[0] for k in range(0, nombre_de_foyers)]
    liste_soc_RR1 = list_soc_ini
    liste_soc_temps_RR1 = [[net.storage.at[nombre_de_foyers, 'soc_percent']] for k in range(0, nombre_de_foyers)]

    for timestep in range(0, len(timesteps)):  # boucle de temps (timestep = 10min)
        compteur = 0
        for batterie in range(0, nombre_de_foyers):
            liste_soc_RR1[batterie] = net.storage.at[nombre_de_foyers + batterie, 'soc_percent']
        tab_soc = np.asarray(liste_soc_RR1)  # on convertit notre liste de soc en tableau numpy
        index_trier = tab_soc.argsort()  # renvoie la liste des indices dans l'ordre des socs
        index_max = index_trier[nombre_de_foyers - 1]  # renvoie l'indice de la batterie ayant le SOC maximum
        i_receveur = index_trier[compteur]  # indice de la batterie qui recoit
        if compteur == 0:
            i_donneur = index_max
        if compteur == nombre_de_foyers - 1:
            compteur = 0
        else:
            i_receveur = index_trier[compteur]
            tab_soc[i_receveur] += 0.1 * tab_soc[i_donneur]  # la batterie donne 20% de son SOC à celle qui recoit
            tab_soc[i_donneur] -= 0.1 * tab_soc[i_donneur]
            compteur += 1
        for batterie in range(0, nombre_de_foyers):
            net.storage.at[nombre_de_foyers + batterie, 'soc_percent'] = tab_soc[batterie]
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
            liste_soc_temps_RR1[composant].append(soc_mod)

    for batterie in range(0, nombre_de_foyers):   # On enlève le dernier calcul de soc pour avoir des listes de mm dim
        liste_soc_temps_RR1[batterie].pop()
        liste_corr_pv_soc_RR1[batterie].append(correlation(puissances_pvs[batterie], liste_soc_temps_RR1[batterie]))
        liste_corr_load_soc_RR1[batterie].append(correlation(puissances_loads[batterie], liste_soc_temps_RR1[batterie]))
        liste_moyenne_soc_RR1[batterie].append(mo_var_ecartype(liste_soc_temps_RR1[batterie])[0])
        liste_ecart_soc_RR1[batterie].append(mo_var_ecartype(liste_soc_temps_RR1[batterie])[2])

    # ALGO 2 : ROUND ROBIN 2

    nbr_coupures_RR2 = 0
    energie_perdue_RR2 = 0
    nbr_solicitations_RR2 = [[0] for k in range(0, nombre_de_foyers)]
    nbr_solicité_RR2 = [[0] for k in range(0, nombre_de_foyers)]
    liste_soc_RR2 = list_soc_ini
    liste_soc_temps_RR2 = [[net.storage.at[nombre_de_foyers, 'soc_percent']] for k in range(0, nombre_de_foyers)]

    liste_des_index = []
    for timestep in range(0, len(timesteps)):  # boucle de temps (timestep = 10min)
        for batterie in range(0, nombre_de_foyers):
            liste_soc_RR2[batterie] = net.storage.at[nombre_de_foyers + batterie, 'soc_percent']
        tab_soc = np.asarray(liste_soc_RR2)
        index_trier = tab_soc.argsort()  # renvoie la liste des indices dans l'ordre des socs
        index_max = index_trier[nombre_de_foyers - 1]
        if len(liste_des_index) == nombre_de_foyers:
            liste_des_index = []
        compt = 2
        while index_max in liste_des_index:
            index_max = index_trier[nombre_de_foyers - compt]
            compt += 1
        index_min = index_trier[0]
        if index_max != index_min:
            liste_des_index.append(index_max)
            min_soc = liste_soc_RR2[index_trier[index_min]]
            max_soc = liste_soc_RR2[index_trier[index_max]]
            liste_soc_RR2[index_trier[index_min]] += 0.1 * liste_soc_RR2[index_trier[index_max]]
            liste_soc_RR2[index_trier[index_max]] -= 0.1 * liste_soc_RR2[index_trier[index_max]]
        for batterie in range(0, nombre_de_foyers):
            net.storage.at[nombre_de_foyers + batterie, 'soc_percent'] = liste_soc_RR2[batterie]
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
            liste_soc_temps_RR2[composant].append(soc_mod)

    for batterie in range(0, nombre_de_foyers):  # On enlève le dernier calcul de soc pour avoir des listes de mm dim
        liste_soc_temps_RR2[batterie].pop()
        liste_corr_pv_soc_RR2[batterie].append(correlation(puissances_pvs[batterie], liste_soc_temps_RR2[batterie]))
        liste_corr_load_soc_RR2[batterie].append(correlation(puissances_loads[batterie], liste_soc_temps_RR2[batterie]))
        liste_moyenne_soc_RR2[batterie].append(mo_var_ecartype(liste_soc_temps_RR2[batterie])[0])
        liste_ecart_soc_RR2[batterie].append(mo_var_ecartype(liste_soc_temps_RR2[batterie])[2])

    # ALGO 3 : Weighted Round Robin

    nbr_coupures_WRR = 0
    energie_perdue_WRR = 0
    nbr_solicitations_WRR = [[0] for k in range(0, nombre_de_foyers)]  # inutile car à chaque tour on sollicite tt les batt
    nbr_solicité_WRR = [[0] for k in range(0, nombre_de_foyers)]
    liste_soc_WRR = list_soc_ini
    liste_soc_temps_WRR = [[net.storage.at[nombre_de_foyers, 'soc_percent']] for k in range(0, nombre_de_foyers)]

    for timestep in range(0, len(timesteps)):
        pot_commun = 0
        for composant in range(0, nombre_de_foyers):  # calcul de la quantité d'énergie que donne chaque batterie
            soc = net.storage.at[nombre_de_foyers + composant, 'soc_percent']  # accès SOC des batteries via Pandapower
            poids = attribution_poids(soc)
            dont = poids * (soc / 2) / 100 * capacite  # énergie donnée
            pot_commun += dont
            net.storage.at[nombre_de_foyers + composant, 'soc_percent'] -= dont * 100 / capacite
        for composant in range(0, nombre_de_foyers):  # calcul de la quantité d'énergie que recoit chaque batterie
            net.storage.at[
                nombre_de_foyers + composant, 'soc_percent'] += pot_commun * 100 / capacite / nombre_de_foyers
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
            liste_soc_temps_WRR[composant].append(soc_mod)

    for batterie in range(0, nombre_de_foyers):  # On enlève le dernier calcul de soc pour avoir des listes de mm dim
        liste_soc_temps_WRR[batterie].pop()
        liste_corr_pv_soc_WRR[batterie].append(correlation(puissances_pvs[batterie], liste_soc_temps_WRR[batterie]))
        liste_corr_load_soc_WRR[batterie].append(correlation(puissances_loads[batterie], liste_soc_temps_WRR[batterie]))
        liste_moyenne_soc_WRR[batterie].append(mo_var_ecartype(liste_soc_temps_WRR[batterie])[0])
        liste_ecart_soc_WRR[batterie].append(mo_var_ecartype(liste_soc_temps_WRR[batterie])[2])

    # ALGO 4 : Least Demand

    nbr_coupures_LD = 0
    energie_perdue_LD = 0
    nbr_solicitations_LD = [[0] for k in range(0, nombre_de_foyers)]
    nbr_solicité_LD = [[0] for k in range(0, nombre_de_foyers)]
    liste_soc_LD = list_soc_ini
    liste_soc_temps_LD = [[net.storage.at[nombre_de_foyers, 'soc_percent']] for k in range(0, nombre_de_foyers)]

    for timestep in range(0, len(timesteps)):
        for batterie in range(0, nombre_de_foyers):
            liste_soc_LD[batterie] = net.storage.at[nombre_de_foyers + batterie, 'soc_percent']
        tab_soc = np.asarray(liste_soc_LD)
        list_load_timestep = []
        for load in range(0, nombre_de_foyers):
            list_load_timestep.append(puissances_loads[load][timestep])
            tableau_load_timestep = np.asarray(list_load_timestep)
            index_trier = tableau_load_timestep.argsort()
            lowest_demand = index_trier[0]  # c'est le smart grid ayant la demande la plus faible
            don = 0.1 * tab_soc[lowest_demand]
            tab_soc[lowest_demand] -= don
            if load != lowest_demand:
                tab_soc[load] += don / (nombre_de_foyers - 1)  # on donne 1/N de l'énergie donnée par le min demande
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
            liste_soc_temps_LD[composant].append(soc_mod)

    for batterie in range(0, nombre_de_foyers):  # On enlève le dernier calcul de soc pour avoir des listes de mm dim
        liste_soc_temps_LD[batterie].pop()
        liste_corr_pv_soc_LD[batterie].append(correlation(puissances_pvs[batterie], liste_soc_temps_LD[batterie]))
        liste_corr_load_soc_LD[batterie].append(correlation(puissances_loads[batterie], liste_soc_temps_LD[batterie]))
        liste_moyenne_soc_LD[batterie].append(mo_var_ecartype(liste_soc_temps_LD[batterie])[0])
        liste_ecart_soc_LD[batterie].append(mo_var_ecartype(liste_soc_temps_LD[batterie])[2])

    # ALGO 5 : Weighted Least Demand

    nbr_coupures_WLD = 0
    energie_perdue_WLD = 0
    nbr_solicitations_WLD = [[0] for k in range(0, nombre_de_foyers)]
    nbr_solicité_WLD = [[0] for k in range(0, nombre_de_foyers)]
    liste_soc_WLD = list_soc_ini
    liste_soc_temps_WLD = [[net.storage.at[nombre_de_foyers, 'soc_percent']] for k in range(0, nombre_de_foyers)]

    for timestep in range(0, len(timesteps)):
        for batterie in range(0, nombre_de_foyers):
            liste_soc_WLD[batterie] = net.storage.at[nombre_de_foyers + batterie, 'soc_percent']
        tab_soc = np.asarray(liste_soc_WLD)
        list_load_timestep = []
        poids = []
        somme_soc = sum(tab_soc)
        for load in range(0, nombre_de_foyers):
            list_load_timestep.append(puissances_loads[load][timestep])
        tableau_load_timestep = np.asarray(list_load_timestep)
        index_trier = tableau_load_timestep.argsort()
        lowest_demand = index_trier[0]  # c'est le smart grid ayant la demande la plus faible
        somme_soc -= tab_soc[lowest_demand]
        dont = 0.1 * tab_soc[lowest_demand]
        for load in range(0, nombre_de_foyers):
            if load != lowest_demand:
                poids = tab_soc[load] / (somme_soc + 0.000000001)
                tab_soc[load] += dont * poids  # on donne l'énergie en fonction du poids
        tab_soc[lowest_demand] -= dont
        for composant in range(0, nombre_de_foyers):  # calcul de la quantité d'énergie que recoit chaque batterie
            net.storage.at[nombre_de_foyers + composant, 'soc_percent'] = tab_soc[composant]
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
            liste_soc_temps_WLD[composant].append(soc_mod)

    for batterie in range(0, nombre_de_foyers):  # On enlève le dernier calcul de soc pour avoir des listes de mm dim
        liste_soc_temps_WLD[batterie].pop()
        liste_corr_pv_soc_WLD[batterie].append(correlation(puissances_pvs[batterie], liste_soc_temps_WLD[batterie]))
        liste_corr_load_soc_WLD[batterie].append(correlation(puissances_loads[batterie], liste_soc_temps_WLD[batterie]))
        liste_moyenne_soc_WLD[batterie].append(mo_var_ecartype(liste_soc_temps_WLD[batterie])[0])
        liste_ecart_soc_WLD[batterie].append(mo_var_ecartype(liste_soc_temps_WLD[batterie])[2])

    #  Plots :

    # abscisse = ['Round Robin 1', 'Round Robin 2', 'Weighted Round Robin', 'Least Demand', 'Weighted Least Demand']
    # plt.subplot(3, 1, 1)
    # plt.bar(abscisse, [moyenne_soc_RR1[0], moyenne_soc_RR2[0], moyenne_soc_WRR[0], moyenne_soc_LD[0],
    # moyenne_soc_WLD[0]],
    #         color='orange')
    # plt.xlabel("Algorithme")
    # plt.ylabel("Moyenne SOC (%)")
    #
    # plt.subplot(3, 1, 2)
    # plt.bar(abscisse, [moyenne_soc_RR1[1], moyenne_soc_RR2[1], moyenne_soc_WRR[1], moyenne_soc_LD[1],
    # moyenne_soc_WLD[1]],
    #         color='green')
    # plt.xlabel("Algorithme")
    # plt.ylabel("Variance")
    #
    # plt.subplot(3, 1, 3)
    # plt.bar(abscisse, [moyenne_soc_RR1[2], moyenne_soc_RR2[2], moyenne_soc_WRR[2], moyenne_soc_LD[2],
    # moyenne_soc_WLD[2]],
    #         color='blue')
    # plt.xlabel("Algorithme")
    # plt.ylabel("Ecart-type")
    #
    # batterie = ['batterie 1', 'batterie 2', 'batterie 3', 'batterie 4']
    #
    # plt.show()
    #
    # # correlation pv / soc
    # plt.subplot(3, 1, 1)
    # plt.bar(batterie, corr_pv_soc_RR1, color='green')
    # plt.ylabel("Round Robin 1")
    # plt.title('Coefficient de corrélation entre le PV et les SOC')
    #
    # plt.subplot(3, 1, 2)
    # plt.bar(batterie, corr_pv_soc_RR2, color='blue')
    # plt.ylabel("Round Robin 2")
    #
    # plt.subplot(3, 1, 3)
    # plt.bar(batterie, corr_pv_soc_WRR, color='orange')
    # plt.ylabel("Weighted RR")
    #
    # plt.show()
    #
    # plt.subplot(2, 1, 1)
    # plt.bar(batterie, corr_pv_soc_LD, color='grey')
    # plt.ylabel("Least demand")
    # plt.title('Coefficient de corrélation entre le PV et les SOC')
    #
    # plt.subplot(2, 1, 2)
    # plt.bar(batterie, corr_pv_soc_WLD, color='black')
    # plt.ylabel("Weighted Least demand")
    #
    # plt.show()
    # # correlation load / soc
    #
    # plt.subplot(3, 1, 1)
    # plt.bar(batterie, corr_load_soc_RR1, color='green')
    # plt.ylabel("Round Robin 1")
    # plt.title('Coefficient de corrélation entre les Loads et les SOC')
    #
    # plt.subplot(3, 1, 2)
    # plt.bar(batterie, corr_load_soc_RR2, color='blue')
    # plt.ylabel("Round Robin 2")
    #
    # plt.subplot(3, 1, 3)
    # plt.bar(batterie, corr_load_soc_WRR, color='orange')
    # plt.ylabel("Weighted RR")
    #
    # plt.show()
    #
    # plt.subplot(2, 1, 1)
    # plt.bar(batterie, corr_load_soc_LD, color='grey')
    # plt.ylabel("Least demand")
    # plt.title('Coefficient de corrélation entre les Loads et les SOC')
    #
    # plt.subplot(2, 1, 2)
    # plt.bar(batterie, corr_load_soc_WLD, color='black')
    # plt.ylabel("Weighted Least demand")
    #
    # plt.show()

# Calcul de la moyenne de la moyenne des socs

for batterie in range(0, nombre_de_foyers):
    liste_moyenne_soc_RR1[batterie] = np.average(liste_moyenne_soc_RR1[batterie])
    liste_moyenne_soc_RR2[batterie] = np.average(liste_moyenne_soc_RR2[batterie])
    liste_moyenne_soc_WRR[batterie] = np.average(liste_moyenne_soc_WRR[batterie])
    liste_moyenne_soc_LD[batterie] = np.average(liste_moyenne_soc_LD[batterie])
    liste_moyenne_soc_WLD[batterie] = np.average(liste_moyenne_soc_WLD[batterie])

# Calcul de la moyenne des ecarts-types de soc

    liste_ecart_soc_RR1[batterie] = np.average(liste_ecart_soc_RR1[batterie])
    liste_ecart_soc_RR2[batterie] = np.average(liste_ecart_soc_RR2[batterie])
    liste_ecart_soc_WRR[batterie] = np.average(liste_ecart_soc_WRR[batterie])
    liste_ecart_soc_LD[batterie] = np.average(liste_ecart_soc_LD[batterie])
    liste_ecart_soc_WLD[batterie] = np.average(liste_ecart_soc_WLD[batterie])

# Calcul de la moyenne de correlation pv/soc

    liste_corr_pv_soc_RR1[batterie] = np.average(liste_corr_pv_soc_RR1[batterie])
    liste_corr_pv_soc_RR2[batterie] = np.average(liste_corr_pv_soc_RR2[batterie])
    liste_corr_pv_soc_WRR[batterie] = np.average(liste_corr_pv_soc_WRR[batterie])
    liste_corr_pv_soc_LD[batterie] = np.average(liste_corr_pv_soc_LD[batterie])
    liste_corr_pv_soc_WLD[batterie] = np.average(liste_corr_pv_soc_WLD[batterie])


# Calcul de la moyenne de correlation load/soc

    liste_corr_load_soc_RR1[batterie] = np.average(liste_corr_load_soc_RR1[batterie])
    liste_corr_load_soc_RR2[batterie] = np.average(liste_corr_load_soc_RR2[batterie])
    liste_corr_load_soc_WRR[batterie] = np.average(liste_corr_load_soc_WRR[batterie])
    liste_corr_load_soc_LD[batterie] = np.average(liste_corr_load_soc_LD[batterie])
    liste_corr_load_soc_WLD[batterie] = np.average(liste_corr_load_soc_WLD[batterie])

abscisse = ['Round Robin 1', 'Round Robin 2', 'Weighted Round Robin', 'Least Demand', 'Weighted Least Demand']
plt.subplot(2, 1, 1)
plt.bar(abscisse, [liste_moyenne_soc_RR1[0], liste_moyenne_soc_RR2[0], liste_moyenne_soc_WRR[0], liste_moyenne_soc_LD[0]
        , liste_moyenne_soc_WLD[0]], color='orange')
plt.xlabel("Algorithme")
plt.ylabel("Moyenne SOC (%)")


plt.subplot(2, 1, 2)
plt.bar(abscisse, [liste_ecart_soc_RR1[0], liste_ecart_soc_RR2[0], liste_ecart_soc_WRR[0],
                   liste_ecart_soc_LD[0], liste_ecart_soc_WLD[0]], color='blue')
plt.xlabel("Algorithme")
plt.ylabel("Ecart-type")

batterie = ['batterie 1', 'batterie 2', 'batterie 3', 'batterie 4']

plt.show()

# correlation pv / soc
plt.subplot(3, 1, 1)
plt.bar(batterie, liste_corr_pv_soc_RR1, color='green')
plt.ylabel("Round Robin 1")
plt.title('Coefficient de corrélation entre le PV et les SOC')

plt.subplot(3, 1, 2)
plt.bar(batterie, liste_corr_pv_soc_RR2, color='blue')
plt.ylabel("Round Robin 2")

plt.subplot(3, 1, 3)
plt.bar(batterie, liste_corr_pv_soc_WRR, color='orange')
plt.ylabel("Weighted RR")

plt.show()

plt.subplot(2, 1, 1)
plt.bar(batterie, liste_corr_pv_soc_LD, color='grey')
plt.ylabel("Least demand")
plt.title('Coefficient de corrélation entre le PV et les SOC')

plt.subplot(2, 1, 2)
plt.bar(batterie, liste_corr_pv_soc_WLD, color='black')
plt.ylabel("Weighted Least demand")

plt.show()
# correlation load / soc

plt.subplot(3, 1, 1)
plt.bar(batterie, liste_corr_load_soc_RR1, color='green')
plt.ylabel("Round Robin 1")
plt.title('Coefficient de corrélation entre les Loads et les SOC')

plt.subplot(3, 1, 2)
plt.bar(batterie, liste_corr_load_soc_RR2, color='blue')
plt.ylabel("Round Robin 2")

plt.subplot(3, 1, 3)
plt.bar(batterie, liste_corr_load_soc_WRR, color='orange')
plt.ylabel("Weighted RR")

plt.show()

plt.subplot(2, 1, 1)
plt.bar(batterie, liste_corr_load_soc_LD, color='grey')
plt.ylabel("Least demand")
plt.title('Coefficient de corrélation entre les Loads et les SOC')

plt.subplot(2, 1, 2)
plt.bar(batterie, liste_corr_load_soc_WLD, color='black')
plt.ylabel("Weighted Least demand")

plt.show()

