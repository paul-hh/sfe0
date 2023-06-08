import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
import itertools
import pickle

# Importation des données


def extraction_donnee_pv(panneaux):
    # Liens https des données 2016 Cilaos
    url0 = 'https://galilee.univ-reunion.fr/thredds/fileServer/dataTextfiles/La_Reunion/cilaospiscine/2016/cilaospiscine_2016-01.csv'
    url1 = 'https://galilee.univ-reunion.fr/thredds/fileServer/dataTextfiles/La_Reunion/cilaospiscine/2016/cilaospiscine_2016-02.csv'
    url2 = 'https://galilee.univ-reunion.fr/thredds/fileServer/dataTextfiles/La_Reunion/cilaospiscine/2016/cilaospiscine_2016-03.csv'
    url3 = 'https://galilee.univ-reunion.fr/thredds/fileServer/dataTextfiles/La_Reunion/cilaospiscine/2016/cilaospiscine_2016-05.csv'
    url4 = 'https://galilee.univ-reunion.fr/thredds/fileServer/dataTextfiles/La_Reunion/cilaospiscine/2016/cilaospiscine_2016-05.csv'
    url5 = 'https://galilee.univ-reunion.fr/thredds/fileServer/dataTextfiles/La_Reunion/cilaospiscine/2016/cilaospiscine_2016-06.csv'
    url6 = 'https://galilee.univ-reunion.fr/thredds/fileServer/dataTextfiles/La_Reunion/cilaospiscine/2016/cilaospiscine_2016-07.csv'
    url7 = 'https://galilee.univ-reunion.fr/thredds/fileServer/dataTextfiles/La_Reunion/cilaospiscine/2016/cilaospiscine_2016-08.csv'
    url8 = 'https://galilee.univ-reunion.fr/thredds/fileServer/dataTextfiles/La_Reunion/cilaospiscine/2016/cilaospiscine_2016-09.csv'
    url9 = 'https://galilee.univ-reunion.fr/thredds/fileServer/dataTextfiles/La_Reunion/cilaospiscine/2016/cilaospiscine_2016-10.csv'
    url10 = 'https://galilee.univ-reunion.fr/thredds/fileServer/dataTextfiles/La_Reunion/cilaospiscine/2016/cilaospiscine_2016-11.csv'
    url11 = 'https://galilee.univ-reunion.fr/thredds/fileServer/dataTextfiles/La_Reunion/cilaospiscine/2016/cilaospiscine_2016-12.csv'

    url = [url0, url1, url2, url3, url4, url5, url6, url7, url8, url9, url10, url11]

    data = []
    for mois in range(0, 11):
        df = pd.read_csv(url[mois], usecols=[0, 2], parse_dates=['timestamp'])
        df = df.fillna(method="ffill")
        df = df.resample('10min', on="timestamp").mean()
        time_idx = df.index
        df = np.array(df)
        for donnee in range(0, len(df)):
            df[donnee] = df[donnee] * 1.7 * panneaux * (20 / 100) / 1000   # rendement des 8 panneaux solaire de 13.6m² (en kW)
    #     gb = df.groupby([time_idx.hour, time_idx.minute])
    #     df = gb.aggregate(np.mean)
    #     df.index.names = ["hour", "minute"]
    #
    #     df = df.reset_index()
    #     print(df)
    #
        data.extend(df)
    #
    # df = pd.concat(data)
    # df = df.groupby('index').mean()
    return data


# Enregistrer le tableau "action" dans un fichier avec pickle
with open("pv2016.pkl", "wb") as f:
    pickle.dump(extraction_donnee_pv(17), f)

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


