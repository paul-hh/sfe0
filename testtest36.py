import gym
from gym import spaces
from stable_baselines3 import PPO


model = PPO.load("ppo_v1")
env = CustomEnvironment(actions, 0)  # Remplacez CustomEnvironment() par l'instanciation de votre environnement avec les paramètres appropriés

# Enjoy trained agent
obs = env.reset()
soc1, soc2, soc3, soc4 = [50], [50], [50], [50]

while env.timestep != len(pvs) - 1:
    action, _states = model.predict(obs)
    obs, rewards, dones, info = env.step(action)
    soc1.append(obs[0])
    soc2.append(obs[1])
    soc3.append(obs[2])
    soc4.append(obs[3])

liste_temps = [k for k in range(0, len(pvs))]


plt.subplot()
plt.plot(liste_temps, soc1)
plt.xlabel('Temps (en h)')
plt.ylabel('SOC batterie 1')
plt.show()

plt.subplot()
plt.plot(liste_temps, soc2)
plt.xlabel('Temps (en h)')
plt.ylabel('SOC batterie 2')
plt.show()


plt.subplot()
plt.plot(liste_temps, soc3)
plt.xlabel('Temps (en h)')
plt.ylabel('SOC batterie 3')
plt.show()


plt.subplot()
plt.plot(liste_temps, soc4)
plt.xlabel('Temps (en h)')
plt.ylabel('SOC batterie 4')

plt.show()