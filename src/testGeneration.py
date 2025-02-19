import prototypeGraphe as pg
from numpy.random import normal

def generer_arbre() -> pg.Noeud:
    #creer les enfants d'un noeud
    def generer_enfants(noeud: pg.Noeud, p: int) -> None:
        nonlocal nbNextNiv

        nb = nb_enfants(p)

        for i in range(nb):
            nouveauNoeud = pg.Noeud(nbNoeuds)
            nbNoeuds += 1

            noeud.add_voisin(nouveauNoeud)
            queue.append(nouveauNoeud)
            nbNextNiv += 1

    #helper de generer_enfants
    def nb_enfants(p: int) -> int:
        mean : float = (-1)*p + 3
        std_div: float = (1/3)*p + 1

        nbAl = normal(loc = mean, scale = std_div)

        if nbAl < 0:
            nbAl = 0

        return int(nbAl)
    
    #Initialisation des variables
    root = pg.Noeud(0)
    nbNoeuds = 1 #TODO Enlever une fois que générer une image n'est plus nécessaire
    queue: list[pg.Noeud] = []
    profondeur: int = 0
    nbNiv: int = 1
    nbNextNiv: int = 0

    #Navigation dans l'arbre
    queue.append(root)

    while len(queue) != 0:
        current = queue.pop(0)
        generer_enfants(current, profondeur)

        nbNiv -= 1
        if nbNiv == 0:
            profondeur += 1
            nbNiv = nbNextNiv
            nbNextNiv = 0
    
    return root

if __name__ == "__main__":
    root = generer_arbre()
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

    print(graphe)
    graphe.afficher()