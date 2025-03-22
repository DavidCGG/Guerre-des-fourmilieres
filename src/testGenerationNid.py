import pygame
import tkinter as tk
import prototypeGraphe as pg
from testGenerationGraphe import generer_graphe

#Variables globales
SCREEN_WIDTH: int = 800
SCREEN_HEIGHT: int = 600

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

def draw(screen, graphe, hauteur_sol = 100) -> None:
    screen.fill((255, 255, 255))

    pygame.draw.rect(screen, (90, 160, 250), (0, 0, SCREEN_WIDTH, hauteur_sol))
    pygame.draw.rect(screen, (140, 90, 40), (0, hauteur_sol, SCREEN_WIDTH, SCREEN_HEIGHT - hauteur_sol))

    for tunnel in graphe.tunnels:
        pygame.draw.line(screen, (0, 0, 0), tunnel.depart.coord, tunnel.arrivee.coord, tunnel.largeur)

    for salle in graphe.salles:
        pygame.draw.circle(screen, (0, 0, 0), salle.noeud.coord, salle.type.value)
    
    pygame.display.flip()

def convertir_coord(coord, scale = 50) -> tuple:
    x = (SCREEN_WIDTH/2) + scale * coord[0]
    y = (SCREEN_HEIGHT/2) + scale * coord[1]
    return (int(x), int(y))

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
        for salle in graphe.salles:
            salle.noeud.coord = convertir_coord(salle.noeud.coord)

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
            
            draw(screen, graphe)

        pygame.quit()
    
    initialiser()

if __name__ == "__main__":
    interface()