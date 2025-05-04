import math

from pygame import Vector2

import classes_graphe as cg
import random
from numpy.random import normal

#Variables de génération
nb_noeuds_cible: int = random.randint(8,10) #Nombre total de noeuds à générer
nb_iter_forces: int = 50 #Nombre d'itérations pour appliquer les forces
connect_chance: float = 0.3 #Chance de connexion entre les noeuds
taux_mean: float = -1 #Taux de croissance de la médiane de la distribution normale
initial_mean: float = 3 #Valeur de initiale de la médiane de la distribution normale
taux_std_dev: float = 1/3 #Taux de croissance de l'écart type de la distribution normale
initial_std_dev: float = 1 #Valeur de initiale de l'écart type de la distribution normale

def generer_arbre() -> cg.NoeudGeneration:
    """
    Génère un arbre de noeuds de type NoeudGeneration. Chaque noeud a un nombre d'enfants aléatoire basé sur une distribution normale qui dépend de la profondeur.
    Args:
        None
    Returns:
        cg.NoeudGeneration: Le noeud racine de l'arbre généré.
    """
    def traverser_arbre(noeuds: list[cg.NoeudGeneration]) -> None:
        """
        Traverse l'arbre de noeuds et génère des enfants pour chaque noeud.
        Args:
            noeuds (list[cg.NoeudGeneration]): Liste des noeuds à traverser.
        Returns:
            None
        """
        i: int = 0
        profondeur: int = 0
        first_of_next_level: int = 1
        not_set: bool = False

        while i < len(noeuds):
            if noeuds[i].nb == first_of_next_level:
                profondeur += 1
                not_set = True

            generer_enfants(noeuds[i], noeuds, profondeur)

            if not_set and len(noeuds[i].voisins) != 0:
                not_set = False
                first_of_next_level = min(v.nb for v in noeuds[i].voisins)

            i += 1

    def generer_enfants(current: cg.NoeudGeneration, noeuds: list[cg.NoeudGeneration], profondeur: int) -> None:
        """
        Génère des enfants pour un noeud donné en fonction de la profondeur.
        Args:
            current (cg.NoeudGeneration): Le noeud actuel.
            noeuds (list[cg.NoeudGeneration]): Liste des noeuds générés jusqu'à présent.
            profondeur (int): La profondeur actuelle dans l'arbre.
        Returns:
            None
        """      
        if len(current.voisins) != 0: #Évite de générer des enfants inutilement lors d'une ennième itération
            return

        nb = nb_enfants(profondeur)
        for _ in range(nb):
            if len(noeuds) >= nb_noeuds_cible:
                return

            enfant = cg.NoeudGeneration(len(noeuds))
            current.add_voisin(enfant)
            noeuds.append(enfant)

    def nb_enfants(profondeur: int) -> int:
        """
        Calcule le nombre d'enfants pour un noeud donné en fonction de la profondeur.
        Args:
            profondeur (int): La profondeur actuelle dans l'arbre.
        Returns:
            int: Le nombre d'enfants générés.
        """
        mean : float = taux_mean * profondeur + initial_mean
        std_div: float = taux_std_dev * profondeur + initial_std_dev

        nbAl: float = normal(loc = mean, scale = std_div)

        if nbAl < 0:
            nbAl = 0
        elif nbAl > 3:
            nbAl = 3

        return int(nbAl)
    
    root = cg.NoeudGeneration(0)
    noeuds: list[cg.NoeudGeneration] = [root]

    while len(noeuds) < nb_noeuds_cible:
        traverser_arbre(noeuds)
    
    return root

def connecter_branches(root: cg.NoeudGeneration) -> cg.NoeudGeneration:
    """
    Connecte les branches de l'arbre généré.
    Args:
        root (cg.NoeudGeneration): Le noeud racine de l'arbre.
    Returns:
        cg.NoeudGeneration: Le noeud racine de l'arbre avec les connexions ajoutées.
    """
    def connecter_noeud(noeud: cg.NoeudGeneration, _) -> None:
        """
        Connecte un noeud à un voisin à droite avec une certaine probabilité.
        Args:
            noeud (cg.NoeudGeneration): Le noeud actuel.
            _: Non utilisé.
        Returns:
            None
        """
        if random.random() > connect_chance:
            return
        
        voisin: cg.NoeudGeneration = trouver_voisin_droite(noeud, root)

        if voisin != None:
            noeud.add_voisin(voisin)

    def trouver_voisin_droite(noeud: cg.NoeudGeneration, root: cg.NoeudGeneration) -> cg.NoeudGeneration:
        """
        Trouve le voisin de droite d'un noeud en utilisant bfs et un helper.
        Args:
            noeud (cg.NoeudGeneration): Le noeud actuel.
            root (cg.NoeudGeneration): Le noeud racine de l'arbre.
        Returns:
            cg.NoeudGeneration: Le voisin de droite du noeud ou None s'il n'existe pas."""
        profondeur_noeud: int = -1
        profondeur_cible: int = -1
        voisin = None

        def trouver_voisin_droite_helper(current: cg.NoeudGeneration, infos: tuple) -> None:
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

def attribuer_poids(root: cg.NoeudGeneration) -> cg.NoeudPondere:
    """
    Attribue des coordonnées aux noeuds de l'arbre en utilisant un algorithme de disposition par forces.
    Args:
        root (cg.NoeudGeneration): Le noeud racine de l'arbre.
    Returns:
        cg.NoeudPondere: Le noeud racine de l'arbre avec les coordonnées attribuées.
    """
    def initialiser_coord(root: cg.NoeudGeneration) -> cg.NoeudPondere:
        """
        Initialise les coordonnées des noeuds avec des coordonnées prédifinies. Fait la transition entre NoeudGeneration et NoeudPondere.
        Args:
            root (cg.NoeudGeneration): Le noeud racine de l'arbre.
        Returns:
            cg.NoeudPondere: Le noeud racine de l'arbre avec les coordonnées attribuées.
        """
        profondeur_max = trouver_profondeur(root)
        root_pondere = None
        lien_graphe: dict[cg.NoeudGeneration, cg.NoeudPondere] = dict()

        def initialiser_lien_graphe(current: cg.NoeudGeneration, _) -> None:
            nonlocal root_pondere, lien_graphe

            current_pondere = cg.NoeudPondere()
            lien_graphe[current] = current_pondere

            if current == root:
                root_pondere = current_pondere

        def initialiser_graphe_pondere(current: cg.NoeudGeneration, _) -> None:
            current_pondere = lien_graphe[current]

            for v in current.voisins:
                current_pondere.add_voisin(lien_graphe[v])

        def initialiser_coord_helper(current: cg.NoeudGeneration, infos: tuple) -> None:
            profondeur, nb_niv_actuel, nb_niv_precedents = infos

            current_pondere = lien_graphe[current]
            current_pondere.coord = [current.nb - nb_niv_precedents - int(nb_niv_actuel/2), profondeur_max - profondeur]

        bfs(root, initialiser_lien_graphe)
        bfs(root, initialiser_graphe_pondere)
        bfs(root, initialiser_coord_helper)
        return root_pondere

    def trouver_profondeur(root: cg.NoeudGeneration) -> int:
        """
        Trouve la profondeur maximale de l'arbre en utilisant bfs et un helper.
        Args:
            root (cg.NoeudGeneration): Le noeud racine de l'arbre.
        Returns:
            int: La profondeur maximale de l'arbre.
        """
        profondeur_max: int = 0

        def trouver_profondeur_helper(current: cg.NoeudGeneration, infos: tuple)-> None:
            nonlocal profondeur_max

            profondeur, _, __ = infos

            profondeur_max = max(profondeur_max, profondeur)

        bfs(root, trouver_profondeur_helper)
        return profondeur_max

    #Applique les forces sur tous les noeuds
    def calculer_force(root_pondere: cg.NoeudPondere, deplacement_attraction: float, deplacement_repulsion: float) -> None:
        """
        Applique les forces de répulsion et d'attraction sur tous les noeuds de l'arbre en utilisant bfs et un helper.
        Args:
            root_pondere (cg.NoeudPondere): Le noeud racine de l'arbre avec les coordonnées attribuées.
            deplacement_attraction (float): Le facteur d'attraction.
            deplacement_repulsion (float): Le facteur de répulsion.
        Returns:
            None
        """
        def calculer_force_helper(noeud: cg.NoeudPondere, _) -> None:
            calculer_repulsion(noeud, root_pondere, deplacement_repulsion)
            calculer_attraction(noeud, deplacement_attraction)
        
        bfs(root_pondere, calculer_force_helper)

    #Applique une force de repulsion sur un noeud
    def calculer_repulsion(noeud: cg.NoeudPondere, root_pondere: cg.NoeudPondere, deplacement_repulsion: float) -> None:
        """
        Applique une force de répulsion sur un noeud en fonction de la distance entre les noeuds en utilisant bfs et un helper.
        Args:
            noeud (cg.NoeudPondere): Le noeud actuel.
            root_pondere (cg.NoeudPondere): Le noeud racine de l'arbre avec les coordonnées attribuées.
            deplacement_repulsion (float): Le facteur de répulsion.
            None
        """
        def calculer_repulsion_helper(autre: cg.NoeudPondere, _) -> None:
            if autre == noeud:
                return
            
            dx = noeud.coord[0] - autre.coord[0]
            dy = noeud.coord[1] - autre.coord[1]
            dist = (dx ** 2 + dy ** 2) ** 0.5

            force_x, force_y = deplacement_repulsion * dx / (dist ** 2), deplacement_repulsion * dy / (dist ** 2)
            noeud.coord = [noeud.coord[0] + force_x, noeud.coord[1] + force_y]

        bfs(root_pondere, calculer_repulsion_helper)

    #Applique une force d'attraction sur un noeud
    def calculer_attraction(noeud: cg.NoeudPondere, deplacement_attraction: float) -> None:
        """
        Applique une force d'attraction sur un noeud en fonction de la distance avec les noeuds voisins.
        Args:
            noeud (cg.NoeudPondere): Le noeud actuel.
            deplacement_attraction (float): Le facteur d'attraction.
        Returns:
            None
        """
        for v in noeud.voisins:
            dx = v.coord[0] - noeud.coord[0]
            dy = v.coord[1] - noeud.coord[1]
            force_x, force_y = deplacement_attraction * dx, deplacement_attraction * dy

            noeud.coord = [noeud.coord[0] + force_x, noeud.coord[1] + force_y]

    root_pondere = initialiser_coord(root)
    deplacement_attraction: float = 0.02 + (random.random() * 0.01 - 0.005)
    deplacement_repulsion: float = 0.02 + (random.random() * 0.01 - 0.005)

    for _ in range(nb_iter_forces):
        calculer_force(root_pondere, deplacement_attraction, deplacement_repulsion)

    return root_pondere

def bfs(start, action=None) -> None:
    """
    Effectue une recherche en largeur (BFS) sur un graphe à partir d'un noeud de départ.
    Args:
        start (cg.Noeud): Le noeud de départ pour la recherche.
        action (callable): Une fonction à appeler pour chaque noeud visité.
    Returns:
        None
    """
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

def generer_graphe(HAUTEUR_SOL, MAP_LIMIT_X,nb_salles_initiales) -> cg.Graphe:
    """
    Génère un graphe à partir d'un arbre de noeuds en utilisant des paramètres de génération.
    Args:
        HAUTEUR_SOL (int): La hauteur du sol pour le nid.
        MAP_LIMIT_X (int): La largeur maximale du nid.
    Returns:
        cg.Graphe: Le graphe généré.
    """
    def collecter_noeuds(root: cg.NoeudPondere, _) -> None:
        """
        Collecte les noeuds de l'arbre en utilisant bfs et un helper.
        Args:
            root (cg.NoeudPondere): Le noeud racine de l'arbre.
            _: Non utilisé.
        Returns:
            None
        """
        noeuds.append(root)

    def convertir_coord(graphe: cg.Graphe, scale,nb_salles_initiales) -> None:
        """
        Convertit les coordonnées des noeuds du graphe en fonction de l'échelle et ajuste la position de la salle de sortie.
        Args:
            graphe (cg.Graphe): Le graphe à convertir.
            scale (float): L'échelle de conversion.
        Returns:
            None
        """
        noeud_min: cg.Salle = None #Salle la plus haute
        salle_min: cg.Salle = None #Salle la plus haute qui n'est pas une intersection

        for salle in graphe.salles:
            if noeud_min is None or salle.noeud.coord[1] < noeud_min.noeud.coord[1]:
                noeud_min = salle
                
                if salle.type == cg.TypeSalle.SALLE:
                    salle_min = salle

        if salle_min != noeud_min:
            nouveau_x = noeud_min.noeud.coord[0] + 2 * random.random() - 1
            nouveau_y = noeud_min.noeud.coord[1]

            salle_min = cg.Salle(noeud = cg.NoeudPondere([nouveau_x, nouveau_y]), type = cg.TypeSalle.SORTIE)
            graphe.add_salle(salle_min, [noeud_min])
        else:
            salle_min.type = cg.TypeSalle.SORTIE
        
        dy: float = scale * salle_min.noeud.coord[1] - HAUTEUR_SOL

        for salle in graphe.salles:
            salle.noeud.coord = [(MAP_LIMIT_X/2) + salle.noeud.coord[0] * scale,
                                salle.noeud.coord[1] * scale - dy]
            
            if salle != salle_min:
                salle.noeud.coord[1] += 75

    valide: bool = False
    scale = 200
    while not valide:
        root = generer_arbre()
        connecter_branches(root)
        root = attribuer_poids(root)

        noeuds: list[cg.NoeudPondere] = []
        bfs(root, collecter_noeuds)

        graphe = cg.Graphe()
        graphe.initialiser_graphe(noeuds)
        convertir_coord(graphe, scale,nb_salles_initiales)
        
        valide = graphe.verifier_graphe(scale, HAUTEUR_SOL,nb_salles_initiales)

    #assigner rôle des permières salles
    coords_sortie=(0,0)
    salles_salle=[]
    for salle in graphe.salles: #trouver sortie et liste de toutes les salles de type salle
        if salle.type == cg.TypeSalle.SORTIE:
            coords_sortie = salle.noeud.coord
        elif salle.type == cg.TypeSalle.SALLE:
            salles_salle.append(salle)

    def distance_sortie(salle):
        return (Vector2(salle.noeud.coord)-Vector2(coords_sortie)).magnitude()

    for i in range(len(salles_salle)): # sort selon distance
        for j in range(len(salles_salle) - 1 - i):
            if distance_sortie(salles_salle[j]) > distance_sortie(salles_salle[j + 1]):
                salles_salle[j], salles_salle[j + 1] = salles_salle[j + 1], salles_salle[j]

    #donner rôle selon distance
    salles_salle[-1].type=cg.TypeSalle.THRONE
    if nb_salles_initiales > 2 :
        salles_salle[0].type=cg.TypeSalle.BANQUE
        if nb_salles_initiales > 3 :
            salles_salle[1].type=cg.TypeSalle.MEULE
            if nb_salles_initiales > 4:
                salles_salle[2].type = cg.TypeSalle.ENCLUME

    return graphe