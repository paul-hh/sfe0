import pandas as pd
import numpy as np

# Lien https des données juin 2016 Cilaos
url = 'https://galilee.univ-reunion.fr/thredds/fileServer/dataTextfiles/La_Reunion/cilaospiscine/2016/cilaospiscine_2016-06.csv'

# Importation des données
data = pd.io.parsers.read_csv(url, header=None)

tab_donnee = np.zeros(len(data))  # Tableau np des données qui nous interesse

for donnee in range(1, len(data)):
    tab_donnee[donnee] = data[2][donnee]

tab_donnee = np.delete(tab_donnee, 0)  # Suppression du premier élement, car ne correspond pas à de la donnée

