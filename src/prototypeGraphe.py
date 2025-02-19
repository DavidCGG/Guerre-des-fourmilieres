import networkx as nx
import matplotlib.pyplot as plt
import sys

class Noeud:
    def __init__(self, nb = -1, voisins = None):
        self.nb = nb #numéro du noeud
        #Dict contenant les voisins
        #{voisin: poid}
        self.voisins = voisins if voisins is not None else dict()

    def __str__(self):
        return f"{self.nb}"

    def add_voisin(self, voisin, poid = -1) -> None:
        self.voisins[voisin] = poid        
    
    def remove_voisin(self, voisin) -> None:
        self.voisins.pop(voisin)

class Graph:
    def __init__(self, noeuds = None):
        self.noeuds = noeuds if noeuds is not None else set()

    def add_noeud(self, noeud) -> None:
        if noeud not in self.noeuds:
            self.noeuds.add(noeud)
            for v in noeud.voisins:
                v.voisins[noeud] = noeud.voisins[v]

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

    def afficher(self) -> None:
        G = nx.Graph()

        for n in self.noeuds:
            G.add_node(n.nb)

        for n in self.noeuds:
            for v in n.voisins:
                G.add_edge(n.nb, v.nb)

        nx.draw(G, with_labels=True, node_color='lightblue', edge_color='gray', node_size=800, font_size=10)
        plt.show()

    def afficher_weighted(self) -> None:
        G = nx.Graph()

        for n in self.noeuds:
            G.add_node(n.nb)

        for n in self.noeuds:
            for v, poid in n.voisins.items():
                G.add_edge(n.nb, v.nb, weight = poid)

        pos = nx.spring_layout(G)
        nx.draw(G, pos, with_labels=True, node_color='orange', node_size=2000, font_size=15)
        edge_labels = nx.get_edge_attributes(G, 'weight')
        nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels)

        plt.show()

    def dijkstra(self, depart, arrivee) -> list[Noeud]:
        def sort_queue(arr) -> list[Noeud]:
            if len(arr) <= 1:
                return arr

            mid = len(arr) // 2
            left_half = sort_queue(arr[:mid])
            right_half = sort_queue(arr[mid:])

            return merge(left_half, right_half)

        def merge(left, right) -> list[Noeud]:
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
        queue: list[Noeud] = [] #queue qui permet de savoir quel noeud visiter
        distance: dict[Noeud, int] = dict() #distance du départ à une node
        previous: dict[Noeud, Noeud] = dict() #noeud par lequel on est arrivé à ce noeud
        visited: set[Noeud] = set() #noeuds dont tous les voisins ont été visités

        queue.append(depart)
        distance[depart] = 0
        previous[depart] = None
        
        #Naviguation
        while queue[0] != arrivee:
            sort_queue(queue)
            current: Noeud = queue[0]

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
        chemin: list[Noeud] = [] #le chemin pris pour arriver à la fin
        current: Noeud = arrivee

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
                s_voisins += f"{v.nb}, {p}; "

            s += f"Numéro: {n.nb}, Voisins: {s_voisins}\n"
        return s
    
if __name__ == "__main__":
    n0 = Noeud(0)
    n1 = Noeud(1)
    n2 = Noeud(2)
    n3 = Noeud(3)
    n4 = Noeud(4)

    n0.add_voisin(n1)
    n0.add_voisin(n2)
    n2.add_voisin(n3)
    n2.add_voisin(n4)

    graph = Graph()
    graph.add_noeuds([n0, n1, n2, n3, n4])
    graph.afficher()