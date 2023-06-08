# Importation des librairies :

import numpy as np

n = 3 # nombre de lignes et de colonnes
t = 3 # nombre d'éléments par liste
p = 3 # nombre de valeurs possibles pour chaque élément

# Créer un tableau multidimensionnel de forme (p**(n*n*t), n, n, t) contenant toutes les combinaisons possibles des éléments
matrices = np.array(np.meshgrid(*[range(p) for _ in range(n*n*t)])).T.reshape(-1, n, n, t)

