import prototypeGraphe as pg
import tkinter as tk
import networkx as nx
import matplotlib.pyplot as plt
import random
from numpy.random import normal

#Variables globales
connect_chance: float = 0.3
taux_mean: float = -1
initial_mean: float = 3
taux_std_dev: float = 1/3
initial_std_dev: float = 1

def generer_arbre() -> pg.Noeud:
    #creer les enfants d'un noeud
    def generer_enfants(noeud: pg.Noeud) -> None:
        nonlocal nb_next_niv
        nonlocal nb_noeuds

        nb = nb_enfants()

        for i in range(nb):
            nouveauNoeud = pg.Noeud(nb_noeuds)
            nb_noeuds += 1

            noeud.add_voisin(nouveauNoeud)
            queue.append(nouveauNoeud)
            nb_next_niv += 1

    #helper de generer_enfants
    def nb_enfants() -> int:
        mean : float = taux_mean * profondeur + initial_mean
        std_div: float = taux_std_dev * profondeur + initial_std_dev

        nbAl: float = normal(loc = mean, scale = std_div)

        if nbAl < 0:
            nbAl = 0
        elif nbAl > 3:
            nbAl = 3

        return int(nbAl)
    
    #Initialisation des variables
    root = pg.Noeud(0)
    queue: list[pg.Noeud] = []

    nb_noeuds = 1
    profondeur: int = 0
    nb_niv: int = 1
    nb_next_niv: int = 0

    #Navigation dans l'arbre
    queue.append(root)

    while len(queue) != 0:
        current = queue.pop(0)
        generer_enfants(current)

        nb_niv -= 1
        if nb_niv == 0:
            profondeur += 1
            nb_niv = nb_next_niv
            nb_next_niv = 0
    
    return root

def connecter_branches(root: pg.Noeud) -> pg.Noeud:
    #connecte ou non le noeud à un noeud à droite
    def connecter_noeud(noeud: pg.Noeud) -> None:
        if random.random() > connect_chance:
            return
        
        voisin: pg.Noeud = trouver_voisin_droite(noeud)

        if voisin != None:
            noeud.add_voisin(voisin)

    #retourne le voisin de droite d'un noeud à un certain niveau ou None s'il n'existe pas
    def trouver_voisin_droite(noeud: pg.Noeud) -> pg.Noeud:
        profondeur_noeud: int = -1
        profondeur_cible: int = -1
        voisin = None

        profondeur: int = 0
        nb_niv: int = 1
        nb_next_niv: int = 0

        visited: set[pg.Noeud] = set()
        queue: list[pg.Noeud] = []

        queue.append(root)
        visited.add(root)

        while len(queue) != 0:
            current = queue.pop(0)

            if current.nb == noeud.nb:
                profondeur_noeud = profondeur
            elif current.nb == noeud.nb + 1:
                profondeur_cible = profondeur
                voisin = current

            for v in current.voisins:
                if v not in visited:
                    queue.append(v)
                    visited.add(v)
                    nb_next_niv += 1

            nb_niv -= 1
            if nb_niv == 0:
                profondeur += 1
                nb_niv = nb_next_niv
                nb_next_niv = 0

        if profondeur_noeud != profondeur_cible:
            return None

        return voisin

    #Initialisation des variables
    visited: set[pg.Noeud] = set()
    stack: list[pg.Noeud] = []
    stack.append(root)

    #Navigation dans l'arbre
    while len(stack) != 0:
        current: pg.Noeud = stack.pop()

        visited.add(current)
        for v in current.voisins:
            if v in visited:
                continue

            stack.append(v)

        connecter_noeud(current)

def interface() -> None:
    def initialiser() -> None:
        root = tk.Tk()
        root.geometry("500x300")
        root.title("Configuration des paramètres de génération de graphe")

        labels = ["Chance de connection", "Taux médianne", "Médianne Initiale", "Taux écart-type", "Écart-type initial"]
        default_values: list[float] = [connect_chance, taux_mean, initial_mean, taux_std_dev, initial_std_dev]
        entry_vars: list[tk.StringVar] = []

        for i, label in enumerate(labels):
            tk.Label(root, text=label).grid(row=i, column=0, padx=10, pady=5)
            
            var = tk.StringVar(value=str(default_values[i]))
            var.trace_add("write", lambda name, index, mode, i=i, v=var: modifier_valeur(i, v))

            entry = tk.Entry(root, textvariable=var)
            entry.grid(row=i, column=1, padx=10, pady=5)
            
            entry_vars.append(var)

        tk.Button(root, text="Générer des graphes", command=afficher_graphes).grid(row=6, column=0, columnspan=2, pady=10)

        root.mainloop()

    def modifier_valeur(index: int, var: tk.StringVar):
        global connect_chance, taux_mean, initial_mean, taux_std_dev, initial_std_dev

        try:
            new_value = float(var.get())
        except ValueError:
            return

        if index == 0:
            connect_chance = new_value
        elif index == 1:
            taux_mean = new_value
        elif index == 2:
            initial_mean = new_value
        elif index == 3:
            taux_std_dev = new_value
        elif index == 4:
            initial_std_dev = new_value

    def afficher_graphes() -> None:
        graphes: list[pg.Graph] = []

        for i in range(4):
            graphes.append(generer_graphe())

        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        for i, graphe in enumerate(graphes):
            graphe.afficher(ax = axes[i//2, i%2])

        plt.show()

    def generer_graphe() -> pg.Graph:
        root = generer_arbre()
        connecter_branches(root)
        noeuds: list[pg.Noeud] = []

        visited: set[pg.Noeud] = set()
        queue: list[pg.Noeud] = []

        queue.append(root)
        visited.add(root)

        while len(queue) != 0:
            current: pg.Noeud = queue.pop(0)
            noeuds.append(current)

            for v in current.voisins:
                if v not in visited:
                    queue.append(v)
                    visited.add(v)

        graphe = pg.Graph()
        graphe.add_noeuds(noeuds)

        return graphe
    
    initialiser()

if __name__ == "__main__":
    interface()