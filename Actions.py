import itertools
import numpy as np
import pickle

# Options pour chaque paramètre
options = [-10, 0, 10]


# Fonction de transition pour vérifier les conditions*


def transition(matrix):
    for j in range(0, 4):  # Les colonnes ont un seul signe
        for i in range(j, 4):
            if np.sign(matrix[i][j]) != np.sign(matrix[j][j]) and np.sign(matrix[i][j]) != 0 and np.sign(matrix[j][j]) != 0:
                return False

    for i in range(1, 4):
        for j in range(0, i):
            signe = np.sign(matrix[i][j])
            for ligne in range(0, 4):
                if np.sign(matrix[ligne][i]) == signe and np.sign(matrix[ligne][i]) != 0:
                    return False

    return True


# Fonction pour générer le tableau "action" avec les matrices compatibles
def generate_action():
    # Générer toutes les combinaisons possibles
    combinations = np.array(list(itertools.product(options, repeat=10)))

    # Initialiser le tableau "action"
    actions = []

    # Vérifier chaque matrice générée et les ajouter à "action" si elles sont compatibles
    for combination in combinations:
        matrix = np.zeros((4, 4))
        matrix[np.tril_indices(4)] = combination

        if transition(matrix):
            actions.append(matrix)

    # Convertir "action" en un tableau numpy
    actions = np.array(actions)

    return actions


# Appeler la fonction pour générer le tableau "action"
actions = generate_action()

# Afficher le tableau "action"

# Enregistrer le tableau "action" dans un fichier avec pickle
with open("actions.pkl", "wb") as f:
    pickle.dump(actions, f)

print("Le tableau 'actions' a été enregistré dans le fichier 'action.pkl'.")

print(len(actions))


