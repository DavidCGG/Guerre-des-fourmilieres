import pygame
import tkinter as tk
import random
import prototypeGraphe as pg
from testGenerationGraphe import generer_graphe

#Variables globales
SCREEN_WIDTH: int = 800
SCREEN_HEIGHT: int = 600
HAUTEUR_SOL = 100

#Variables de génération
nb_noeuds_cible: int = 10
nb_iter_forces: int = 100
connect_chance: float = 0.3
taux_mean: float = -1
initial_mean: float = 3
taux_std_dev: float = 1/3
initial_std_dev: float = 1

def init() -> pygame.Surface:
    pygame.init()
    pygame.display.set_caption("Test de génération de nids")
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    return screen

def draw(screen, graphe) -> None:
    screen.fill((255, 255, 255))

    pygame.draw.rect(screen, (90, 160, 250), (0, 0, SCREEN_WIDTH, HAUTEUR_SOL))
    pygame.draw.rect(screen, (140, 90, 40), (0, HAUTEUR_SOL, SCREEN_WIDTH, SCREEN_HEIGHT - HAUTEUR_SOL))

    for tunnel in graphe.tunnels:
        pygame.draw.line(screen, (0, 0, 0), tunnel.depart.coord, tunnel.arrivee.coord, tunnel.largeur)

    for salle in graphe.salles:
        pygame.draw.circle(screen, (0, 0, 0), salle.noeud.coord, salle.type.value)
    
    pygame.display.flip()

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
        salle.noeud.coord = [(SCREEN_WIDTH/2) + salle.noeud.coord[0] * scale,
                            salle.noeud.coord[1] * scale - dy]
        
        if salle != salle_min:
                salle.noeud.coord[1] += 75
        
def interface() -> None:
    def initialiser() -> None:
        root = tk.Tk()
        root.geometry("500x350")
        root.title("Configuration des paramètres de génération de graphe")

        labels = ["Nombre de noeuds", "Nombre d'itérations des forces", "Chance de connection", "Taux médianne", "Médianne Initiale", "Taux écart-type", "Écart-type initial"]
        default_values: list[float] = [nb_noeuds_cible, nb_iter_forces, connect_chance, taux_mean, initial_mean, taux_std_dev, initial_std_dev]
        entry_vars: list[tk.StringVar] = []

        for i, label in enumerate(labels):
            tk.Label(root, text=label).grid(row=i, column=0, padx=10, pady=5)
            
            var = tk.StringVar(value=str(default_values[i]))
            var.trace_add("write", lambda name, index, mode, i=i, v=var: modifier_valeur(i, v))

            entry = tk.Entry(root, textvariable=var)
            entry.grid(row=i, column=1, padx=10, pady=5)
            
            entry_vars.append(var)

        tk.Button(root, text="Générer des graphes", command=afficher_graphe).grid(row=7, column=0, columnspan=2, pady=10)

        root.mainloop()

    def modifier_valeur(index: int, var: tk.StringVar):
        global nb_noeuds_cible, nb_iter_forces, connect_chance, taux_mean, initial_mean, taux_std_dev, initial_std_dev

        try:
            new_value = float(var.get())
        except ValueError:
            return

        if index == 0:
            nb_noeuds_cible = int(new_value)
        elif index == 1:
            nb_iter_forces = int(new_value)
        elif index == 2:
            connect_chance = new_value
        elif index == 3:
            taux_mean = new_value
        elif index == 4:
            initial_mean = new_value
        elif index == 5:
            taux_std_dev = new_value
        elif index == 6:
            initial_std_dev = new_value

    def afficher_graphe() -> None:
        running = True

        screen = init()
        graphe: pg.Graph = generer_graphe((nb_noeuds_cible, taux_mean, initial_mean, taux_std_dev, initial_std_dev), connect_chance, nb_iter_forces)
        convertir_coord(graphe)

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
            
            draw(screen, graphe)

        pygame.quit()
    
    initialiser()

if __name__ == "__main__":
    interface()