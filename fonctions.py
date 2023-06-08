import numpy as np


def matrice_liste(mat):
    """Renvoie une liste de tous les élements de la matrice bout à bout"""
    return np.ndarray.flatten(mat)


def base_p(liste, p):
    """Renvoie la valeur en base p de la matrice pour un nombre p de valeurs de variable possible """
    nbr = 0
    for elt in range(0, len(liste)):
        nbr += liste[elt] * (p**elt)
    return nbr


def decomposition_base_p(k, p, n):
    """
    Renvoie la décomposition dans la base p de k sous forme de liste de taille 2*n*(n-1)
    """
    # Initialisation de la liste de décomposition
    decomp = [0] * n

    # Calcul de la décomposition dans la base p
    i = 0
    while k > 0:
        r = k % p
        decomp[i] = r
        k = (k - r) // p
        i += 1

    # Remplissage de la liste avec des zéros si nécessaire
    while i < n:
        decomp[i] = 0
        i += 1

    return np.array(decomp)


def tab_matrice(tab):
    """Renvoie la matrice reformée à partir d'un tableau, tab contient les élements sous diagonaux de la matrice
    il faut combler le reste avec des zeros"""

