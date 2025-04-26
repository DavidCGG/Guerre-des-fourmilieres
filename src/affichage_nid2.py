import pygame
from camera_nid import Camera
from generation_graphe import generer_graphe
from config import trouver_font
from config import SCREEN_WIDTH, SCREEN_HEIGHT

#Variables globales
MAP_LIMIT_X: int = 5000
MAP_LIMIT_Y: int = 3000
HAUTEUR_SOL: int = 200

class Nid:
    def __init__(self, graphe):
        self.graphe = graphe
        self.camera = Camera(SCREEN_WIDTH, SCREEN_HEIGHT, MAP_LIMIT_X, MAP_LIMIT_Y)

    def draw(self, screen) -> None:
        def draw_background() -> None:
            rectangle_ciel = pygame.Rect(0, 0, MAP_LIMIT_X, HAUTEUR_SOL)
            rectangle_sol = pygame.Rect(0, HAUTEUR_SOL, MAP_LIMIT_X, MAP_LIMIT_Y - HAUTEUR_SOL)

            for i in range(2):
                rect = rectangle_ciel if i == 0 else rectangle_sol
                color = (90, 160, 250) if i == 0 else (140, 90, 40)

                new_point = self.camera.apply((rect.x, rect.y))
                new_rect = pygame.Rect(new_point[0], new_point[1], rect.width * self.camera.get_zoom(), rect.height * self.camera.get_zoom())
                pygame.draw.rect(screen, color, new_rect)

        def draw_tunnels() -> None:
            for tunnel in self.graphe.tunnels:
                depart = self.camera.apply(tunnel.depart.noeud.coord)
                arrivee = self.camera.apply(tunnel.arrivee.noeud.coord)
                pygame.draw.line(screen, (0, 0, 0), depart, arrivee, int(tunnel.largeur * self.camera.get_zoom()))

        def draw_salles() -> None:
            for salle in self.graphe.salles:
                pos = self.camera.apply(salle.noeud.coord)
                pygame.draw.circle(screen, (0, 0, 0), pos, int(salle.type.value[0] * self.camera.get_zoom()))

        draw_background()
        draw_tunnels()
        draw_salles()

    #Retourne true si le ciel à été clické pour retourner à la carte
    def handle_event(self, event) -> bool:
        if event.type == pygame.MOUSEBUTTONDOWN:
            x, y = event.pos

            if event.button == 1:  # Clic gauche
                self.camera.start_drag(*event.pos)
            elif event.button == 3:  # Clic droit
                if y < HAUTEUR_SOL:
                    return True
            elif event.button == 4:  # Molette haut
                self.camera.zoom_camera(*event.pos, "in")
            elif event.button == 5:  # Molette bas
                self.camera.zoom_camera(*event.pos, "out")

        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                self.camera.stop_drag()

        elif event.type == pygame.MOUSEMOTION:
            self.camera.drag(*event.pos)

def chargement(screen: pygame.Surface) -> list:
    def afficher_chargement(n, total):
        screen.fill((30, 30, 30))

        titre = font.render("Création des nids", True, (255, 255, 255))
        progression = small_font.render(f"{n} sur {total}", True, (200, 200, 200))

        screen.blit(titre, (SCREEN_WIDTH//2 - titre.get_width()//2, SCREEN_HEIGHT//2 - 100))
        screen.blit(progression, (screen.get_width()//2 - progression.get_width()//2, SCREEN_HEIGHT//2))

        pygame.display.update()

    graphes = []
    total = 4

    font = pygame.font.Font(trouver_font("LowresPixel-Regular.otf"), 48)
    small_font = pygame.font.Font(trouver_font("LowresPixel-Regular.otf"), 32)

    for i in range(total):
        afficher_chargement(i+1, total)

        graphe = generer_graphe(HAUTEUR_SOL, MAP_LIMIT_X)
        graphes.append(graphe)

    return graphes