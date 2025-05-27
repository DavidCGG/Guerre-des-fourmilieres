import random
import pygame
import numpy as np

from colonies import Colonie, ColonieIA
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

        self.graphes = graphes

        self.grid_mode = False # option pour montrer la bordure des tuiles en noir
        self.hover_tuile = None  # la tuile qui devient couleur AQUA quand on a une fourmi selectionnee

        self.map_data = None
        self.tuiles_ressources = [] # liste des tuiles ayant une ressource
        
        self.tuiles_debut = []  # liste des tuiles de debut de chaque colonie
        self.colonies = []

        self.liste_boutons = []

        self.image_etoile = pygame.image.load(trouver_img("Monde/etoile.png"))
        self.image_etoile = pygame.transform.scale(self.image_etoile, (self.TILE_SIZE, self.TILE_SIZE))

        self.nb_colonies_nids = nb_colonies_nids
        self.liste_fourmis_jeu_complet = liste_fourmis_jeu_complet
        self.couleurs_colonies=[]
        for i in range(self.nb_colonies_nids):
            self.couleurs_colonies.append(couleurs_possibles[i])
        self.screen = screen
        self.generation_map(liste_fourmis_jeu_complet)

        self.camera = Camera(screen.get_width(), screen.get_height(), self.MAP_WIDTH * self.TILE_SIZE, self.MAP_HEIGHT * self.TILE_SIZE)
        self.set_camera_tuile_debut()

    def generation_map(self,liste_fourmis_jeu_complet):
        def liste_tuiles() -> list:
            tuiles = [[Tuile(x, y, self.TILE_SIZE, self.TILE_SIZE) for x in range(self.MAP_WIDTH)] for y in range(self.MAP_HEIGHT)]
            return tuiles
    
        def transformer_tuiles():
            """Transforme les tuiles de la carte en fonction de la valeur du bruit"""
            noise_gen = RandomNoise(self.MAP_WIDTH, self.MAP_HEIGHT, 255, extra=32)
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
                        self.map_data[y][x] = Montagne(x, y, self.TILE_SIZE, self.TILE_SIZE)
                        self.map_data[y][x].color = (0, 0, 0)

                    if self.map_data[y][x].tuile_ressource:
                        self.tuiles_ressources.append(self.map_data[y][x])

        def placer_colonies(min_dist, region_size):
            # On definit des regions aux coins de la carte
            curr_couleur = 0
            regions = [
                (min_dist, min_dist),  # Top-left corner
                #(self.MAP_WIDTH - region_size - min_dist, min_dist),  # Top-right corner
                #(min_dist, self.MAP_HEIGHT - region_size - min_dist),  # Bottom-left corner
                (self.MAP_WIDTH - region_size - min_dist, self.MAP_HEIGHT - region_size - min_dist)  # Bottom-right corner
            ]

            # On les placent a l'interieur de ces regions aleatoirement
            while len(self.tuiles_debut) < self.nb_colonies_nids:
                region = random.choice(regions)
                tuile = None

                while tuile is None:
                    x = random.randint(region[0], region[0] + region_size - 1)
                    y = random.randint(region[1], region[1] + region_size - 1)

                    if isinstance(self.map_data[y][x], (Terre, Montagne)):
                        tuile = (x,y)

                self.map_data[tuile[1]][tuile[0]].tuile_debut = True
                self.map_data[tuile[1]][tuile[0]].color = self.couleurs_colonies[curr_couleur]
                curr_couleur += 1
                self.tuiles_debut.append((x, y))
                regions.remove(region)

            for i in range(self.nb_colonies_nids):
                if i == 0:
                    self.colonies.append(Colonie(self.tuiles_debut[0], self.map_data,self.tuiles_debut ,self.graphes[0], liste_fourmis_jeu_complet))
                else:
                    self.colonies.append(ColonieIA(self.tuiles_debut[1], self.map_data,self.tuiles_debut, self.graphes[1], liste_fourmis_jeu_complet))

        self.map_data = np.array(liste_tuiles())
        transformer_tuiles()
        placer_colonies(min_dist=20, region_size=15)
        self.colonies[0].screen = self.screen

    def draw(self, screen, dt):
        def etoile_tuile_debut():
            """Dessine une étoile sur la tuile de début de la colonie"""
            tile_size = (self.TILE_SIZE * self.camera.zoom)

            x, y = self.colonies[0].tuile_debut
            rect = pygame.Rect(x * tile_size, y * tile_size, tile_size, tile_size)

            if screen.get_rect().colliderect(self.camera.apply_rect(rect)):
                screen.blit(pygame.transform.scale(self.image_etoile, (tile_size, tile_size)), self.camera.apply_rect(rect))

        def draw_tiles(start_x, start_y, end_x, end_y):
            """Dessine les tuiles visibles sur l'écran"""
            tile_size = (self.TILE_SIZE * self.camera.zoom)

            for y in range(start_y, end_y):
                for x in range(start_x, end_x):
                    tile = self.map_data[y][x]
                    tile_rect = pygame.Rect(x * tile_size, y * tile_size, tile_size, tile_size)
                    tile.draw(screen, self.camera.apply_rect(tile_rect), self.grid_mode, dt)
                    if self.colonies[0].fourmis_selection:
                        if self.hover_tuile == (x, y):
                            pygame.draw.rect(screen, AQUA, self.camera.apply_rect(tile_rect), 2)
                        if self.colonies[0].fourmis_selection.centre_in_map is not None and self.colonies[0].fourmis_selection.get_tuile() == (x, y):
                            pygame.draw.rect(screen, GREEN, self.camera.apply_rect(tile_rect), 2)
        
        screen.fill(BLACK)
        start_x, start_y, end_x, end_y = self.trouver_tuiles_visibles()
        draw_tiles(start_x, start_y, end_x, end_y)
        etoile_tuile_debut()

        tile_size = int(self.TILE_SIZE * self.camera.zoom)



        if self.colonies[0].menu_colonie_ouvert:
            self.colonies[0].menu_colonie()

        if self.colonies[0].menu_fourmis_ouvert and self.colonies[0].menu_colonie_ouvert:
            self.colonies[0].menu_fourmis()

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
                    self.colonies[0].fourmis_selection.set_target_in_map(tile_x, tile_y, self.map_data, self.colonies)
                    self.colonies[0].fourmis_selection = None
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
    
    def set_camera_tuile_debut(self):
        """Place la camera sur la tuile de debut de la colonie"""
        x, y = self.colonies[0].tuile_debut
        tile_size = (self.TILE_SIZE * self.camera.zoom)
        self.camera.x = x * tile_size - self.screen.get_width() / 2 + tile_size/2
        self.camera.y = y * tile_size - self.screen.get_height() / 2 + tile_size/2

    def get_tuile(self, event) -> tuple:
        """Retourne la tuile sur laquelle on clique"""
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