import networkx as nx
import matplotlib.pyplot as plt

class Noeud_Generation:
    def __init__(self, nb = -1, voisins = None):
        self.nb = nb #numéro du noeud
        #Set contenant les voisins
        self.voisins = voisins if voisins is not None else set()

    def __str__(self):
        return f"{self.nb}"

    def add_voisin(self, voisin) -> None:
        self.voisins.add(voisin)       
    
    def remove_voisin(self, voisin) -> None:
        self.voisins.pop(voisin)

class Noeud_Pondere:
    def __init__(self, coord = (-1,-1), voisins = None):
        self.coord = coord
        #Dictionnaire contenant les voisins {voisin: poid}
        self.voisins = voisins if voisins is not None else dict()

    def add_voisin(self, voisin, poid = -1) -> None:
        self.voisins[voisin] = poid        
    
    def remove_voisin(self, voisin) -> None:
        self.voisins.pop(voisin)

    def __str__(self):
        s_voisins = ""
        for v, p in self.voisins.items():
            s_voisins += f"({v.coord[0]:.2f}, {v.coord[1]:.2f}); "

        return f"Coord: ({self.coord[0]:.2f}, {self.coord[1]:.2f}), Voisins: {s_voisins}"
        
class Graph:
    def __init__(self, noeuds = None):
        self.noeuds = noeuds if noeuds is not None else set()

    def add_noeud(self, noeud) -> None:
        if noeud not in self.noeuds:
            self.noeuds.add(noeud)
            for v in noeud.voisins:
                v.voisins.add(noeud)

    def add_noeuds(self, noeuds) -> None:
        for n in noeuds:
            if n not in self.noeuds:
                self.noeuds.add(n)
                for v in n.voisins:
                    v.voisins[n] = n.voisins[v]

    def remove_noeud(self, noeud) -> None:
        if noeud in self.noeuds:
            self.noeuds.remove(noeud)
            for v in noeud.voisins:
                v.voisins.pop(noeud)

    def connect_noeuds(self, noeud1, noeud2, poid = -1) -> None:
        if noeud2 not in noeud1.voisins:
            noeud1.voisins[noeud2] = poid
        if noeud1 not in noeud2.voisins:
            noeud2.voisins[noeud1] = poid

    def disconnect_noeuds(self, noeud1, noeud2) -> None:
        if noeud2 in noeud1.voisins:
            noeud1.voisins.pop(noeud2)
        if noeud1 in noeud2.voisins:
            noeud2.voisins.pop(noeud1)

    def afficher(self, ax=None) -> None:
        G = nx.Graph()
        positions = dict()
        num_noeud = dict()

        for n, noeud in enumerate(self.noeuds):
            positions[n] = noeud.coord
            num_noeud[noeud] = n
            G.add_node(n)

        for noeud in self.noeuds:
            for v in noeud.voisins:
                G.add_edge(num_noeud[noeud] , num_noeud[v])

        if ax is None:
            fig, ax = plt.subplots()

        nx.draw(G, pos=positions, with_labels=True, node_color='lightblue', edge_color='gray', node_size=800, font_size=10, ax=ax)

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

    def __str__(self):
        s = ""
        for n in self.noeuds:
            s_voisins = ""
            for v, p in n.voisins.items():
                s_voisins += f"({v.coord[0]:.2f}, {v.coord[1]:.2f}); "

            s += f"Coord: ({n.coord[0]:.2f}, {n.coord[1]:.2f}), Voisins: {s_voisins}\n"
        return s
    
if __name__ == "__main__":
    pass