import prototypeGraphe as pg
import random
from numpy.random import normal

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
        mean : float = (-1)*profondeur + 3
        std_div: float = (1/3)*profondeur + 1

        nbAl: float = normal(loc = mean, scale = std_div)

        if nbAl < 0:
            nbAl = 0

        if nbAl > 3:
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
        if random.random() > 0.50:
            return
        
        voisin: pg.Noeud = trouver_voisin_droite(noeud)

        if voisin != None:
            noeud.add_voisin(voisin)

    #retourne le voisin de droite d'un noeud à un certain niveau ou None s'il n'existe pas
    def trouver_voisin_droite(noeud: pg.Noeud) -> pg.Noeud:
        queue: list[pg.Noeud] = []
        queue.append(root)

        nb_premier: int = 0 #numéro du premier noeud du prochain niveau

        while len(queue) != 0:
            current = queue.pop(0)

            if current.nb == noeud.nb+1 and current.nb < nb_premier:
                return current
            elif current.nb == noeud.nb+1:
                return None
            
            for child in current.voisins:
                queue.append(child)

                if current.nb >= nb_premier or child.nb < nb_premier:
                    nb_premier = child.nb

        return None

    #Initialisation des variables
    stack: list[pg.Noeud] = []
    stack.append(root)

    #Navigation dans l'arbre
    while len(stack) != 0:
        current: pg.Noeud = stack.pop()
        for child in current.voisins:
            stack.append(child)

        connecter_noeud(current)

if __name__ == "__main__":
    root = generer_arbre()
    connecter_branches(root)
    noeuds = []
    queue = []

    queue.append(root)

    while len(queue) != 0:
        current = queue.pop(0)
        noeuds.append(current)

        for v in current.voisins:
            queue.append(v)

    graphe = pg.Graph()
    graphe.add_noeuds(noeuds)

    graphe.afficher()