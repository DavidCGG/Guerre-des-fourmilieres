from enum import Enum
from pygame import Vector2

class Noeud_Generation:
    def __init__(self, nb = -1, voisins = None):
        self.nb: int = nb #Numéro du noeud
        self.voisins: set[Noeud_Generation] = voisins if voisins is not None else set() #Set contenant les voisins

    def add_voisin(self, voisin) -> None:
        self.voisins.add(voisin)       
    
    def remove_voisin(self, voisin) -> None:
        self.voisins.pop(voisin)

class Noeud_Pondere:
    def __init__(self, coord = [-1,-1], voisins = None):
        self.coord: list[float, float] = coord
        self.voisins: dict[Noeud_Pondere: float] = voisins if voisins is not None else dict() #Dictionnaire contenant les voisins {voisin: poid}

    def add_voisin(self, voisin, poid = -1) -> None:
        self.voisins[voisin] = poid   
    
    def remove_voisin(self, voisin) -> None:
        self.voisins.pop(voisin)

class TypeSalle(Enum):
    #Les valeurs représentent la taille de la salle
    INTERSECTION = 10
    SALLE = 25
    SORTIE = 10

class Salle:
    def __init__(self, noeud, tunnels = None, type = None):
        self.noeud: Noeud_Pondere = noeud
        self.tunnels: set[Tunnel] = set(tunnels) if tunnels is not None else set()
        self.type: TypeSalle = type

    def intersecte(self, autre) -> bool:
        coord1 = self.noeud.coord
        coord2 = autre.noeud.coord

        distance = ((coord1[0] - coord2[0]) ** 2 + (coord1[1] - coord2[1]) ** 2) ** 0.5
        distance_min = self.type.value + autre.type.value

        return distance < distance_min
    
class Tunnel:
    def __init__(self, depart = None, arrivee = None, largeur = 15):
        self.depart: Noeud_Pondere = depart
        self.arrivee: Noeud_Pondere= arrivee
        self.largeur: int = largeur
    
    def intersecte(self, autre) -> bool:
        def get_rectangle(tunnel) -> tuple[int, int, int, int]:
            scale_largeur: float = 2 #Sert à bien espacer les tunnels

            direction: Vector2 = Vector2(tunnel.arrivee.coord[0] - tunnel.depart.coord[0],
                                         tunnel.arrivee.coord[1] - tunnel.depart.coord[1]).normalize()
            normal: Vector2 = Vector2(-direction.y, direction.x)
            offset: Vector2 = normal * (scale_largeur * self.largeur / 2)

            p1 = Vector2(tunnel.depart.coord) + offset
            p2 = Vector2(tunnel.arrivee.coord) + offset
            p3 = Vector2(tunnel.arrivee.coord) - offset
            p4 = Vector2(tunnel.depart.coord) - offset

            return [p1, p2, p3, p4]
        
        def intersection_segments(a1, a2, b1, b2):
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
        
class Graph:
    def __init__(self, salles = None, tunnels = None):
        self.salles: set[Salle] = salles if salles is not None else set()
        self.tunnels: set[Tunnel] = tunnels if tunnels is not None else set()

    def initialiser_graphe(self, noeuds: list[Noeud_Pondere]) -> None:
        def connecter_noeuds(noeuds) -> None:
            for noeud in noeuds:
                for voisin in noeud.voisins:
                    distance = ((noeud.coord[0] - voisin.coord[0]) ** 2 + (noeud.coord[1] - voisin.coord[1]) ** 2) ** 0.5
                    noeud.voisins[voisin] = distance
                    voisin.voisins[noeud] = distance

        def initialiser_salles(self, noeuds) -> None:
            for noeud in noeuds:
                salle = Salle(noeud)

                for tunnel in self.tunnels:
                    if tunnel.depart == noeud or tunnel.arrivee == noeud:
                        salle.tunnels.add(tunnel)

                if len(salle.tunnels) == 1: #Salle
                    salle.type = TypeSalle.SALLE
                else: #Intersection
                    salle.type = TypeSalle.INTERSECTION

                self.salles.add(salle)
        
        def initialiser_tunnels(self, noeuds) -> None:
            visited = set()

            for noeud in noeuds:
                for voisin in noeud.voisins:
                    if voisin in visited:
                        continue
                    self.tunnels.add(Tunnel(noeud, voisin))
                visited.add(noeud)

        def initialiser_distances(self, noeuds) -> None:
            for noeud in noeuds:
                for voisin in noeud.voisins:
                    distance = ((noeud.coord[0] - voisin.coord[0]) ** 2 + (noeud.coord[1] - voisin.coord[1]) ** 2) ** 0.5
                    noeud.voisins[voisin] = distance

        connecter_noeuds(noeuds)
        initialiser_tunnels(self, noeuds)
        initialiser_distances(self, noeuds)
        initialiser_salles(self, noeuds)

    def verifier_graphe(self) -> bool:
        def verifier_nombre_salles() -> bool:
            nb_salles: int = 0

            for salle in self.salles:
                if salle.type == TypeSalle.INTERSECTION or salle.type == TypeSalle.SORTIE:
                    continue
                nb_salles += 1

            return nb_salles >= 2 and nb_salles <= 5
        
        def verifier_superpositions() -> bool:
            for salle1 in self.salles:
                for salle2 in self.salles:
                    if salle1 == salle2:
                        continue

                    if salle1.intersecte(salle2):
                        return False
                    

            for tunnel1 in self.tunnels:
                for tunnel2 in self.tunnels:
                    if (tunnel1.depart == tunnel2.depart or
                        tunnel1.depart == tunnel2.arrivee or
                        tunnel1.arrivee == tunnel2.depart or
                        tunnel1.arrivee == tunnel2.arrivee):
                        continue

                    if tunnel1.intersecte(tunnel2):
                        return False
                    
            return True
        
        return verifier_nombre_salles() and verifier_superpositions()

    def add_salle(self, salle: Salle, voisins:list[Salle]) -> None:
        self.salles.add(salle)

        for voisin in voisins:
            distance = ((salle.noeud.coord[0] - voisin.noeud.coord[0]) ** 2 + (salle.noeud.coord[1] - voisin.noeud.coord[1]) ** 2) ** 0.5
            salle.noeud.voisins[voisin.noeud] = distance
            voisin.noeud.voisins[salle.noeud] = distance

            tunnel = Tunnel(salle.noeud, voisin.noeud)
            salle.tunnels.add(tunnel)
            voisin.tunnels.add(tunnel)
            self.tunnels.add(tunnel)

    def dijkstra(self, depart, arrivee) -> list[Noeud_Pondere]:
        def sort_queue(arr) -> list[Noeud_Pondere]:
            if len(arr) <= 1:
                return arr

            mid = len(arr) // 2
            left_half = sort_queue(arr[:mid])
            right_half = sort_queue(arr[mid:])

            return merge(left_half, right_half)

        def merge(left, right) -> list[Noeud_Pondere]:
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
        queue: list[Noeud_Pondere] = [] #queue qui permet de savoir quel noeud visiter
        distance: dict[Noeud_Pondere, int] = dict() #distance du départ à une node
        previous: dict[Noeud_Pondere, Noeud_Pondere] = dict() #noeud par lequel on est arrivé à ce noeud
        visited: set[Noeud_Pondere] = set() #noeuds dont tous les voisins ont été visités

        queue.append(depart)
        distance[depart] = 0
        previous[depart] = None
        
        #Naviguation
        while queue[0] != arrivee:
            sort_queue(queue)
            current: Noeud_Pondere = queue[0]

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
        chemin: list[Noeud_Pondere] = [] #le chemin pris pour arriver à la fin
        current: Noeud_Pondere = arrivee

        while current != None:
            chemin.append(current)
            current = previous[current]

        chemin.reverse()
        return chemin