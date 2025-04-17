import pygame
import tkinter as tk
import random
import prototypeGraphe as pg
from config import WHITE, BLACK, YELLOW, RED, ORANGE, PURPLE, BLUE
from config import trouver_font
from camera_nid import Camera
from testGenerationGraphe import generer_graphe

#Variables globales
SCREEN_WIDTH: int = 1280
SCREEN_HEIGHT: int = 720
MAP_LIMIT_X: int = 4000
MAP_LIMIT_Y: int = 2500
HAUTEUR_SOL: int = 200

rectangle_ciel = pygame.Rect(0, 0, MAP_LIMIT_X, HAUTEUR_SOL)
rectangle_sol = pygame.Rect(0, HAUTEUR_SOL, MAP_LIMIT_X, MAP_LIMIT_Y - HAUTEUR_SOL)

pygame.font.init()
police = pygame.font.Font(trouver_font("LowresPixel-Regular.otf"), 22)
clock = pygame.time.Clock()

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

def draw(screen, graphe, camera) -> None:
    def draw_background() -> None:
        for i in range(2):
            rect = rectangle_ciel if i == 0 else rectangle_sol
            color = (90, 160, 250) if i == 0 else (140, 90, 40)

            new_point = camera.apply((rect.x, rect.y))
            new_rect = pygame.Rect(new_point[0], new_point[1], rect.width * camera.get_zoom(), rect.height * camera.get_zoom())
            pygame.draw.rect(screen, color, new_rect)

    def draw_tunnels() -> None:
        #TODO ajouter un trouver_tuiles_visibles comme dans carte
        for tunnel in graphe.tunnels:
            depart = camera.apply(tunnel.depart.coord)
            arrivee = camera.apply(tunnel.arrivee.coord)
            pygame.draw.line(screen, (0, 0, 0), depart, arrivee, int(tunnel.largeur * camera.get_zoom()))

    def draw_salles() -> None:
        for salle in graphe.salles:
            pos = camera.apply(salle.noeud.coord)
            pygame.draw.circle(screen, (0, 0, 0), pos, int(salle.type.value * camera.get_zoom()))

    def draw_top_bar():            
        pygame.draw.rect(screen, BLACK, (0, 0, SCREEN_WIDTH, 50))
        font = pygame.font.Font(None, 24)
        fps_info = font.render(f'FPS: {clock.get_fps():.2f}', True, YELLOW)
        zoom_info = font.render(f'Zoom: {camera.get_zoom() * 100:.2f}%', True, YELLOW)
        screen.blit(fps_info, (10, 10))
        screen.blit(zoom_info, (10, 30))
        
    draw_background()
    draw_tunnels()
    draw_salles()
    draw_top_bar()
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
        salle.noeud.coord = [(MAP_LIMIT_X/2) + salle.noeud.coord[0] * scale,
                            salle.noeud.coord[1] * scale - dy]
        
        if salle != salle_min:
            salle.noeud.coord[1] += 75
        
def run() -> None:
    running = True

    screen = init()
    graphe: pg.Graph = generer_graphe(
        (nb_noeuds_cible, taux_mean, initial_mean, taux_std_dev, initial_std_dev),
        connect_chance,
        nb_iter_forces
    )
    convertir_coord(graphe)

    camera = Camera(SCREEN_WIDTH, SCREEN_HEIGHT, MAP_LIMIT_X, MAP_LIMIT_Y)

    while running:
        #TODO comparer à handle_event dans carte
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Clic gauche
                    camera.start_drag(*event.pos)
                elif event.button == 4:  # Molette haut
                    camera.zoom_camera(*event.pos, "in")
                elif event.button == 5:  # Molette bas
                    camera.zoom_camera(*event.pos, "out")

            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    camera.stop_drag()

            elif event.type == pygame.MOUSEMOTION:
                camera.drag(*event.pos)

        draw(screen, graphe, camera)
        clock.tick(60)

    pygame.quit()
    
if __name__ == "__main__":
    run()