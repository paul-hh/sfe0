# HENON-HILAIRE PAUL
# Mai 2023


# Code python visant à mettre en place intelligence artificielle de Reinforcement Learning pour le cas de 4 batteries.
# On utilise la librairie Stable Baseline avec l'algorithme PPO2


###################################################   IMPORTATIONS   ###################################################
########################################################################################################################

import numpy as np
import random
from random import *
import matplotlib.pyplot as plt
from matplotlib.pyplot import *


from datetime import datetime, timedelta
import pickle

import gym
from gym import spaces
from stable_baselines3 import PPO


# Charger le tableau "action" depuis le fichier Actions.py
with open("actions.pkl", "rb") as f:
    actions = pickle.load(f)

# Charger le tableau "action" depuis le fichier pv_2016.py
with open("pv2016.pkl", "rb") as f:
    pv2016 = pickle.load(f)

# Charger le tableau "action" depuis le fichier pv_2015_01.py
with open("pv20152semaines.pkl", "rb") as f:
    pv2015_01 = pickle.load(f)

# Charger le tableau "demands" depuis le fichier Classes.py
with open("demands.pkl", "rb") as f:
    demands1 = pickle.load(f)

# Charger le tableau "demands2semaines" depuis le fichier Classes.py
with open("demands2semaines.pkl", "rb") as f:
    demands2semaines = pickle.load(f)


dt = 1/6  # (en h)
capacite = 28.8  # (kWh)

################################################   CUSTOM ENVIRONMENT   ################################################
########################################################################################################################

pvs = pv2016  # On charge les valeurs des PVs (17 panneaux) en kW
demands = demands1


class CustomEnvironment(gym.Env):

    def __init__(self, action_list):
        # Initialisation de l'environnement
        super().__init__()
        self.action_list = action_list
        self.action_space = spaces.Discrete(len(action_list))
        self.observation_space = spaces.Box(low=0, high=100, shape=(12,), dtype=np.float32)  # Dans l'ordre SOC, PV, Demand

        self.timestep = 0
        self.total_reward = 0

    def initial_state(self):
        # Générer l'état initial de l'environnement
        # À adapter selon votre logique
        self.timestep = 0
        return np.array([50, 50, 50, 50, pvs[0][0], pvs[0][0], pvs[0][0], pvs[0][0], demands[0][0], demands[0][1],
                         demands[0][2], demands[0][3]])  # État initial avec 50% de SOC pour chaque batterie

    def step(self, action):
        # Obtenir l'action correspondante à partir de la liste d'actions
        numero_action = action

        # Utiliser l'action sélectionnée pour modifier l'état de l'environnement
        # Effectuer les échanges d'énergie décrits par la matrice d'action

        # Mettre à jour l'état de l'environnement en fonction des actions effectuées
        surplu, Flag = self.update_state(numero_action)

        # Calculer la récompense en fonction de l'état nouvellement atteint
        reward = self.calculate_reward(surplu, Flag)
        self.total_reward += reward

        # Vérifier si l'épisode est terminé ou non
        done = self.is_episode_done()

        # Retourner l'observation mise à jour, la récompense, si l'épisode est terminé et des informations supplémentaires
        return self.current_state, reward, done, {}

    def update_state(self, numero_action):
        # Mettre à jour l'état de l'environnement en fonction des actions effectuées
        surplu = [0, 0, 0, 0]

        Flag = [False, False, False, False]

        for batterie in range(0, 4):

            surplu[batterie] = (pvs[self.timestep] - demands[batterie][self.timestep]) * dt - (actions[numero_action][batterie][batterie] / 100 * capacite)

            if (actions[numero_action][batterie][batterie] / 100 * capacite) > (pvs[self.timestep] * dt):  # On regarde si la batterie ne recoit pas plus que le PV
                Flag[batterie] = True

            for ligne in range(batterie, 4):

                if ligne == batterie:  # La batterie recoit si > 0 donne sinon
                    self.current_state[batterie] += actions[numero_action][batterie][ligne]

                else:
                    self.current_state[batterie] += actions[numero_action][ligne][batterie]  # Echange entre la batterie "batterie" et la
                    self.current_state[ligne] += actions[numero_action][ligne][batterie]  # batterie "ligne"

        self.timestep += 1

        for machins in range(4, 8):
            self.current_state[machins] = pvs[self.timestep][0]

        for trucs in range(8, 12):
            self.current_state[trucs] = demands[trucs - 8][self.timestep]

        return surplu, Flag

    def calculate_reward(self, surplu, Flag):
        # Calculer la récompense en fonction de l'état nouvellement atteint
        # Récompense si les SOCs restent entre 55 et 45 mais un malus sinon. Pénalise si la demande n'est pas satisfaite
        reward = 0
        for batterie in range(0, 4):

            if surplu[batterie] < 0:
                reward -= 10

            if Flag[batterie]:
                reward -= 2

            if 40 < self.current_state[batterie] <= 60:
                reward += 2

            if 60 < self.current_state[batterie] <= 70 or 30 < self.current_state[batterie] <= 40:
                reward += 0.5

            if 70 < self.current_state[batterie] <= 80 or 20 < self.current_state[batterie] <= 30:
                reward += 0.3

            if 80 < self.current_state[batterie] <= 90 or 10 < self.current_state[batterie] <= 20:
                reward += 0.15

            if 90 < self.current_state[batterie] <= 100 or 0 < self.current_state[batterie] <= 10:
                reward += 0.1

            if self.current_state[batterie] > 100:  # Malus si dépasse 100% ou est inférieure à 0%
                reward -= 1
                self.current_state[batterie] = 100

            if self.current_state[batterie] <= 0:
                reward -= 5
                self.current_state[batterie] = 0

        return reward

    def is_episode_done(self):
        # Vérifier si l'épisode est terminé ou non
        if self.timestep >= len(pvs) - 1:
            return True

    def reset(self):
        # Réinitialisation de l'environnement et initialisation de l'état initial
        print("coucou c'est le reset, total_reward = " + str(self.total_reward))
        self.total_reward = 0
        self.current_state = self.initial_state()
        return self.current_state

    def render(self, mode='human'):
        # Méthode d'affichage de l'environnement
        pass

    # def close(self):
    #     # Méthode de fermeture de l'environnement
    #     pass


#############################################   ENTRAINEMENT DU MODEL   ################################################
########################################################################################################################

env = CustomEnvironment(actions)  # Remplacez CustomEnvironment() par l'instanciation de votre environnement avec les paramètres appropriés

model = PPO("MlpPolicy", env, verbose=1)
model.learn(total_timesteps=1000000)
model.save("ppo_v1")

print("L'agent à terminé de s'entrainer, le model est sauvegardé")
# del model  # remove to demonstrate saving and loading

model = PPO.load("ppo_v1")

##############################################   UTILISATION DE L'AGENT   ##############################################
########################################################################################################################

pvs2 = pv2015_01
demands2 = demands2semaines


class TestCustomEnvironment(gym.Env):

    def __init__(self, action_list):
        # Initialisation de l'environnement
        super().__init__()
        self.action_list = action_list
        self.action_space = spaces.Discrete(len(action_list))
        self.observation_space = spaces.Box(low=0, high=100, shape=(12,), dtype=np.float32)  # Dans l'ordre SOC, PV, Demand

        self.timestep = 0
        self.total_reward = 0
        self.nombre_coupures = 0

    def initial_state(self):
        # Générer l'état initial de l'environnement
        # À adapter selon votre logique
        self.timestep = 0
        return np.array([50, 50, 50, 50, pvs2[0][0], pvs2[0][0], pvs2[0][0], pvs2[0][0], demands2[0][0], demands2[0][1],
                         demands2[0][2], demands2[0][3]])  # État initial avec 50% de SOC pour chaque batterie

    def step(self, action):
        # Obtenir l'action correspondante à partir de la liste d'actions
        numero_action = action

        # Utiliser l'action sélectionnée pour modifier l'état de l'environnement
        # Effectuer les échanges d'énergie décrits par la matrice d'action

        # Mettre à jour l'état de l'environnement en fonction des actions effectuées
        surplu, Flag = self.update_state(numero_action)

        # Calculer la récompense en fonction de l'état nouvellement atteint
        reward = self.calculate_reward(surplu, Flag)
        self.total_reward += reward

        # Vérifier si l'épisode est terminé ou non
        done = self.is_episode_done()

        # Retourner l'observation mise à jour, la récompense, si l'épisode est terminé et des informations supplémentaires
        return self.current_state, reward, done, {}, self.nombre_coupures

    def update_state(self, numero_action):
        # Mettre à jour l'état de l'environnement en fonction des actions effectuées
        surplu = [0, 0, 0, 0]

        Flag = [False, False, False, False]

        for batterie in range(0, 4):

            surplu[batterie] = (pvs2[self.timestep] - demands2[batterie][self.timestep]) * dt - (actions[numero_action][batterie][batterie] / 100 * capacite)

            if (actions[numero_action][batterie][batterie] / 100 * capacite) > (pvs2[self.timestep] * dt):  # On regarde si la batterie ne recoit pas plus que le PV
                Flag[batterie] = True

            for ligne in range(batterie, 4):

                if ligne == batterie:  # La batterie recoit si > 0 donne sinon
                    self.current_state[batterie] += actions[numero_action][batterie][ligne]

                else:
                    self.current_state[batterie] += actions[numero_action][ligne][batterie]  # Echange entre la batterie "batterie" et la
                    self.current_state[ligne] += actions[numero_action][ligne][batterie]  # batterie "ligne"

        self.timestep += 1

        for machins in range(4, 8):
            self.current_state[machins] = pvs2[self.timestep][0]

        for trucs in range(8, 12):
            self.current_state[trucs] = demands2[trucs - 8][self.timestep]

        return surplu, Flag

    def calculate_reward(self, surplu, Flag):
        # Calculer la récompense en fonction de l'état nouvellement atteint
        # Récompense si les SOCs restent entre 55 et 45 mais un malus sinon. Pénalise si la demande n'est pas satisfaite
        reward = 0
        for batterie in range(0, 4):

            if surplu[batterie] < 0:
                reward -= 5
                self.nombre_coupures += 1

            if Flag[batterie]:
                reward -= 5

            if 40 < self.current_state[batterie] <= 60:
                reward += 2

            if 60 < self.current_state[batterie] <= 70 or 30 < self.current_state[batterie] <= 40:
                reward += 0.5

            if 70 < self.current_state[batterie] <= 80 or 20 < self.current_state[batterie] <= 30:
                reward += 0.3

            if 80 < self.current_state[batterie] <= 90 or 10 < self.current_state[batterie] <= 20:
                reward += 0.15

            if 90 < self.current_state[batterie] <= 100 or 0 < self.current_state[batterie] <= 10:
                reward += 0.1

            if self.current_state[batterie] > 100:  # Malus si dépasse 100% ou est inférieure à 0%
                reward -= 1
                self.current_state[batterie] = 100

            if self.current_state[batterie] <= 0:
                reward -= 5
                self.current_state[batterie] = 0

        return reward

    def is_episode_done(self):
        # Vérifier si l'épisode est terminé ou non
        if self.timestep >= len(pvs2) - 1:
            return True

    def reset(self):
        # Réinitialisation de l'environnement et initialisation de l'état initial
        print("coucou c'est le reset, total_reward = " + str(self.total_reward))
        self.total_reward = 0
        self.current_state = self.initial_state()
        return self.current_state

    def render(self, mode='human'):
        # Méthode d'affichage de l'environnement
        pass

    # def close(self):
    #     # Méthode de fermeture de l'environnement
    #     pass


env_test = TestCustomEnvironment(actions)

# Enjoy trained agent
obs = env_test.reset()
soc1, soc2, soc3, soc4 = [50], [50], [50], [50]

while env_test.timestep < len(pvs2) - 1:
    action, _states = model.predict(obs)
    obs, rewards, dones, info, nombre_coupures = env_test.step(action)
    soc1.append(obs[0])
    soc2.append(obs[1])
    soc3.append(obs[2])
    soc4.append(obs[3])
print(env_test.nombre_coupures)

#################################################   AFFICHAGE DES SOC   ################################################
########################################################################################################################

liste_temps = [k for k in range(0, len(pvs2))]


plt.subplot()
plt.plot(liste_temps, soc1, color="green")
plt.xlabel('Temps (en h)')
plt.ylabel('SOC batterie 1')
plt.show()


plt.subplot()
plt.plot(liste_temps, soc2, color="blue")
plt.xlabel('Temps (en h)')
plt.ylabel('SOC batterie 2')
plt.show()


plt.subplot()
plt.plot(liste_temps, soc3, color="red")
plt.xlabel('Temps (en h)')
plt.ylabel('SOC batterie 3')
plt.show()


plt.subplot()
plt.plot(liste_temps, soc4, color="orange")
plt.xlabel('Temps (en h)')
plt.ylabel('SOC batterie 4')

plt.show()

