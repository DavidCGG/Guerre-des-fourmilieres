from enum import Enum

class Noeud_Generation:
    def __init__(self, nb = -1, voisins = None):
        self.nb = nb #Numéro du noeud
        self.voisins = voisins if voisins is not None else set() #Set contenant les voisins

    def add_voisin(self, voisin) -> None:
        self.voisins.add(voisin)       
    
    def remove_voisin(self, voisin) -> None:
        self.voisins.pop(voisin)

class Noeud_Pondere:
    def __init__(self, coord = [-1,-1], voisins = None):
        self.coord = coord
        self.voisins = voisins if voisins is not None else dict() #Dictionnaire contenant les voisins {voisin: poid}

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
        self.noeud = noeud
        self.tunnels = set(tunnels) if tunnels is not None else set()
        self.type = type
    
class Tunnel:
    def __init__(self, depart = None, arrivee = None, largeur = 15):
        self.depart = depart
        self.arrivee = arrivee
        self.largeur = largeur
        
class Graph:
    def __init__(self, salles = None, tunnels = None):
        self.salles = salles if salles is not None else set()
        self.tunnels = tunnels if tunnels is not None else set()

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
                    if tunnel.depart == noeud:
                        salle.tunnels.add(tunnel)

                if len(salle.tunnels) == 1: #Salle
                    salle.type = TypeSalle.SALLE
                else: #Intersection
                    salle.type = TypeSalle.INTERSECTION

                self.salles.add(salle)
        
        def initialiser_tunnels(self, noeuds) -> None:
            for noeud in noeuds:
                for voisin in noeud.voisins:
                    self.tunnels.add(Tunnel(noeud, voisin))

        def initialiser_distances(self, noeuds) -> None:
            for noeud in noeuds:
                for voisin in noeud.voisins:
                    distance = ((noeud.coord[0] - voisin.coord[0]) ** 2 + (noeud.coord[1] - voisin.coord[1]) ** 2) ** 0.5
                    noeud.voisins[voisin] = distance

        connecter_noeuds(noeuds)
        initialiser_tunnels(self, noeuds)
        initialiser_distances(self, noeuds)
        initialiser_salles(self, noeuds)

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