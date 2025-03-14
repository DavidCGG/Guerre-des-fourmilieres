import prototypeGraphe as pg
import tkinter as tk
import networkx as nx
import matplotlib.pyplot as plt
import random
from numpy.random import normal

#Variables globales
nb_noeuds_cible: int = 10
connect_chance: float = 0.3
taux_mean: float = -1
initial_mean: float = 3
taux_std_dev: float = 1/3
initial_std_dev: float = 1

def generer_arbre() -> pg.Noeud_Generation:
    #Creer les enfants d'un noeud
    def generer_enfants(current: pg.Noeud_Generation, profondeur: int, _) -> None:
        nonlocal nb_noeuds

        if len(current.voisins) != 0: #Évite de générer des enfants inutilement lors d'une ennième itération
            return

        nb = nb_enfants(profondeur)
        for i in range(nb):
            if nb_noeuds >= nb_noeuds_cible:
                return

            enfant = pg.Noeud_Generation(nb_noeuds)
            nb_noeuds += 1

            current.add_voisin(enfant)

    #Helper de generer_enfants
    def nb_enfants(profondeur: int) -> int:
        mean : float = taux_mean * profondeur + initial_mean
        std_div: float = taux_std_dev * profondeur + initial_std_dev

        nbAl: float = normal(loc = mean, scale = std_div)

        if nbAl < 0:
            nbAl = 0
        elif nbAl > 3:
            nbAl = 3

        return int(nbAl)
    
    root = pg.Noeud_Generation(0)
    nb_noeuds = 1

    while nb_noeuds < nb_noeuds_cible:
        bfs(root, generer_enfants)
    
    return root

def connecter_branches(root: pg.Noeud_Generation) -> pg.Noeud_Generation:
    #Connecte ou non le noeud à un noeud à droite
    def connecter_noeud(noeud: pg.Noeud_Generation, _, __) -> None:
        if random.random() > connect_chance:
            return
        
        voisin: pg.Noeud_Generation = trouver_voisin_droite(noeud, root)

        if voisin != None:
            noeud.add_voisin(voisin)

    #Retourne le voisin de droite d'un noeud à un certain niveau ou None s'il n'existe pas
    def trouver_voisin_droite(noeud: pg.Noeud_Generation, root: pg.Noeud_Generation) -> pg.Noeud_Generation:
        profondeur_noeud: int = -1
        profondeur_cible: int = -1
        voisin = None

        def trouver_voisin_droite_helper(current: pg.Noeud_Generation, profondeur: int, _) -> None:
            nonlocal profondeur_noeud, profondeur_cible, voisin

            if current.nb == noeud.nb:
                profondeur_noeud = profondeur
            elif current.nb == noeud.nb + 1:
                profondeur_cible = profondeur
                voisin = current

        bfs(root, trouver_voisin_droite_helper)

        return voisin if profondeur_noeud == profondeur_cible else None

    bfs(root, connecter_noeud)

#Utilise un algorithme de disposition par forces
def attribuer_poids(root: pg.Noeud_Generation) -> pg.Noeud_Pondere:
    #Créer aléatoirment les coordonnées des noeuds
    def initialiser_coord(root: pg.Noeud_Generation) -> pg.Noeud_Pondere:
        profondeur_max = trouver_profondeur(root)
        root_pondere = None
        lien_graphe: dict[pg.Noeud_Generation, pg.Noeud_Pondere] = dict()

        def initialiser_lien_graphe(current: pg.Noeud_Generation, _, __) -> None:
            nonlocal root_pondere, lien_graphe

            current_pondere = pg.Noeud_Pondere()
            lien_graphe[current] = current_pondere

            if current == root:
                root_pondere = current_pondere

        def initialiser_graphe_pondere(current: pg.Noeud_Generation, _, __) -> None:
            current_pondere = lien_graphe[current]

            for v in current.voisins:
                current_pondere.add_voisin(lien_graphe[v])

        def initialiser_coord_helper(current: pg.Noeud_Generation, profondeur: int, nb_niv_precedents: int) -> None:
            current_pondere = lien_graphe[current]
            current_pondere.coord = (nb_niv_precedents - current.nb, profondeur_max - profondeur)

        bfs(root, initialiser_lien_graphe)
        bfs(root, initialiser_graphe_pondere)
        bfs(root, initialiser_coord_helper)
        return root_pondere

    def trouver_profondeur(root: pg.Noeud_Generation) -> int:
        profondeur_max: int = 0

        def trouver_profondeur_helper(_, profondeur, __)-> None:
            nonlocal profondeur_max
            profondeur_max = max(profondeur_max, profondeur)

        bfs(root, trouver_profondeur_helper)
        return profondeur_max

    #Applique les forces sur tous noeuds
    def calculer_force(root_pondere: pg.Noeud_Pondere) -> None:
        def calculer_force_helper(noeud: pg.Noeud_Pondere, _, __) -> None:
            calculer_repulsion(noeud, root_pondere)
            calculer_attraction(noeud)
        
        bfs(root_pondere, calculer_force_helper)

    #Applique une force de repulsion sur un noeud
    def calculer_repulsion(noeud: pg.Noeud_Pondere, root_pondere: pg.Noeud_Pondere) -> None:
        def calculer_repulsion_helper(autre: pg.Noeud_Pondere, _, __) -> None:
            if autre == noeud:
                return
            
            dx = noeud.coord[0] - autre.coord[0]
            dy = noeud.coord[1] - autre.coord[1]
            dist = (dx ** 2 + dy ** 2) ** 0.5

            force_x, force_y = 0.01 * dx / (dist ** 2), 0.01 * dy / (dist ** 2)
            noeud.coord = (noeud.coord[0] + force_x, noeud.coord[1] + force_y)

        bfs(root_pondere, calculer_repulsion_helper)

    #Applique une force d'attraction sur un noeud
    def calculer_attraction(noeud: pg.Noeud_Pondere) -> None:
        for v in noeud.voisins:
            dx = v.coord[0] - noeud.coord[0]
            dy = v.coord[1] - noeud.coord[1]
            force_x, force_y = 0.01 * dx, 0.01 * dy

            noeud.coord = (noeud.coord[0] + force_x, noeud.coord[1] + force_y)

    root_pondere = initialiser_coord(root)
    for _ in range(100):
        calculer_force(root_pondere)

    return root_pondere

def interface() -> None:
    def initialiser() -> None:
        root = tk.Tk()
        root.geometry("500x300")
        root.title("Configuration des paramètres de génération de graphe")

        labels = ["Nombre de noeuds", "Chance de connection", "Taux médianne", "Médianne Initiale", "Taux écart-type", "Écart-type initial"]
        default_values: list[float] = [nb_noeuds_cible, connect_chance, taux_mean, initial_mean, taux_std_dev, initial_std_dev]
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
        global nb_noeuds_cible, connect_chance, taux_mean, initial_mean, taux_std_dev, initial_std_dev

        try:
            new_value = float(var.get())
        except ValueError:
            return

        if index ==0:
            nb_noeuds_cible = int(new_value)
        elif index == 1:
            connect_chance = new_value
        elif index == 2:
            taux_mean = new_value
        elif index == 3:
            initial_mean = new_value
        elif index == 4:
            taux_std_dev = new_value
        elif index == 5:
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
        def collecter_noeuds(root: pg.Noeud_Pondere, _, __) -> None:
            noeuds.append(root)

        root = generer_arbre()
        connecter_branches(root)
        root = attribuer_poids(root)

        noeuds: list[pg.Noeud_Pondere] = []
        bfs(root, collecter_noeuds)

        graphe = pg.Graph()
        graphe.add_noeuds(noeuds)

        return graphe
    
    initialiser()

def bfs(start, action=None) -> None:
    queue = [start]
    visited = set()
    visited.add(start)

    profondeur: int = 0
    nb_niv: int = 1
    nb_next_niv: int = 0
    nb_niv_precedents: int = 0

    while queue:
        current = queue.pop(0)

        if action:
            action(current, profondeur, nb_niv_precedents)

        for v in current.voisins:
            if v not in visited:
                queue.append(v)
                visited.add(v)
                nb_next_niv += 1

        nb_niv -= 1
        if nb_niv == 0:
            profondeur += 1
            nb_niv_precedents += nb_next_niv
            nb_niv = nb_next_niv
            nb_next_niv = 0


if __name__ == "__main__":
    interface()