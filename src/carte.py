import random
import pygame
import numpy as np
from pygame.examples.grid import TILE_SIZE

from colonies import Colonie
from camera import Camera
from tuile import Tuile
from random_noise import RandomNoise
from tuile import Terre, Sable, Eau, Montagne

from config import trouver_img, GREEN
from config import trouver_font
from config import BLACK, YELLOW, RED, PURPLE, BLUE, AQUA
#from config import SCREEN_WIDTH, SCREEN_HEIGHT

pygame.font.init()
police = pygame.font.Font(trouver_font("LowresPixel-Regular.otf"), 22)
couleurs_possibles = [BLACK, YELLOW, RED, PURPLE, BLUE, AQUA]

taille_tuile = 32
MAP_WIDTH = 100
MAP_HEIGHT = 100

class Carte:
    def __init__(self,nb_colonies_nids,screen,graphes,liste_fourmis_jeu_complet):
        global taille_tuile
        global MAP_WIDTH
        global MAP_HEIGHT
        self.TILE_SIZE = taille_tuile
        self.MAP_WIDTH = MAP_WIDTH
        self.MAP_HEIGHT = MAP_HEIGHT

        self.graphes=graphes

        self.grid_mode = False # option pour montrer la bordure des tuiles en noir
        self.hover_tuile = None  # la tuile qui devient couleur AQUA quand on a une fourmi selectionnee

        self.map_data = None
        self.tuiles_ressources = [] # liste des tuiles ayant une ressource
        
        self.tuiles_debut = []  # liste des tuiles de debut de chaque colonie
        #self.tuile_debut_joueur = None
        self.colonies = []

        self.liste_boutons = []

        self.image_etoile = pygame.image.load(trouver_img("Monde/etoile.png"))
        self.image_etoile = pygame.transform.scale(self.image_etoile, (self.TILE_SIZE, self.TILE_SIZE))

        self.nb_colonies_nids = nb_colonies_nids
        self.couleurs_colonies=[]
        for i in range(self.nb_colonies_nids):
            self.couleurs_colonies.append(couleurs_possibles[i])

        self.generation_map(liste_fourmis_jeu_complet)

        self.screen = screen
        self.camera = Camera(screen.get_width(), screen.get_height(), self.MAP_WIDTH * self.TILE_SIZE, self.MAP_HEIGHT * self.TILE_SIZE)
        self.set_camera_tuile_debut()

    def generation_map(self,liste_fourmis_jeu_complet):
        def liste_tuiles() -> list:
            tuiles = [[Tuile(x, y, self.TILE_SIZE, self.TILE_SIZE) for x in range(self.MAP_WIDTH)] for y in range(self.MAP_HEIGHT)]
            return tuiles
    
        def transformer_tuiles():
            """Transforme les tuiles de la carte en fonction de la valeur du bruit"""
            noise_gen = RandomNoise(self.MAP_WIDTH, self.MAP_HEIGHT, 255, extra=65)
            noise_gen.randomize()
            vals_noise = noise_gen.smoothNoise2d(smoothing_passes=20, upper_value_limit=1)
            
            water_amount = 0.46
            sand_amount = 0.013
            land_amount = 0.44

            for y in range(self.MAP_HEIGHT):
                for x in range(self.MAP_WIDTH):
                    self.map_data[y][x].val_noise = vals_noise[y][x]
                    col = int(vals_noise[y][x] * 255)

                    # Convert noise value to color
                    if col < int(255 * water_amount):  # water
                        self.map_data[y][x] = Eau(x, y, self.TILE_SIZE, self.TILE_SIZE)
                        self.map_data[y][x].color = (0, 0, col)

                    elif col < int(255 * (water_amount + sand_amount)):  # sand
                        self.map_data[y][x] = Sable(x, y, self.TILE_SIZE, self.TILE_SIZE)
                        self.map_data[y][x].color = (col, col, 0)

                    elif col < int(255 * (water_amount + sand_amount + land_amount)):  # land
                        self.map_data[y][x] = Terre(x, y, self.TILE_SIZE, self.TILE_SIZE)
                        self.map_data[y][x].color = (0, col, 0)

                    else:
                        #print("montagne")
                        self.map_data[y][x] = Montagne(x, y, self.TILE_SIZE, self.TILE_SIZE)
                        self.map_data[y][x].color = (0, 0, 0)

                    if self.map_data[y][x].tuile_ressource:
                        self.tuiles_ressources.append(self.map_data[y][x])

        def placer_colonies(region_size, min_dist):
            # On definit des regions aux coins de la carte
            curr_couleur = 0
            regions = [
                (min_dist, min_dist),  # Top-left corner
                (self.MAP_WIDTH - region_size - min_dist, min_dist),  # Top-right corner
                (min_dist, self.MAP_HEIGHT - region_size - min_dist),  # Bottom-left corner
                (self.MAP_WIDTH - region_size - min_dist, self.MAP_HEIGHT - region_size - min_dist)  # Bottom-right corner
            ]

            # On les placent a l'interieur de ces regions aleatoirement
            for region_x, region_y in regions:
                #placed = False
                while len(self.tuiles_debut)<self.nb_colonies_nids:
                    x = random.randint(region_x, region_x + region_size - 1)
                    y = random.randint(region_y, region_y + region_size - 1)
                    if isinstance(self.map_data[y][x], (Terre, Montagne)):
                        self.map_data[y][x].tuile_debut_joueur = True
                        self.map_data[y][x].color = self.couleurs_colonies[curr_couleur]
                        #placed = True
                        curr_couleur += 1
                        self.tuiles_debut.append((x, y))
                        #print(len(self.tuiles_debut))
        
        def set_tuiles_debut(liste_fourmis_jeu_complet):
            #self.tuile_debut_joueur = self.tuiles_debut[random.randint(0, self.nb_colonies_nids - 1)]
            for i in range(self.nb_colonies_nids):
                self.colonies.append(Colonie(self.tuiles_debut[i], self.map_data,self.tuiles_debut,self.graphes[i],liste_fourmis_jeu_complet))

            #index_tuile_debut = self.tuiles_debut.index(self.tuile_debut_joueur)
            #temp = self.tuiles_debut[0]
            #self.tuiles_debut[0] = self.tuile_debut_joueur
            #self.tuiles_debut[index_tuile_debut] = temp

        self.map_data = np.array(liste_tuiles())
        transformer_tuiles()
        placer_colonies(region_size=20, min_dist=50)
        set_tuiles_debut(liste_fourmis_jeu_complet)

    def draw(self, screen):
        def etoile_tuile_debut():
            """Dessine une étoile sur la tuile de début de la colonie"""
            tile_size = (self.TILE_SIZE * self.camera.zoom)

            x, y = self.colonies[0].tuile_debut
            rect = pygame.Rect(x * tile_size, y * tile_size, tile_size, tile_size)

            if screen.get_rect().colliderect(self.camera.apply_rect(rect)):
                screen.blit(pygame.transform.scale(self.image_etoile, (tile_size, tile_size)), self.camera.apply_rect(rect))

        def draw_tiles(start_x, start_y, end_x, end_y):
            """Dessine les tuiles visibles sur l'écran
            Args:
                start_x (int): coordonnee x de la tuile de gauche
                start_y (int): coordonnee y de la tuile du haut
                end_x (int): coordonnee x de la tuile de droite
                end_y (int): coordonnee y de la tuile du bas
            Voir aussi: trouver_tuiles_visibles()
                """
            tile_size = (self.TILE_SIZE * self.camera.zoom)

            for y in range(start_y, end_y):
                for x in range(start_x, end_x):
                    tile = self.map_data[y][x]
                    tile_rect = pygame.Rect(x * tile_size, y * tile_size, tile_size, tile_size)
                    tile.draw(screen, self.camera.apply_rect(tile_rect), self.grid_mode)
                    if self.colonies[0].fourmis_selection and self.colonies[0].fourmis_selection.centre_x_in_map is not None and self.colonies[0].fourmis_selection.centre_y_in_map is not None:
                        if self.hover_tuile == (x, y):
                            pygame.draw.rect(screen, AQUA, self.camera.apply_rect(tile_rect), 2)
                        if self.colonies[0].fourmis_selection.get_tuile() == (x, y):
                            pygame.draw.rect(screen, GREEN, self.camera.apply_rect(tile_rect), 2)
                    if self.colonies[0].groupe_selection:
                        if self.hover_tuile == (x, y):
                            pygame.draw.rect(screen, AQUA, self.camera.apply_rect(tile_rect), 2)
                        if self.colonies[0].groupe_selection.get_tuile() == (x, y):
                            pygame.draw.rect(screen, GREEN, self.camera.apply_rect(tile_rect), 2)
        
        screen.fill(BLACK)
        start_x, start_y, end_x, end_y = self.trouver_tuiles_visibles()
        draw_tiles(start_x, start_y, end_x, end_y)
        etoile_tuile_debut()

        tile_size = int(self.TILE_SIZE * self.camera.zoom)
        self.colonies[0].render_ants(tile_size, screen, self.camera)

        if self.colonies[0].menu_colonie_ouvert:
            self.colonies[0].menu_colonie(screen)

        if self.colonies[0].menu_fourmis_ouvert and self.colonies[0].menu_colonie_ouvert:
            self.colonies[0].menu_fourmis(screen)

    #retourne l'index de la colonie cliquée avec un right click
    def handle_event(self, event, screen) -> int:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_q:
                self.colonies[0].menu_colonie_ouvert = not self.colonies[0].menu_colonie_ouvert

        elif event.type == pygame.MOUSEBUTTONDOWN:
            tile_x, tile_y = self.get_tuile(event)
            if event.button == 1:  #Left click
                self.camera.start_drag(*event.pos)
                self.colonies[0].handle_click(event.pos, tile_x, tile_y, screen)
                if (tile_x, tile_y) == self.colonies[0].tuile_debut:
                    self.colonies[0].menu_colonie_ouvert = not self.colonies[0].menu_colonie_ouvert

            if event.button == 3:  #Right click
                if self.colonies[0].fourmis_selection:
                    self.colonies[0].fourmis_selection.set_target_in_map(tile_x, tile_y, self.map_data,self.colonies)
                    self.colonies[0].fourmis_selection = None
                    self.hover_tuile = None
                elif self.colonies[0].groupe_selection:
                    self.colonies[0].groupe_selection.set_target_in_map(tile_x, tile_y, self.map_data,self.colonies)
                    self.colonies[0].groupe_selection = None
                    self.hover_tuile = None

                elif (tile_x, tile_y) in self.tuiles_debut:
                    return self.tuiles_debut.index((tile_x, tile_y))

            elif event.button == 4: #Scroll up
                self.colonies[0].handle_scroll("up", event.pos)
                if not self.colonies[0].scrolling:
                    self.camera.zoom_camera(*event.pos, "in")

            elif event.button == 5: #Scroll down
                self.colonies[0].handle_scroll("down", event.pos)
                if not self.colonies[0].scrolling:
                    self.camera.zoom_camera(*event.pos, "out")

        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                self.camera.stop_drag()

        elif event.type == pygame.MOUSEMOTION:
            self.camera.drag(*event.pos)
            self.colonies[0].handle_hover(event.pos)
            if self.colonies[0].fourmis_selection is not None:
                self.hover_tuile = self.get_tuile(event)
            elif self.colonies[0].groupe_selection is not None:
                self.hover_tuile = self.get_tuile(event)
    
    def set_camera_tuile_debut(self):
        """Place la camera sur la tuile de debut de la colonie"""
        x, y = self.colonies[0].tuile_debut
        tile_size = (self.TILE_SIZE * self.camera.zoom)
        self.camera.x = x * tile_size - self.screen.get_width() / 2 + tile_size/2
        self.camera.y = y * tile_size - self.screen.get_height() / 2 + tile_size/2

    def decouvrir_tuiles(self, x_tuile, y_tuile):
        for y in range(y_tuile - 2, y_tuile+3):
            for x in range(x_tuile - 2, x_tuile+3):
                if abs(x - x_tuile) + abs(y - y_tuile) <= 2:
                    if 0 <= x < self.MAP_WIDTH and 0 <= y < self.MAP_HEIGHT:
                        self.map_data[y][x].toggle_color()

    def get_tuile(self, event) -> tuple:
        """Retourne la tuile sur laquelle on clique
        Args:
            event (tuple): pygame.event
        """
        tile_size = (self.TILE_SIZE * self.camera.zoom)
        tile_x = int((self.camera.x + event.pos[0]) // tile_size)
        tile_y = int((self.camera.y + event.pos[1] - 50) // tile_size)
        return tile_x, tile_y

    def trouver_tuiles_visibles(self) -> tuple:
        """Retourne les tuiles visibles sur l'ecran"""
        tile_size = (self.TILE_SIZE * self.camera.zoom)
        start_x = max(0, int(self.camera.x // tile_size))
        start_y = max(0, int(self.camera.y // tile_size))

        # On s'assure que la tuile se retrouve dans les limites de la carte
        end_x = min(int((self.camera.x + self.screen.get_width()) // tile_size + 1), self.MAP_WIDTH)
        end_y = min(int((self.camera.y + self.screen.get_height()) // tile_size + 1), self.MAP_HEIGHT)

        return start_x, start_y, end_x, end_y