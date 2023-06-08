import math
import numpy as np
import random
from random import *
from datetime import datetime, timedelta

import pickle

# Charger le tableau "action" depuis le fichier
with open("action.pkl", "rb") as f:
    actions = pickle.load(f)


dt = 1/6  # (en h)
n_batterie = 4
puissance_reception = puissance_emission = 18  # (kW)
capacite = 14.4  # (kWh)

n_coupures = 0


def sign(x):
    if x > 0:
        return 1
    if x < 0:
        return -1
    if x == 0:
        return 0


class Batterie:
    def __init__(self, numero, soc_initial, puissance_emission, puissance_reception, capacite):
        self.numero = numero
        self.soc_initial = soc_initial
        self.soc = soc_initial
        self.puissance_emission = puissance_emission
        self.puissance_reception = puissance_reception
        self.capacite = capacite

    def get_numero(self):
        return self.numero

    def get_soc_initial(self):
        return self.soc_initial

    def get_soc(self):
        return self.soc

    def get_puissance_emission(self):
        return self.puissance_emission

    def get_puissance_reception(self):
        return self.puissance_reception

    def get_capacite(self):
        return self.capacite

    def donne(self, puissance):
        self.soc -= (puissance * dt / self.capacite) * 100
        if self.soc < 0:
            self.soc = 0

    def recoit(self, puissance):
        self.soc += (puissance * dt / self.capacite) * 100
        if self.soc > 100:
            self.soc = 100


# def action(pv, demand, soc):
#
#     actions = np.zeros((n_batterie, n_batterie))
#     surplus = []
#     puissance_dispo_rec = [puissance_emission, puissance_emission, puissance_emission, puissance_emission]
#     puissance_dispo_em = [puissance_emission, puissance_emission, puissance_emission, puissance_emission]
#     donneurs = []
#     receveurs = []
#     don_max = 30 / 100  # chaque batterie peut donner aux autres maximum 30% de son SOC
#
#     # Calcul du surplu restant après avoir aidé le PV
#     for batterie in range(0, n_batterie):
#         surplus.append(pv[batterie] - demand[batterie])
#
#         if surplus[batterie] <= 0:  # La batterie est donneuse ie alpha < 0.
#             soc_demande = ((surplus[batterie] * dt) / capacite) * 100
#
#             if soc_demande > soc[batterie]:  # la batterie n'a pas assez de SOC pour aider le PV
#                 reward(-100)  # On a une coupure et donc on va plutot charger la batterie
#                 soc[batterie] = ((soc[batterie] / 100) * capacite - surplus[batterie] * dt) * 100  # on charge
#                 actions[batterie][batterie] += - surplus[batterie] / puissance_emission
#                 puissance_dispo_rec[batterie] += surplus  # surplus < 0
#                 receveurs.append(batterie)
#
#             else:
#                 donneurs.append(batterie)
#                 soc[batterie] += (surplus[batterie] * dt) / capacite * 100
#                 actions[batterie][batterie] = surplus[batterie] / puissance_emission
#                 puissance_dispo_em[batterie] += surplus[batterie]  # surplus < 0
#
#         else:
#             chance_recoit = randint(0, 1)
#             if chance_recoit == 1:
#                 actions[batterie][batterie] = surplus[batterie] / puissance_emission  # la batterie recoie le surplus de son PV
#                 puissance_dispo_rec[batterie] -= surplus[batterie]
#                 receveurs.append(batterie)
#
#             else:
#                 donneurs.append(batterie)
#
#     # si surplus > 0 on ne donne pas, alpha reste = 0
#     nombre_donneuse = len(donneurs)
#     nombre_receveuse = len(receveurs)
#     print(actions, f"donneurs =  {donneurs}", f"receveurs = {receveurs}")
#     for batterie in range(0, n_batterie):  # on va maintenant donné les gammas et alphas donneurs avec surplus > 0
#         n_parts = 100  # on convertit en W et on divise la puissance_dispo en 100 parts
#
#         if actions[batterie][batterie] <= 0:  # la batterie est donneuse, et à deja donné a son PV
#             if len(receveurs) != 0:
#                 for parts in range(0, n_parts):
#                     nbr = randint(0, len(receveurs)-1)  # si 0 on ne donne pas, sinon dans l'ordre de receveurs
#                     if receveurs[nbr] > batterie:
#                         puissance_donnee = puissance_dispo_em[batterie] / n_parts
#
#                         actions[receveurs[nbr]][batterie] -= puissance_donnee / puissance_emission
#                         soc[receveurs[nbr]] += (puissance_donnee * dt / capacite) * 100
#                         soc[batterie] -= (puissance_donnee * dt / capacite) * 100
#                         puissance_dispo_em[batterie] -= puissance_donnee
#                         puissance_dispo_rec[receveurs[nbr]] -= puissance_donnee
#
#         if actions[batterie][batterie] > 0:  # la batterie est receveuse et recoit deja son PV
#             if len(donneurs) != 0:
#                 for parts in range(0, n_parts):
#                     nbr = randint(0, len(donneurs)-1)  # si 0 on ne donne pas, sinon dans l'ordre de receveurs
#                     if donneurs[nbr] > batterie:
#                         puissance_donnee = puissance_dispo_em[donneurs[nbr]] / n_parts
#
#                         actions[donneurs[nbr]][batterie] += puissance_donnee / puissance_reception
#                         soc[donneurs[nbr]] -= (puissance_donnee * dt / capacite) * 100
#                         soc[batterie] += (puissance_donnee * dt / capacite) * 100
#                         puissance_dispo_em[donneurs[nbr]] -= puissance_donnee
#                         puissance_dispo_rec[batterie] -= puissance_donnee
#
#     return actions, soc
#
#
# print(action([3.5, 2.5, 2.0, 2.7], [2.7, 2.3, 2.5, 2.0], [50, 60, 30, 55]))

def list_charges(delais):
    charge = []

    # Date de début (aujourd'hui à minuit)
    start_date = datetime(2016, 1, 1)

    # Date de fin (un mois plus tard)
    end_date = start_date + timedelta(days=delais)

    # Heures de début et de fin des deux périodes
    day_start = start_date.replace(hour=7, minute=0, second=0, microsecond=0)
    day_end = start_date.replace(hour=21, minute=0, second=0, microsecond=0)

    # Boucle pour remplir la liste avec des valeurs toutes les 10 minutes
    while start_date < end_date:
        if start_date.hour >= 6 and start_date.hour < 22:
            # Ajouter une valeur spécifique pour les heures de jour
            charge.append(np.random.uniform(0, 3.5))
        else:
            # Ajouter une autre valeur pour les heures de nuit
            charge.append(np.random.uniform(0, 0.52))
        start_date += timedelta(minutes=10)
    return charge


def demand(delai):
    puissances_loads = []

    for batterie in range(0, 4):
        puissances_loads.append(list_charges(delai))

    return puissances_loads


# Appeler la fonction pour générer le tableau "action"
demands = demand(334)
demands2semaines = demand(15)

# Afficher le tableau "demands"

# Enregistrer le tableau "demands" dans un fichier avec pickle
with open("demands.pkl", "wb") as f:
    pickle.dump(demands, f)


# Enregistrer le tableau "demands" dans un fichier avec pickle
with open("demands2semaines.pkl", "wb") as f:
    pickle.dump(demands2semaines, f)

print("Le tableau 'demands' a été enregistré dans le fichier 'demands.pkl'.")




