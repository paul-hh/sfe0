import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
import itertools
import pickle

# Importation des données


def extraction_donnee_pv_2semaines(panneaux):
    # Liens https des données 2016 Cilaos
    url = "https://galilee.univ-reunion.fr/thredds/fileServer/dataTextfiles/La_Reunion/cilaospiscine/2015/cilaospiscine_2015-01.csv"

    data = []
    df = pd.read_csv(url, usecols=[0, 2], parse_dates=['timestamp'])
    df = df.fillna(method="ffill")
    df = df.resample('10min', on="timestamp").mean()
    time_idx = df.index
    df = np.array(df)
    for donnee in range(0, 15 * 144):
        df[donnee] = df[donnee] * 1.7 * panneaux * (20 / 100) / 1000   # rendement des 8 panneaux solaire de 13.6m² (en kW)
        data.append(df[donnee])
#     gb = df.groupby([time_idx.hour, time_idx.minute])
#     df = gb.aggregate(np.mean)
#     df.index.names = ["hour", "minute"]
#
#     df = df.reset_index()
#     print(df)
    return data


# Enregistrer le tableau "action" dans un fichier avec pickle
with open("pv20152semaines.pkl", "wb") as f:
    pickle.dump(extraction_donnee_pv_2semaines(17), f)

# liste_temps = [k for k in range(len(extraction_donnee_pv(17)))]
#
# fig, ax = plt.subplots()
#
# ax.plot(liste_temps,  extraction_donnee_pv(17))
# lst_position = np.arange(144, len(extraction_donnee_pv(17)) + 144, 144)
# l_xlabel = np.arange(1, 335)
# ax.set_xticks(lst_position, l_xlabel)
# plt.xlabel('Temps (en j)')
# plt.ylabel('Puissance solaire (kW)')
#
# plt.show()


