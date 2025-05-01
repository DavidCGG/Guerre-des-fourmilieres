from enum import Enum
from pygame import Vector2

class NoeudGeneration:
    """
    Représente le noeud d'un graphe
    Attributs :
        nb (int) : Numéro du noeud.
        voisins (set[NoeudGeneration]) : Ensemble des voisins du noeud.
    """
    
    def __init__(self, nb = -1, voisins = None):
        self.nb: int = nb
        self.voisins: set[NoeudGeneration] = voisins if voisins is not None else set()

    def add_voisin(self, voisin) -> None:
        """
        Ajoute un voisin au noeud
        Args:
            voisin (NoeudGeneration): Voisin à ajouter
        Returns:
            None
        """
        self.voisins.add(voisin)       

class NoeudPondere:
    """
    Représente un noeud dans un graphe pondéré 2D.
    Attributs :
        coord (list[float, float]) : Coordonnées [x, y] du noeud.
        voisins (dict[NoeudPondere, float]) : Dictionnaire des voisins avec le poids (distance) de la connexion.
    """

    def __init__(self, coord = [-1,-1], voisins = None):
        self.coord: list[float, float] = coord
        self.voisins: dict[NoeudPondere: float] = voisins if voisins is not None else dict()

    def connecter_noeud(self, voisin) -> None:
        """
        Connecte le noeud à un voisin et l'inverse en initialisant la distance entre les deux noeuds
        Args:
            voisin (NoeudPondere): Voisin à connecter
        Returns:
            None
        """
        distance = ((self.coord[0] - voisin.coord[0]) ** 2 + (self.coord[1] - voisin.coord[1]) ** 2) ** 0.5
        self.voisins[voisin] = distance
        voisin.voisins[self] = distance

    def add_voisin(self, voisin, poid = -1) -> None:
        """
        Ajoute un voisin au noeud
        Args:
            voisin (NoeudPondere): Voisin à ajouter
            poid (float): Poids de la connexion
        Returns:
            None
        """
        self.voisins[voisin] = poid   
    
    def remove_voisin(self, voisin) -> None:
        """
        Supprime un voisin du noeud
        Args:
            voisin (NoeudPondere): Voisin à supprimer
        Returns:
            None
        """
        self.voisins.pop(voisin)

class TypeSalle(Enum):
    """
    Enumération des types de salles dans un nid de fourmis.
    Chaque type est associé à un rayon et un nom.
    Membres :
        INDEFINI : Salle non définie.
        INTERSECTION : Point de jonction entre tunnels.
        SALLE : Salle ayant un rôle quelconque.
        SORTIE : Sortie du nid.
    """

    INDEFINI = (40, "indéfini")
    INTERSECTION = (40, "intersection")
    SALLE = (120, "salle","salle_vide.png")
    SORTIE = (40, "sortie")
    ENCLUME = (120, "enclume","enclume.png")

class Salle:
    """
    Représente une salle dans un graphe.
    Attributs :
        noeud (NoeudPondere) : Noeud associé à la salle.
        tunnels (set[Tunnel]) : Ensemble des tunnels connectés à la salle.
        type (TypeSalle) : Type de la salle (défini par l'énumération TypeSalle).
    """

    def __init__(self, noeud, tunnels = None, type = None):
        self.noeud: NoeudPondere = noeud
        self.tunnels: set[Tunnel] = set(tunnels) if tunnels is not None else set()
        self.type: TypeSalle = type

    def intersecte_salle(self, autre) -> bool:
        """
        Vérifie si deux salles se superposent.
        Args:
            autre (Salle): Autre salle à vérifier.
        Returns:
            bool: True si les salles se superposent, False sinon.
        """
        coord1 = self.noeud.coord
        coord2 = autre.noeud.coord

        distance = ((coord1[0] - coord2[0]) ** 2 + (coord1[1] - coord2[1]) ** 2) ** 0.5
        distance_min = self.type.value[0] + autre.type.value[0]

        return distance < distance_min

    def intersecte_tunnel(self, tunnel) -> bool:
        """
        Vérifie si une salle se superpose à un tunnel.
        Args:
            tunnel (Tunnel): Tunnel à vérifier.
        Returns:
            bool: True si la salle se superpose au tunnel, False sinon.
        """
        x1, y1 = tunnel.depart.noeud.coord
        x2, y2 = tunnel.arrivee.noeud.coord
        cx, cy = self.noeud.coord

        #Vecteur directeur de la droite
        droite = Vector2(x2 - x1, y2 - y1)

        #Vecteur entre le centre de la salle et le point de départ du tunnel
        droite_cercle = Vector2(cx - x1, cy - y1)

        #Rapport entre le vecteur directeur et
        #la projection du vecteur entre le centre de la salle et le point de départ du tunnel sur celui-ci
        t = max(0, min(1, (droite.x * droite_cercle.x + droite.y * droite_cercle.y) / (droite.x ** 2 + droite.y ** 2)))

        #Point le plus proche de la salle sur la droite
        closest_x = x1 + t * droite.x
        closest_y = y1 + t * droite.y

        #Distance au centre
        distance = ((closest_x - cx) ** 2 + (closest_y - cy) ** 2) ** 0.5
        rayon = self.type.value[0] + tunnel.largeur / 2

        return distance <= rayon
   
class Tunnel:
    """
    Représente un tunnel entre deux salles dans un graphe.
    Attributs :
        depart (Salle) : Une première salle reliée au tunnel.
        arrivee (Salle) : Une seconde salle reliée au tunnel.
        largeur (int) : Largeur du tunnel.
    """
    def __init__(self, depart = None, arrivee = None, largeur = 80):
        """
        Constructeur de la classe Tunnel. Ajoute le tunnel aux salles et connecte leurs noeuds.
        Args:
            depart (Salle): Salle de départ.
            arrivee (Salle): Salle d'arrivée.
            largeur (int): Largeur du tunnel.
        """
        self.depart: Salle = depart
        self.arrivee: Salle = arrivee
        self.largeur: int = largeur

        depart.tunnels.add(self)
        arrivee.tunnels.add(self)
        depart.noeud.connecter_noeud(arrivee.noeud)
    
    def intersecte(self, autre) -> bool:
        """
        Vérifie si deux tunnels se superposent.
        Args:
            autre (Tunnel): Autre tunnel à vérifier.
        Returns:
            bool: True si les tunnels se superposent, False sinon.
        """
        def get_rectangle(tunnel) -> tuple[int, int, int, int]:
            """
            Crée un rectangle représentant le tunnel.
            Args:
                tunnel (Tunnel): Tunnel à représenter.
            Returns:
                list[Vector2]: Liste de points représentant les coins du rectangle.
            """
            scale_largeur: float = 2 #Sert à bien espacer les tunnels

            direction: Vector2 = Vector2(tunnel.arrivee.noeud.coord[0] - tunnel.depart.noeud.coord[0],
                                         tunnel.arrivee.noeud.coord[1] - tunnel.depart.noeud.coord[1]).normalize()
            normal: Vector2 = Vector2(-direction.y, direction.x)
            offset: Vector2 = normal * (scale_largeur * self.largeur / 2)

            p1 = Vector2(tunnel.depart.noeud.coord) + offset
            p2 = Vector2(tunnel.arrivee.noeud.coord) + offset
            p3 = Vector2(tunnel.arrivee.noeud.coord) - offset
            p4 = Vector2(tunnel.depart.noeud.coord) - offset

            return [p1, p2, p3, p4]
        
        def intersection_segments(a1, a2, b1, b2):
            """
            Vérifie si deux segments de droite se croisent. Utilise la fonction ccw pour déterminer l'orientation des points.
            Args:
                a1 (Vector2): Premier point du premier segment.
                a2 (Vector2): Deuxième point du premier segment.
                b1 (Vector2): Premier point du deuxième segment.
                b2 (Vector2): Deuxième point du deuxième segment.
            Returns:
                bool: True si les segments se croisent, False sinon.
            """
            def ccw(p1, p2, p3):
                return (p3.y - p1.y) * (p2.x - p1.x) > (p2.y - p1.y) * (p3.x - p1.x)
            
            return ccw(a1, b1, b2) != ccw(a2, b1, b2) and ccw(b1, a1, a2) != ccw(b2, a1, a2)
        
        rect1 = get_rectangle(self)
        rect2 = get_rectangle(autre)

        for i in range(len(rect1)):
            a1 = rect1[i]
            a2 = rect1[(i + 1) % len(rect1)]
            for j in range(len(rect2)):
                b1 = rect2[j]
                b2 = rect2[(j + 1) % len(rect2)]
                if intersection_segments(a1, a2, b1, b2):
                    return True
                
        return False
        
class Graphe:
    """
    Représente un graphe de salles et de tunnels.
    Attributs :
        salles (set[Salle]) : Ensemble des salles du graphe.
        tunnels (set[Tunnel]) : Ensemble des tunnels du graphe.
    """
    def __init__(self, salles = None, tunnels = None):
        self.salles: set[Salle] = salles if salles is not None else set()
        self.tunnels: set[Tunnel] = tunnels if tunnels is not None else set()

    def initialiser_graphe(self, noeuds: list[NoeudPondere]) -> None:
        """
        Initialise le graphe en connectant les noeuds et en créant les salles et tunnels.
        Args:
            noeuds (list[NoeudPondere]): Liste de noeuds à initialiser.
        Returns:
            None
        """
        def connecter_noeuds(noeuds) -> None:
            """
            Connecte les noeuds entre eux en ajoutant des voisins.
            Args:
                noeuds (list[NoeudPondere]): Liste de noeuds à connecter.
            Returns:
                None
            """
            for noeud in noeuds:
                for voisin in noeud.voisins:
                    noeud.connecter_noeud(voisin)

        def initialiser_salles(self, noeuds, lien_noeud_salle) -> None:
            """
            Initialise les salles en fonction des noeuds.
            Args:
                noeuds (list[NoeudPondere]): Liste de noeuds à initialiser.
                lien_noeud_salle (dict[NoeudPondere, Salle]): Dictionnaire liant les noeuds aux salles.
            Returns:
                None
            """
            for noeud in noeuds:
                salle = Salle(noeud)

                if len(salle.noeud.voisins) == 1: #Salle
                    salle.type = TypeSalle.SALLE
                else: #Intersection
                    salle.type = TypeSalle.INTERSECTION

                self.salles.add(salle)
                lien_noeud_salle[noeud] = salle
        
        def initialiser_tunnels(self, noeuds, lien_noeud_salle) -> None:
            """
            Initialise les tunnels en fonction des noeuds.
            Args:
                noeuds (list[NoeudPondere]): Liste de noeuds à initialiser.
                lien_noeud_salle (dict[NoeudPondere, Salle]): Dictionnaire liant les noeuds aux salles.
            Returns:
                None
            """
            visited = set()

            for noeud in noeuds:
                for voisin in noeud.voisins:
                    if voisin in visited:
                        continue

                    self.tunnels.add(Tunnel(lien_noeud_salle[noeud], lien_noeud_salle[voisin]))
                visited.add(noeud)

        lien_noeud_salle = dict()
        connecter_noeuds(noeuds)
        initialiser_salles(self, noeuds, lien_noeud_salle)
        initialiser_tunnels(self, noeuds, lien_noeud_salle)

    def verifier_graphe(self, scale, HAUTEUR_SOL) -> bool:
        """
        Vérifie si le graphe respecte les contraintes de superposition et de nombre de salles.
        Args:
            None
        Returns:
            bool: True si le graphe est valide, False sinon.
        """
        def verifier_nombre_salles() -> bool:
            """
            Vérifie si le nombre de salles autre que des intersections ou des sorties est compris entre 2 et 5.
            Args:
                None
            Returns:
                bool: True si le nombre de salles est valide, False sinon.
            """
            nb_salles: int = 0

            for salle in self.salles:
                if salle.type == TypeSalle.INTERSECTION or salle.type == TypeSalle.SORTIE:
                    continue
                nb_salles += 1

            return nb_salles == 3
        
        def verifier_longueur_tunnels(scale) -> bool:
            """
            Vérifie si les tunnels sont suffisamment longs.
            Args:
                None
            Returns:
                bool: True si les tunnels sont suffisament long, False sinon.
            """
            for tunnel in self.tunnels:
                longueur = ((tunnel.depart.noeud.coord[0] - tunnel.arrivee.noeud.coord[0]) ** 2 +
                            (tunnel.depart.noeud.coord[1] - tunnel.arrivee.noeud.coord[1]) ** 2) ** 0.5
                if longueur / scale < 1.5:
                    return False
            return True
        
        def verifier_angle_tunnels() -> bool:
            """
            Vérifie si les tunnels adjacents sont trop proches.
            Args:
                None
            Returns:
                bool: True si les tunnels adjacents ne sont pas trop proches, False sinon."""
            for tunnel1 in self.tunnels:
                for tunnel2 in self.tunnels:
                    if tunnel1 == tunnel2:
                        continue

                    if not (tunnel1.depart in (tunnel2.depart, tunnel2.arrivee) or 
                        tunnel1.arrivee in (tunnel2.depart, tunnel2.arrivee)):
                        continue

                    direction1: Vector2 = Vector2(tunnel1.arrivee.noeud.coord[0] - tunnel1.depart.noeud.coord[0],
                                            tunnel1.arrivee.noeud.coord[1] - tunnel1.depart.noeud.coord[1]).normalize()
                    direction2: Vector2 = Vector2(tunnel2.arrivee.noeud.coord[0] - tunnel2.depart.noeud.coord[0],
                                            tunnel2.arrivee.noeud.coord[1] - tunnel2.depart.noeud.coord[1]).normalize()
                    angle = direction1.angle_to(direction2)

                    if abs(angle) < 25:
                        return False
                    
            return True
        
        def verifier_sous_terre(HAUTEUR_SOL) -> bool:
            """
            Vérifie si les salles sont sous terre.
            Args:
                HAUTEUR_SOL (float): Hauteur du sol.
            Returns:
                bool: True si les salles sont sous terre, False sinon.
            """
            for salle in self.salles:
                if salle.type == TypeSalle.SORTIE:
                    continue

                if salle.noeud.coord[1] - salle.type.value[0] < HAUTEUR_SOL + HAUTEUR_SOL / 10:
                    return False
                
            return True
        
        def verifier_superpositions() -> bool:
            """
            Vérifie si les salles et tunnels se superposent.
            Args:
                None
            Returns:
                bool: True si les salles et les tunnels ne se supperposent pas, False sinon.
            """
            for salle1 in self.salles:
                for salle2 in self.salles:
                    if salle1 == salle2:
                        continue

                    if salle1.intersecte_salle(salle2):
                        return False    

            for tunnel1 in self.tunnels:
                for tunnel2 in self.tunnels:
                    if (tunnel1.depart in (tunnel2.depart, tunnel2.arrivee) or 
                        tunnel1.arrivee in (tunnel2.depart, tunnel2.arrivee)):
                        continue

                    if tunnel1.intersecte(tunnel2):
                        return False
                    
            for salle in self.salles:
                for tunnel in self.tunnels:
                    if tunnel in salle.tunnels:
                        continue

                    if salle.intersecte_tunnel(tunnel):
                        return False
                    
            return True
        
        valide: bool = True
        valide = valide and verifier_nombre_salles()
        valide = valide and verifier_longueur_tunnels(scale)
        valide = valide and verifier_angle_tunnels()
        valide = valide and verifier_sous_terre(HAUTEUR_SOL)
        valide = valide and verifier_superpositions()
        return valide
    
    def add_salle(self, salle: Salle, voisins:list[Salle]) -> None:
        """
        Ajoute une salle au graphe et creer les tunnels entre la salle et ses voisins.
        Args:
            salle (Salle): Salle à ajouter.
            voisins (list[Salle]): Liste de salles voisines.
        Returns:
            None
        """
        self.salles.add(salle)
        for voisin in voisins:
            tunnel = Tunnel(salle, voisin)
            self.tunnels.add(tunnel)

    def creer_salle_depuis_intersection(self, salle: Salle, coord_arrivee: list[float, float]) -> None:
        """
        Crée une nouvelle salle à partir d'une intersection et d'une coordonnée d'arrivée.
        Args:
            salle (Salle): Salle d'intersection.
            coord_arrivee (list[float, float]): Coordonnée de la nouvelle salle.
        Returns:
            None
        """
        #Initialisation de la nouvelle salle
        noeud_salle = NoeudPondere(coord_arrivee)
        salle_indefinie = Salle(noeud_salle, type = TypeSalle.INDEFINI)
        self.salles.add(salle_indefinie)

        #Création des nouveaux tunnels
        self.tunnels.add(Tunnel(salle, salle_indefinie))

    def creer_salle_depuis_tunnel(self, tunnel: Tunnel, coord_depart: list[float, float], coord_arrivee) -> None:     
        """
        Crée une nouvelle salle à partir d'un tunnel, du point de départ dans le tunnel et des coordonnées de la nouvelle salle.
        Args:
            tunnel (Tunnel): Tunnel à partir duquel la salle est créée.
            coord_depart (list[float, float]): Coordonnée de départ dans le tunnel.
            coord_arrivee (list[float, float]): Coordonnée de la nouvelle salle.
        Returns:
            None
        """
        #Initialisation des nouvelles salles
        noeud_intersection = NoeudPondere(coord_depart)
        salle_intersection = Salle(noeud_intersection, type = TypeSalle.INTERSECTION)

        noeud_salle = NoeudPondere(coord_arrivee)
        salle_indefinie = Salle(noeud_salle, type = TypeSalle.INDEFINI)

        self.salles.add(salle_intersection)
        self.salles.add(salle_indefinie)

        #Déconnexion des noeuds
        tunnel.depart.noeud.remove_voisin(tunnel.arrivee.noeud)
        tunnel.arrivee.noeud.remove_voisin(tunnel.depart.noeud)

        #Suppression des tunnels
        self.tunnels.remove(tunnel)
        for s in self.salles:
            for t in s.tunnels:
                if t == tunnel:
                    s.tunnels.remove(t)
                    break
        
        #Création des nouveaux tunnels
        self.tunnels.add(Tunnel(tunnel.depart, salle_intersection))
        self.tunnels.add(Tunnel(tunnel.arrivee, salle_intersection))
        self.tunnels.add(Tunnel(salle_intersection, salle_indefinie))

    def dijkstra(self, depart, arrivee) -> list[NoeudPondere]:
        """
        Implémente l'algorithme de Dijkstra pour trouver le chemin le plus court entre deux noeuds dans un graphe pondéré.
        Args:
            depart (NoeudPondere): Noeud de départ.
            arrivee (NoeudPondere): Noeud d'arrivée.
        Returns:
            list[NoeudPondere]: Liste des noeuds représentant le chemin le plus court.
        """
        def sort_queue(arr, distance) -> list[NoeudPondere]:
            """
            Trie la liste de noeuds en fonction de leur distance avec un algorithme de merge sort.
            Args:
                arr (list[NoeudPondere]): Liste de noeuds à trier.
                distance (dict[NoeudPondere, int]): Dictionnaire des distances.
            Returns:
                list[NoeudPondere]: Liste triée de noeuds.
            """
            if len(arr) <= 1:
                return arr

            mid = len(arr) // 2
            left_half = sort_queue(arr[:mid])
            right_half = sort_queue(arr[mid:])

            return merge(left_half, right_half, distance)

        def merge(left, right, distance) -> list[NoeudPondere]:
            """
            Fusionne deux listes triées en une seule liste triée.
            Args:
                left (list[NoeudPondere]): Première liste triée.
                right (list[NoeudPondere]): Deuxième liste triée.
                distance (dict[NoeudPondere, int]): Dictionnaire des distances.
            Returns:
                list[NoeudPondere]: Liste fusionnée et triée.
            """
            sorted_arr = []
            i, j = 0, 0

            while i < len(left) and j < len(right):
                if distance[left[i]] < distance[right[j]]:
                    sorted_arr.append(left[i])
                    i += 1
                else:
                    sorted_arr.append(right[j])
                    j += 1

            sorted_arr.extend(left[i:])
            sorted_arr.extend(right[j:])
            
            return sorted_arr
        
        #Initialisation
        queue: list[NoeudPondere] = [] #queue qui permet de savoir quel noeud visiter
        distance: dict[NoeudPondere, int] = dict() #distance du départ à une node
        previous: dict[NoeudPondere, NoeudPondere] = dict() #noeud par lequel on est arrivé à ce noeud
        visited: set[NoeudPondere] = set() #noeuds dont tous les voisins ont été visités

        queue.append(depart)
        distance[depart] = 0
        previous[depart] = None
        
        #Naviguation
        while queue[0] != arrivee:
            sort_queue(queue)
            current: NoeudPondere = queue[0]

            for v, p in current.voisins.items():
                if v in visited:
                    continue

                if v not in queue:
                    queue.append(v)
                    distance[v] = distance[current] + p
                    previous[v] = current
                    continue

                if distance[current] + p < distance[v]:
                    distance[v] = distance[current] + p
                    previous[v] = current
            
            visited.add(current)
            queue.pop(0)

        #Reconstruction du chemin
        chemin: list[NoeudPondere] = [] #le chemin pris pour arriver à la fin
        current: NoeudPondere = arrivee

        while current != None:
            chemin.append(current)
            current = previous[current]

        chemin.reverse()
        return chemin