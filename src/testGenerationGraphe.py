import prototypeGraphe as pg
import random
from numpy.random import normal

def generer_arbre(nb_noeuds_cible: int, taux_mean: float, initial_mean: float, taux_std_dev: float, initial_std_dev: float) -> pg.Noeud_Generation:
    def traverser_arbre(root: pg.Noeud_Generation, noeuds: list[pg.Noeud_Generation]) -> None:
        i: int = 0
        while i < len(noeuds):
            generer_enfants(noeuds[i], noeuds, root.nb + 1)
            i += 1

    #Créer les enfants d'un noeud
    def generer_enfants(current: pg.Noeud_Generation, noeuds: list[pg.Noeud_Generation], profondeur: int) -> None:
        nonlocal nb_noeuds
        
        if len(current.voisins) != 0: #Évite de générer des enfants inutilement lors d'une ennième itération
            return

        nb = nb_enfants(profondeur)
        for _ in range(nb):
            if nb_noeuds >= nb_noeuds_cible:
                return

            enfant = pg.Noeud_Generation(nb_noeuds)
            nb_noeuds += 1

            current.add_voisin(enfant)

            noeuds.append(enfant)

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
    noeuds: list[pg.Noeud_Generation] = [root]
    nb_noeuds = 1

    while nb_noeuds < nb_noeuds_cible:
        traverser_arbre(root, noeuds)
    
    return root

def connecter_branches(root: pg.Noeud_Generation, connect_chance: float) -> pg.Noeud_Generation:
    #Connecte ou non le noeud à un noeud à droite
    def connecter_noeud(noeud: pg.Noeud_Generation, _) -> None:
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

        def trouver_voisin_droite_helper(current: pg.Noeud_Generation, infos: tuple) -> None:
            nonlocal profondeur_noeud, profondeur_cible, voisin

            profondeur, _, __ = infos

            if current.nb == noeud.nb:
                profondeur_noeud = profondeur
            elif current.nb == noeud.nb + 1:
                profondeur_cible = profondeur
                voisin = current

        bfs(root, trouver_voisin_droite_helper)

        return voisin if profondeur_noeud == profondeur_cible else None

    bfs(root, connecter_noeud)

#Utilise un algorithme de disposition par forces
def attribuer_poids(root: pg.Noeud_Generation, nb_iter_forces: int) -> pg.Noeud_Pondere:
    #Créer aléatoirment les coordonnées des noeuds
    def initialiser_coord(root: pg.Noeud_Generation) -> pg.Noeud_Pondere:
        profondeur_max = trouver_profondeur(root)
        root_pondere = None
        lien_graphe: dict[pg.Noeud_Generation, pg.Noeud_Pondere] = dict()

        def initialiser_lien_graphe(current: pg.Noeud_Generation, _) -> None:
            nonlocal root_pondere, lien_graphe

            current_pondere = pg.Noeud_Pondere()
            lien_graphe[current] = current_pondere

            if current == root:
                root_pondere = current_pondere

        def initialiser_graphe_pondere(current: pg.Noeud_Generation, _) -> None:
            current_pondere = lien_graphe[current]

            for v in current.voisins:
                current_pondere.add_voisin(lien_graphe[v])

        def initialiser_coord_helper(current: pg.Noeud_Generation, infos: tuple) -> None:
            profondeur, nb_niv_actuel, nb_niv_precedents = infos

            current_pondere = lien_graphe[current]
            current_pondere.coord = [current.nb - nb_niv_precedents - int(nb_niv_actuel/2), profondeur_max - profondeur]

        bfs(root, initialiser_lien_graphe)
        bfs(root, initialiser_graphe_pondere)
        bfs(root, initialiser_coord_helper)
        return root_pondere

    def trouver_profondeur(root: pg.Noeud_Generation) -> int:
        profondeur_max: int = 0

        def trouver_profondeur_helper(current: pg.Noeud_Generation, infos: tuple)-> None:
            nonlocal profondeur_max

            profondeur, _, __ = infos

            profondeur_max = max(profondeur_max, profondeur)

        bfs(root, trouver_profondeur_helper)
        return profondeur_max

    #Applique les forces sur tous les noeuds
    def calculer_force(root_pondere: pg.Noeud_Pondere) -> None:
        def calculer_force_helper(noeud: pg.Noeud_Pondere, _) -> None:
            calculer_repulsion(noeud, root_pondere)
            calculer_attraction(noeud)
        
        bfs(root_pondere, calculer_force_helper)

    #Applique une force de repulsion sur un noeud
    def calculer_repulsion(noeud: pg.Noeud_Pondere, root_pondere: pg.Noeud_Pondere) -> None:
        def calculer_repulsion_helper(autre: pg.Noeud_Pondere, _) -> None:
            if autre == noeud:
                return
            
            dx = noeud.coord[0] - autre.coord[0]
            dy = noeud.coord[1] - autre.coord[1]
            dist = (dx ** 2 + dy ** 2) ** 0.5

            force_x, force_y = 0.01 * dx / (dist ** 2), 0.01 * dy / (dist ** 2)
            noeud.coord = [noeud.coord[0] + force_x, noeud.coord[1] + force_y]

        bfs(root_pondere, calculer_repulsion_helper)

    #Applique une force d'attraction sur un noeud
    def calculer_attraction(noeud: pg.Noeud_Pondere) -> None:
        for v in noeud.voisins:
            dx = v.coord[0] - noeud.coord[0]
            dy = v.coord[1] - noeud.coord[1]
            force_x, force_y = 0.01 * dx, 0.01 * dy

            noeud.coord = [noeud.coord[0] + force_x, noeud.coord[1] + force_y]

    root_pondere = initialiser_coord(root)

    for _ in range(nb_iter_forces):
        calculer_force(root_pondere)

    return root_pondere

def bfs(start, action=None) -> None:
    queue = [start]
    visited = set()
    visited.add(start)

    profondeur: int = 0
    nb_restants: int = 1
    nb_niv_actuel: int = 1
    nb_next_niv: int = 0
    nb_niv_precedents: int = 0

    while queue:
        current = queue.pop(0)

        if action:
            infos = (profondeur, nb_niv_actuel, nb_niv_precedents)
            action(current, infos)

        for v in current.voisins:
            if v not in visited:
                queue.append(v)
                visited.add(v)
                nb_next_niv += 1

        nb_restants -= 1
        if nb_restants == 0:
            profondeur += 1
            nb_niv_precedents += nb_niv_actuel
            nb_niv_actuel = nb_next_niv
            nb_restants = nb_next_niv
            nb_next_niv = 0

def generer_graphe(infos_gen_arbre, connect_chance, nb_iter_forces, infos_convertion_coord) -> pg.Graph:
        def collecter_noeuds(root: pg.Noeud_Pondere, _) -> None:
            noeuds.append(root)

        def convertir_coord(graphe: pg.Graph, scale = 50) -> None:
            noeud_min: pg.Salle = None #Salle la plus haute
            salle_min: pg.Salle = None #Salle la plus haute qui n'est pas une intersection

            for salle in graphe.salles:
                if noeud_min is None or salle.noeud.coord[1] < noeud_min.noeud.coord[1]:
                    noeud_min = salle
                    
                    if salle.type == pg.TypeSalle.SALLE:
                        salle_min = salle

            if salle_min != noeud_min:
                nouveau_x = noeud_min.noeud.coord[0] + 2 * random.random() - 1
                nouveau_y = noeud_min.noeud.coord[1]

                salle_min = pg.Salle(noeud = pg.Noeud_Pondere([nouveau_x, nouveau_y]), type = pg.TypeSalle.SORTIE)
                graphe.add_salle(salle_min, [noeud_min])
            else:
                salle_min.type = pg.TypeSalle.SORTIE
            
            dy: float = scale * salle_min.noeud.coord[1] - HAUTEUR_SOL

            for salle in graphe.salles:
                salle.noeud.coord = [(MAP_LIMIT_X/2) + salle.noeud.coord[0] * scale,
                                    salle.noeud.coord[1] * scale - dy]
                
                if salle != salle_min:
                    salle.noeud.coord[1] += 75

        nb_noeuds_cible, taux_mean, initial_mean, taux_std_dev, initial_std_dev = infos_gen_arbre
        HAUTEUR_SOL, MAP_LIMIT_X = infos_convertion_coord

        valide: bool = False
        while not valide:
            root = generer_arbre(nb_noeuds_cible, taux_mean, initial_mean, taux_std_dev, initial_std_dev)
            connecter_branches(root, connect_chance)
            root = attribuer_poids(root, nb_iter_forces)

            noeuds: list[pg.Noeud_Pondere] = []
            bfs(root, collecter_noeuds)

            graphe = pg.Graph()
            graphe.initialiser_graphe(noeuds)
            convertir_coord(graphe)
            
            valide = graphe.verifier_graphe()

        return graphe