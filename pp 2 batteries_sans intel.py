import pandapower as pp
import numpy as np
import random
from random import *
import matplotlib.pyplot as plt

L_perdue = []
N_perdue = []

for k in range(0, 1000):
    net = pp.create_empty_network()
    n_perdue = 0
    # Création des bus :
    bus1 = pp.create_bus(net, vn_kv=0.4, name='Générateur')  # pour le générateur
    bus2 = pp.create_bus(net, vn_kv=0.4, name='Stockage1')  # pour le stockage1
    bus3 = pp.create_bus(net, vn_kv=0.4, name='Stockage2')  # pour la stockage 2
    bus4 = pp.create_bus(net, vn_kv=0.4, name='Charge1')  # pour la charge1
    bus5 = pp.create_bus(net, vn_kv=0.4, name='Charge2')  # pour la charge2

    # Création des composants
    pv1 = pp.create_sgen(net, bus=bus1, p_mw=0.020, index=1, q_mvar=0, type='PV', slack=True)
    pv2 = pp.create_sgen(net, bus=bus1, p_mw=0.020, index=2, q_mvar=0, type='PV', slack=True)

    storage1 = pp.create_storage(net, bus=bus2, p_mw=0.00, index=3, min_p_mw=-0.015, max_p_mw=0.015, min_e_mwh=0,
                                 max_e_mwh=0.00625, q_mvar=0, min_q_mvar=-0.1, max_q_mvar=0.1, soc_percent=50,
                                 controllable=True)
    storage2 = pp.create_storage(net, bus=bus3, p_mw=0.00, index=4, min_p_mw=-0.015, max_p_mw=0.015, min_e_mwh=0,
                                 max_e_mwh=0.00625, q_mvar=0, min_q_mvar=-0.1, max_q_mvar=0.1, soc_percent=50,
                                 controllable=True)

    load1 = pp.create_load(net, bus=bus4, p_mw=0.0125, index=5,  q_mvar=0.1)  # Ajouter une charge à la maison
    load2 = pp.create_load(net, bus=bus4, p_mw=0.0125, index=6,  q_mvar=0.1)


    def list_gaussienne(amplitude, centre, ecart_type, t):
        x = t.copy()
        y = x.copy()
        for k in range(len(x)):
            y[k] = amplitude * np.exp(-(x[k] - centre)**2 / (2 * ecart_type**2)) + (random() / 10) * amplitude
        return y


    # Initialiser les valeurs de la simulation :
    # ATTENTION : donner en minutes
    timesteps = [k for k in range(0, 24 * 4)]  # 24 heures avec des mises à jour toutes les 15 minutes
    time = 60 / (len(timesteps) / 24)  # temps d'une simulation en heure
    list_load1 = []
    list_load2 = []

    # Permet de créer un décalage entre les deux Gaussiennes :
    tirage = random()
    if tirage >= 0.5:
        decalage = - tirage
    else:
        decalage = 1 - tirage

    list_pv_power1 = list_gaussienne(net.sgen.at[1, 'p_mw'], len(timesteps) / 2, 20, timesteps)
    list_pv_power2 = list_gaussienne(net.sgen.at[2, 'p_mw'], decalage + len(timesteps) / 2, 15, timesteps)

    # Creation de la liste de temps :
    for k in range(0, len(timesteps)):
        list_load1.append(np.random.uniform(0.0001, net.load.at[5, 'p_mw']))
        list_load2.append(np.random.uniform(0.0001, net.load.at[6, 'p_mw']))

    soc1, soc2 = 80, 80
    list_soc1 = []  # État de charge initial de la batterie1
    list_soc2 = []  # État de charge initial de la batterie2

    p_max_bat1 = net.storage.at[3, 'max_p_mw']
    p_max_bat2 = net.storage.at[4, 'max_p_mw']
    p_max_bat = [p_max_bat1, p_max_bat2]

    capacite1 = net.storage.at[3, 'max_e_mwh']
    capacite2 = net.storage.at[4, 'max_e_mwh']
    capacite = [capacite1, capacite2]

    l_coast1, l_coast2 = [0 for k in range(len(timesteps))], [0 for k in range(len(timesteps))]  # liste des demandes non
    # satisfaites
    l_perdue = [0 for k in range(len(timesteps))]  # liste du total energetique perdue (lorsque un pv ne donne pas toute
    # son energie)

    ecart = 20  # écart de soc entre les batteries pour déclencher un transfert d'énergie

    def transfert_energie(soc1, soc2, pv_power1, pv_power2, load1, load2, cas, n_perdue):
        soc = [soc1, soc2]
        index_max = np.argmax(soc)
        index_min = np.argmin(soc)
        max_soc = max(soc1, soc2)
        min_soc = min(soc1, soc2)

        pv = [pv_power1, pv_power2]

        load = [load1, load2]

        surplus1 = pv_power1 - load1
        surplus2 = pv_power2 - load2

        soc1_mem = soc1
        soc2_mem = soc2

        if cas == 1:  # PV1 > load1 et PV2 > load2
            #print('cas' + str(1))
            soc1 = min(100, soc1 + ((surplus1 / time) / capacite1) * 100)
            soc2 = min(100, soc2 + ((surplus2 / time) / capacite2) * 100)
            if soc1 == 100:
                cout_puissance = (soc1_mem + (((surplus1 / time) / capacite1) * 100) - 100) * capacite2 * time / 100
                coast(- cout_puissance, 0, timestep)
            if soc2 == 100:
                cout_puissance = (soc2_mem + (((surplus2 / time) / capacite2) * 100) - 100) * capacite2 * time / 100
                coast(0, - cout_puissance, timestep)
            return soc1, soc2
        if cas == 2:  # PV1 > load1 et PV2 <= load2
            #print(' cas' + str(2))
            exces2 = p_max_bat2 - (load2 - pv_power2)
            soc1 = min(100, soc1 + (surplus1 / time / capacite1) * 100)
            soc2 = max(0, soc2 + ((load2 - pv_power2) / time / capacite2) * 100)
            if soc1 == 100:  # Si B2 à charger B1 à 100% on perd de l'énergie
                cout_puissance = (soc1_mem + (((surplus1 / time) / capacite1) * 100) - 100) * capacite1 * time / 100
                coast(- cout_puissance, 0, timestep)
            if soc2 == 0:
                 cout_puissance = soc2_mem - (((load2 - pv_power2) / capacite2 / time) * 100)
                 coast(0, cout_puissance)
            return soc1, soc2
        if cas == 3:  # PV1 <= load1 et PV2 > load 2
            #print(' cas' + str(3))
            exces1 = p_max_bat1 - (load1 - pv_power1)  # Puissance restante à B1
            soc2 = min(100, soc2 + (surplus2 / time / capacite2) * 100)
            soc1 = max(0, ((load1 - pv_power1) / time / capacite1) * 100)
            if soc2 == 100:  # Si B2 à charger B1 à 100% on perd de l'énergie
                cout_puissance = (soc2_mem + (((surplus2 / time) / capacite2) * 100) - 100) * capacite2 * time / 100
                coast(0, - cout_puissance, timestep)
            if soc1 == 0:
                cout_puissance = soc1_mem - (((load1 - pv_power1) / capacite1 / time) * 100)
                coast(cout_puissance, 0)
            return soc1, soc2

        if cas == 4:  # PV1 <= load1 et PV2 <= load 2
            # print(' cas' + str(4))
            if (((load1 - pv_power1) / time / capacite1) * 100) > soc1:
                n_perdue += 1
                #print("la batterie1 n'a pas réussi à aider le pv1, elle charge 15 min")
                soc1 += (pv_power1 / time / capacite1) * 100
            if (((load2 - pv_power2) / time / capacite2) * 100) > soc2:
                #print("la batterie2 n'a pas réussi à aider le pv2, elle charge 15 min")
                n_perdue += 1
                soc2 += (pv_power2 / time / capacite2) * 100
            if not (((load1 - pv_power1) / time / capacite1) * 100) > soc1 and not (((load2 - pv_power2) / time / capacite2) * 100) > soc2:
                soc1 -= (((load1 - pv_power1) / time / capacite1) * 100)
                soc2 -= (((load2 - pv_power2) / time / capacite2) * 100)
            return soc1, soc2, n_perdue
        return soc1, soc2


    def coast(cout1, cout2, timestep):
        """ Calcul le cout positif : energie n'ayant pas pu être fournie à la charge car trop de demande
            et le coup négatif : batterie deja à 100% ou en train de se décharger dans l'autre"""
        if cout1 > 0:
            l_coast1[timestep] = cout1
        if cout2 > 0:
            l_coast2[timestep] = cout2
        if cout1 < 0:
            l_perdue[timestep] = cout1 + l_perdue[timestep - 1]
        if cout2 < 0:
            l_perdue[timestep] = cout2 + l_perdue[timestep - 1]


    # Boucle sur une journée avec un pas de temps de 15min
    for timestep in range(len(timesteps)):

        list_soc1.append(soc1)
        list_soc2.append(soc2)
        pv_power1 = list_pv_power1[timestep]  # Renommage pour calcul
        pv_power2 = list_pv_power2[timestep]

        load1 = list_load1[timestep]
        load2 = list_load2[timestep]

        cas = 0

        # print(list_soc1[timestep], list_soc2[timestep], pv_power1, pv_power2, load1, load2)
        # print(l_perdue[timestep - 1])
        if load1 > (pv_power1 + p_max_bat1):   # Test de sécurité surcharge
            soc1 += ((pv_power1 / time) / capacite1) * 100  # Calcul fait pour 15min
            print("la batterie 1 et le pv1 n'ont pas assez d'énergie")
            n_perdue += 1
            coast(load1, 0, timestep)
            n_perdue += 1

        if load2 > (pv_power2 + p_max_bat2):
            soc2 += ((pv_power2 / time) / capacite2) * 100  # Calcul fait pour 15min
            print("la batterie 2 et le pv2 n'ont pas assez d'énergie")
            n_perdue += 1
            coast(0, load2, timestep)
            n_perdue += 1
        else:
            if pv_power1 > load1:
                if pv_power2 >= load2:  # Les deux PV peuvent gérer les charges, on regarde pour équilibrer les bat
                    cas = 1
                    soc1, soc2 = transfert_energie(soc1, soc2, pv_power1, pv_power2, load1, load2, cas, n_perdue)

                if pv_power2 <= load2:   # La batterie 2 décharge déja donc elle le transfert sera de 2 -> 1
                    cas = 2
                    soc1, soc2 = transfert_energie(soc1, soc2, pv_power1, pv_power2, load1, load2, cas, n_perdue)

            if load1 > pv_power1:  # Le pv ne peux pas fournir toute la puissance
                if load2 <= pv_power2:  # B2 charge avec le pv ou B1 (le meilleur) si différence de soc
                    cas = 3
                    soc1, soc2 = transfert_energie(soc1, soc2, pv_power1, pv_power2, load1, load2, cas, n_perdue)

                if load2 >= pv_power2:
                    cas = 4
                    soc1, soc2, n_perdue = transfert_energie(soc1, soc2, pv_power1, pv_power2, load1, load2, cas, n_perdue)
        if l_perdue[timestep] == 0:  # Si pas de perte sur un tour de boucle alors on garde en mémoire la précedente
            l_perdue[timestep] = l_perdue[timestep - 1]
    L_perdue.append(l_perdue[len(timesteps) - 1])
    N_perdue.append(n_perdue)

moyenne1 = sum(L_perdue) / len(L_perdue)
moyenne2 = sum(N_perdue) / len(N_perdue)
print("moyenne1 perdue = " + str(moyenne1))
print("moyenne2 perdue = " + str(moyenne2))

# Temps = [k/4 for k in range(len(timesteps))]
# plt.subplot(2, 2, 1)
# plt.plot(Temps, list_pv_power1, label='pv_power1')
# plt.plot(Temps, list_pv_power2, label='pv_power2')
# plt.xlabel('Temps (en h)')
# plt.ylabel('Puissance (mW)')
# plt.legend()
#
# plt.subplot(2, 2, 2)
# plt.plot(Temps, list_load1, label='load1')
# plt.plot(Temps, list_load2, label='load2')
# plt.xlabel('Temps (en h)')
# plt.ylabel('Puissance (mW)')
# plt.legend()
#
# plt.subplot(2, 2, 3)
# plt.plot(Temps, l_perdue, label='Puissance perdue')
# plt.xlabel('Temps (en h)')
# plt.ylabel('Puissance (mW)')
# plt.legend()
#
# plt.subplot(2, 2, 4)
# plt.plot(Temps, list_soc1, label='soc1')
# plt.plot(Temps, list_soc2, label='soc2')
# plt.xlabel('Temps (en h)')
# plt.ylabel('State of charge (%)')
# plt.legend()
#
# plt.show()

