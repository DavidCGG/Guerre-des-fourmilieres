import pygame
from camera import Camera
from generation_graphe import generer_graphe
from config import trouver_font,trouver_img
from config import SCREEN_WIDTH, SCREEN_HEIGHT

#Variables globales
MAP_LIMIT_X: int = 4000
MAP_LIMIT_Y: int = 2250
HAUTEUR_SOL: int = 150

class Nid:
    """
    Représente un des nids
    Attributs :
        graphe (Graphe): Graphe contenant les salles et tunnels du nid
        camera (Camera): Caméra pour le zoom et le déplacement
    """

    def __init__(self, graphe):
        self.graphe = graphe
        self.camera = Camera(SCREEN_WIDTH, SCREEN_HEIGHT, MAP_LIMIT_X, MAP_LIMIT_Y)

        self.image_terre = pygame.image.load(trouver_img("terre.png"))
        self.image_terre_sombre = pygame.image.load(trouver_img("terre_dark_brown.png"))
        self.image_ciel = pygame.image.load(trouver_img("ciel2.png"))
        self.scale_images(8, initial_sky_scaling = True)

        self.TILE_SIZE = self.image_terre.get_width()
        self.SKY_TILE_SIZE = self.image_ciel.get_width() - 1

    def scale_images(self, scale, initial_sky_scaling = False) -> None:
        if initial_sky_scaling:
            facteur_ciel = HAUTEUR_SOL / self.image_ciel.get_height()
            self.image_ciel = pygame.transform.scale(self.image_ciel, (int(self.image_ciel.get_width() * facteur_ciel), int(self.image_ciel.get_height() * facteur_ciel)))
        else:
            self.image_ciel = pygame.transform.scale(self.image_ciel, (int(self.image_ciel.get_width() * scale), int(self.image_ciel.get_height() * scale)))

        self.image_terre = pygame.transform.scale(self.image_terre, (int(self.image_terre.get_width() * scale), int(self.image_terre.get_height() * scale)))
        self.image_terre_sombre = pygame.transform.scale(self.image_terre_sombre, (int(self.image_terre_sombre.get_width() * scale), int(self.image_terre_sombre.get_height() * scale)))        

    def draw(self, screen) -> None:
        """
        Dessine tous les éléments du nid sur l'écran incluant l'arrière-plan
        Args:
            screen (pygame.Surface): La surface sur laquelle dessiner
        Returns:
            None
        """
        def draw_terre() -> None:
            for x in range(0, MAP_LIMIT_X, self.TILE_SIZE):
                for y in range(HAUTEUR_SOL, MAP_LIMIT_Y - HAUTEUR_SOL, self.TILE_SIZE):
                    screen_pos = self.camera.apply((x, y))
                    screen.blit(self.image_terre , screen_pos)

        def draw_ciel() -> None:
            for x in range(0, MAP_LIMIT_X, self.SKY_TILE_SIZE):
                screen_pos = self.camera.apply((x, 0))
                screen.blit(self.image_ciel, screen_pos)

        def draw_nid() -> None: 
            mask_surface = pygame.Surface((MAP_LIMIT_X, MAP_LIMIT_Y), pygame.SRCALPHA)
            mask_surface.fill((0, 0, 0, 0))

            for salle in self.graphe.salles:
                pos = self.camera.apply(salle.noeud.coord)
                radius = salle.type.value[0] * self.camera.zoom
                pygame.draw.circle(mask_surface, (255, 255, 255, 255), pos, radius)

            for tunnel in self.graphe.tunnels:
                start = self.camera.apply(tunnel.depart.noeud.coord)
                end = self.camera.apply(tunnel.arrivee.noeud.coord)
                width = int(tunnel.largeur * self.camera.zoom)
                pygame.draw.line(mask_surface, (255, 255, 255, 255), start, end, width)

            dug_surface = pygame.Surface((MAP_LIMIT_X, MAP_LIMIT_Y), pygame.SRCALPHA)
            for x in range(0, MAP_LIMIT_X, int(self.TILE_SIZE)):
                for y in range(0, MAP_LIMIT_Y, int(self.TILE_SIZE)):
                    screen_pos = self.camera.apply((x, y))
                    dug_surface.blit(self.image_terre_sombre , screen_pos)

            dug_surface.blit(mask_surface, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

            screen.blit(dug_surface, (0, 0))

        draw_terre()
        draw_nid()
        draw_ciel()

    def handle_event(self, event) -> bool:
        """
        Gère tous les événements liés au nid
        Args:
            event (pygame.event.Event): L'événement à gérer
        Returns:
            bool: True si le ciel a été cliqué pour sortir du nid, False sinon
        """
        if event.type == pygame.MOUSEBUTTONDOWN:
            x, y = event.pos

            if event.button == 1:  # Clic gauche
                self.camera.start_drag(*event.pos)
            elif event.button == 3:  # Clic droit
                if y < HAUTEUR_SOL:
                    return True
            elif event.button == 4:  # Molette haut
                old_zoom = self.camera.zoom
                self.camera.zoom_camera(*event.pos, "in")
                self.scale_images(self.camera.zoom / old_zoom)
            elif event.button == 5:  # Molette bas
                old_zoom = self.camera.zoom
                self.camera.zoom_camera(*event.pos, "out")
                self.scale_images(self.camera.zoom / old_zoom)

        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                self.camera.stop_drag()

        elif event.type == pygame.MOUSEMOTION:
            self.camera.drag(*event.pos)

def chargement(screen: pygame.Surface,nb_nids) -> list:
    """
    Créer tous les graphes du jeu et affiche un écran de chargement
    Args:
        screen (pygame.Surface): La surface sur laquelle dessiner
    Returns:
        list: Liste des graphes générés
    """
    def afficher_chargement(nb_genere, total):
        """
        Affiche l'écran de chargement
        Args:
            n (int): Le nombre de graphes déjà générés
            total (int): Le nombre total de graphes à générer
        Returns:
            None
        """
        screen.fill((30, 30, 30))

        titre = font.render("Création des nids", True, (255, 255, 255))
        progression = small_font.render(f"{nb_genere} sur {total}", True, (200, 200, 200))

        screen.blit(titre, (SCREEN_WIDTH//2 - titre.get_width()//2, SCREEN_HEIGHT//2 - 100))
        screen.blit(progression, (screen.get_width()//2 - progression.get_width()//2, SCREEN_HEIGHT//2))

        pygame.display.update()

    graphes = []
    total = nb_nids

    font = pygame.font.Font(trouver_font("LowresPixel-Regular.otf"), 48)
    small_font = pygame.font.Font(trouver_font("LowresPixel-Regular.otf"), 32)

    for i in range(total):
        afficher_chargement(i+1, total)

        graphe = generer_graphe(HAUTEUR_SOL, MAP_LIMIT_X)
        graphes.append(graphe)

    return graphes