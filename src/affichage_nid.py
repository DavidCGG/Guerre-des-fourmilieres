import pygame
import classes_graphe as cg
from config import WHITE, BLACK, YELLOW
from config import trouver_font
from camera_nid import Camera
from generation_graphe import generer_graphe
from classes import Bouton

#Variables globales
SCREEN_WIDTH: int = 1280
SCREEN_HEIGHT: int = 720
MAP_LIMIT_X: int = 5000
MAP_LIMIT_Y: int = 3000
HAUTEUR_SOL: int = 200

running: bool = True
in_menu: bool = False

rectangle_ciel = pygame.Rect(0, 0, MAP_LIMIT_X, HAUTEUR_SOL)
rectangle_sol = pygame.Rect(0, HAUTEUR_SOL, MAP_LIMIT_X, MAP_LIMIT_Y - HAUTEUR_SOL)

screen: pygame.Surface = None
clock = pygame.time.Clock()
liste_boutons = []

def init() -> None:
    global screen

    pygame.init()
    pygame.font.init()
    pygame.display.set_caption("Test de génération de nids")
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

def draw(graphe, camera) -> None:
    def draw_background() -> None:
        for i in range(2):
            rect = rectangle_ciel if i == 0 else rectangle_sol
            color = (90, 160, 250) if i == 0 else (140, 90, 40)

            new_point = camera.apply((rect.x, rect.y))
            new_rect = pygame.Rect(new_point[0], new_point[1], rect.width * camera.get_zoom(), rect.height * camera.get_zoom())
            pygame.draw.rect(screen, color, new_rect)

    def draw_tunnels() -> None:
        for tunnel in graphe.tunnels:
            depart = camera.apply(tunnel.depart.noeud.coord)
            arrivee = camera.apply(tunnel.arrivee.noeud.coord)
            pygame.draw.line(screen, (0, 0, 0), depart, arrivee, int(tunnel.largeur * camera.get_zoom()))

    def draw_salles() -> None:
        for salle in graphe.salles:
            pos = camera.apply(salle.noeud.coord)
            pygame.draw.circle(screen, (0, 0, 0), pos, int(salle.type.value[0] * camera.get_zoom()))

    def draw_top_bar():
        global liste_boutons

        if  not any(isinstance(bouton, Bouton) and bouton.texte == "Options" for bouton in liste_boutons):
            bouton = Bouton(screen, SCREEN_WIDTH - 100, 25, 100, 30, "Options", menu_options, pygame.font.Font(trouver_font("LowresPixel-Regular.otf"), 22))
            liste_boutons.append(bouton)

        pygame.draw.rect(screen, BLACK, (0, 0, SCREEN_WIDTH, 50))

        font = pygame.font.Font(None, 24)
        fps_info = font.render(f'FPS: {clock.get_fps():.2f}', True, YELLOW)
        zoom_info = font.render(f'Zoom: {camera.get_zoom() * 100:.2f}%', True, YELLOW)

        screen.blit(fps_info, (10, 10))
        screen.blit(zoom_info, (10, 30))
    
    if not in_menu:
        draw_background()
        draw_tunnels()
        draw_salles()

    draw_top_bar()
    for bouton in liste_boutons:
            bouton.draw()
    pygame.display.flip()

def menu_options():
    global liste_boutons
    global in_menu

    in_menu = True

    surface = pygame.Surface((300, 400))
    surface.fill(BLACK)

    texte_render = pygame.font.Font(trouver_font("LowresPixel-Regular.otf"), 36).render("Options", True, WHITE)
    police_boutons = pygame.font.Font(trouver_font("LowresPixel-Regular.otf"), 30)

    surface.blit(texte_render, [surface.get_width() / 2 - texte_render.get_rect().width / 2, 10])
    screen.blit(surface, (SCREEN_WIDTH / 2 - 150, SCREEN_HEIGHT / 2 - 250))

    liste_boutons.append(Bouton(screen, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 100, SCREEN_WIDTH / 8, SCREEN_HEIGHT / 15,
                            'Retour', retour, police_boutons))
    liste_boutons.append(Bouton(screen, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2, SCREEN_WIDTH / 8, SCREEN_HEIGHT / 15,
                            'Quitter', quitter, police_boutons))
    
def retour():
    global liste_boutons
    global in_menu

    liste_boutons.clear()
    in_menu = False

def quitter():
    global running

    running = False

def handle_events(events, camera):
    for event in events:
        if event.type == pygame.QUIT:
            quitter()

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
        
def run() -> None:
    init()
    graphe: cg.Graphe = generer_graphe(HAUTEUR_SOL, MAP_LIMIT_X)

    camera = Camera(SCREEN_WIDTH, SCREEN_HEIGHT, MAP_LIMIT_X, MAP_LIMIT_Y)

    while running:
        handle_events(pygame.event.get(), camera)
        draw(graphe, camera)
        clock.tick(60)

    pygame.quit()
    
if __name__ == "__main__":
    run()