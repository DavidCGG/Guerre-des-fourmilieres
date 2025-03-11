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

def generer_arbre() -> pg.Noeud_Generation:
    #creer les enfants d'un noeud
    def generer_enfants(noeud: pg.Noeud_Generation) -> None:
        nonlocal nb_next_niv
        nonlocal nb_noeuds

        nb = nb_enfants()

        for i in range(nb):
            nouveauNoeud = pg.Noeud_Generation(nb_noeuds)
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
    root = pg.Noeud_Generation(0)
    queue: list[pg.Noeud_Generation] = []

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

def connecter_branches(root: pg.Noeud_Generation) -> pg.Noeud_Generation:
    #connecte ou non le noeud à un noeud à droite
    def connecter_noeud(noeud: pg.Noeud_Generation) -> None:
        if random.random() > connect_chance:
            return
        
        voisin: pg.Noeud_Generation = trouver_voisin_droite(noeud)

        if voisin != None:
            noeud.add_voisin(voisin)

    #retourne le voisin de droite d'un noeud à un certain niveau ou None s'il n'existe pas
    def trouver_voisin_droite(noeud: pg.Noeud_Generation) -> pg.Noeud_Generation:
        profondeur_noeud: int = -1
        profondeur_cible: int = -1
        voisin = None

        profondeur: int = 0
        nb_niv: int = 1
        nb_next_niv: int = 0

        visited: set[pg.Noeud_Generation] = set()
        queue: list[pg.Noeud_Generation] = []

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
    visited: set[pg.Noeud_Generation] = set()
    visited.add(root)

    stack: list[pg.Noeud_Generation] = []
    stack.append(root)

    #Navigation dans l'arbre
    while len(stack) != 0:
        current: pg.Noeud_Generation = stack.pop()

        for v in current.voisins:
            if v not in visited:
                stack.append(v)
                visited.add(v)

        connecter_noeud(current)

#Utilise une méthode de disposition avec ressorts
def attribuer_poids(root: pg.Noeud_Generation) -> pg.Noeud_Pondere:
    #Créer aléatoirment les coordonnées des noeuds
    def initialiser_coord() -> pg.Noeud_Pondere:

        visited: set[pg.Noeud_Generation] = set()
        visited.add(root)

        queue: list[pg.Noeud_Generation] = []
        queue.append(root)

        profondeur: int = 0
        nb_niv: int = 1
        nb_next_niv: int = 0
        nb_niv_precedents: int = 0

        profondeur_max = trouver_profondeur(root)
        root_pondere = pg.Noeud_Pondere()

        queue_pondere: list[pg.Noeud_Pondere] = []
        queue_pondere.append(root_pondere)

        lien_graphe: dict[pg.Noeud_Generation, pg.Noeud_Pondere] = dict()

        #Navigation dans l'arbre
        while len(queue) != 0:
            current = queue.pop(0)
            current_pondere = queue_pondere.pop(0)

            current_pondere.coord = (nb_niv_precedents - current.nb, profondeur_max - profondeur)

            for v in current.voisins:
                if v not in lien_graphe:
                    lien_graphe[v] = pg.Noeud_Pondere()
                    current_pondere.add_voisin(lien_graphe[v])
                else:
                    current_pondere.add_voisin(lien_graphe[v])

                if v not in visited:
                    queue.append(v)
                    queue_pondere.append(lien_graphe[v])
                    visited.add(v)
                    nb_next_niv += 1 

            nb_niv -= 1
            if nb_niv == 0:
                profondeur += 1
                nb_niv_precedents += nb_next_niv

                nb_niv = nb_next_niv
                nb_next_niv = 0

        return root_pondere

    def trouver_profondeur(root: pg.Noeud_Generation) -> int:
        visited: set[pg.Noeud_Generation] = set()
        visited.add(root)

        queue: list[pg.Noeud_Generation] = []
        queue.append(root)

        profondeur: int = 0
        nb_niv: int = 1
        nb_next_niv: int = 0

        while len(queue) != 0:
            current = queue.pop(0)

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

        return profondeur

    #Applique les forces sur tous noeuds
    def calculer_force() -> None:
        visited: set[pg.Noeud_Pondere] = set()
        visited.add(root_pondere)

        queue: list[pg.Noeud_Pondere] = []
        queue.append(root_pondere)

        #Navigation dans l'arbre
        while len(queue) != 0:
            current = queue.pop(0)

            calculer_repulsion(current)
            calculer_attraction(current)

            for v in current.voisins:
                if v not in visited:
                    queue.append(v)
                    visited.add(v)

    #Applique une force de repulsion sur un noeud
    def calculer_repulsion(noeud: pg.Noeud_Pondere) -> None:
        visited: set[pg.Noeud_Pondere] = set()
        visited.add(root_pondere)

        queue: list[pg.Noeud_Pondere] = []
        queue.append(root_pondere)

        #Navigation dans l'arbre
        while len(queue) != 0:
            current = queue.pop(0)

            if current == noeud:
                continue

            dx = noeud.coord[0] - current.coord[0]
            dy = noeud.coord[1] - current.coord[1]
            dist = (dx ** 2 + dy ** 2) ** 0.5
            force_x, force_y = 0.01 * dx / (dist ** 2), 0.01 * dy / (dist ** 2)

            noeud.coord = (noeud.coord[0] + force_x, noeud.coord[1] + force_y)

            for v in current.voisins:
                if v not in visited:
                    queue.append(v)
                    visited.add(v)

    #Applique une force d'attraction sur un noeud
    def calculer_attraction(noeud: pg.Noeud_Pondere) -> None:
        for v in noeud.voisins:
            dx = v.coord[0] - noeud.coord[0]
            dy = v.coord[1] - noeud.coord[1]
            force_x, force_y = 0.01 * dx, 0.01 * dy

            noeud.coord = (noeud.coord[0] + force_x, noeud.coord[1] + force_y)

    #Initialisation des variables
    root_pondere = initialiser_coord()

    for _ in range(100):
        calculer_force()

    return root_pondere

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
        noeuds: list[pg.Noeud_Generation] = []

        visited: set[pg.Noeud_Generation] = set()
        queue: list[pg.Noeud_Generation] = []

        queue.append(root)
        visited.add(root)

        while len(queue) != 0:
            current: pg.Noeud_Generation = queue.pop(0)
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
    n0 = pg.Noeud_Generation(0)
    n1 = pg.Noeud_Generation(1)
    n2 = pg.Noeud_Generation(2)
    n3 = pg.Noeud_Generation(3)
    n4 = pg.Noeud_Generation(4)
    n5 = pg.Noeud_Generation(5)

    n0.add_voisin(n1)
    n0.add_voisin(n2)
    n0.add_voisin(n3)

    n1.add_voisin(n2)
    n1.add_voisin(n4)
    n1.add_voisin(n5)

    n0_pondere = attribuer_poids(n0)

    noeuds: list[pg.Noeud_Pondere] = []

    visited: set[pg.Noeud_Pondere] = set()
    queue: list[pg.Noeud_Pondere] = []

    queue.append(n0_pondere)
    visited.add(n0_pondere)

    while len(queue) != 0:
        current: pg.Noeud_Pondere = queue.pop(0)
        noeuds.append(current)

        for v in current.voisins:
            if v not in visited:
                queue.append(v)
                visited.add(v)

    graphe = pg.Graph()
    graphe.add_noeuds(noeuds)

    print(graphe)
    graphe.afficher()