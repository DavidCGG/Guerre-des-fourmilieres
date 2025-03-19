import random
import pygame
import venv_setup
from memory_profiler import profile
import gc
from colonies import Colonie

from bouton import Bouton
from camera import Camera
from config import WHITE, BLACK, YELLOW, RED, ORANGE, PURPLE, BLUE
from config import trouver_font
from generation_map import GenerationMap
from random_noise import RandomNoise
from config import trouver_img
from tuile import Terre, Sable, Eau, Montagne

pygame.font.init()
police = pygame.font.Font(trouver_font("LowresPixel-Regular.otf"), 22)
couleurs_colonies = [RED, BLUE, PURPLE, YELLOW]

class Carte:
    def __init__(self):
        pygame.init()
        self.running = True
        self.size = (1280, 720)
        self.screen = pygame.display.set_mode(self.size)
        pygame.display.set_caption("Guerre des fourmilières")

        self.water_amount = 0.46
        self.sand_amount = 0.013
        self.land_amount = 0.44

        self.grid_mode = False
        self.in_menu = False
        self.close_menu = False
        self.moving = False
        self.menu_colonie = False

        self.TILE_SIZE = 32
        self.MAP_WIDTH = 100
        self.MAP_HEIGHT = 100
        self.gen_map = GenerationMap(self.MAP_WIDTH, self.MAP_HEIGHT, self.TILE_SIZE)
        self.map_data = self.gen_map.liste_tuiles()
        self.objets = []
        self.clock = pygame.time.Clock()



        self.camera = Camera(self.size[0], self.size[1], self.MAP_WIDTH, self.MAP_HEIGHT, self.TILE_SIZE)
        self.last_cam_x = self.camera.x
        self.last_cam_y = self.camera.y
        self.last_zoom = self.camera.zoom
        self.surface_map = pygame.Surface((self.MAP_WIDTH * self.TILE_SIZE, self.MAP_HEIGHT * self.TILE_SIZE))

        self.noise_gen = RandomNoise(self.MAP_WIDTH, self.MAP_HEIGHT, 255, extra=65)
        self.noise_gen.randomize()
        self.transformer_tuiles()

        self.tuiles_debut = []
        self.placer_colonies(region_size=15, min_dist=20)
        self.tuile_debut = self.tuiles_debut[self.rand_tuile_debut()]
        self.colonie_joeur = Colonie(self.tuile_debut, self.objets)

        self.image_etoile = pygame.image.load(trouver_img("etoile.png"))
        self.image_etoile = pygame.transform.scale(self.image_etoile, (self.TILE_SIZE, self.TILE_SIZE))

    def rand_tuile_debut(self):
        return random.randint(0,3)

    def etoile_tuile_debut(self, start_x, start_y, end_x, end_y, tile_size):
        if self.in_menu:
            return
        x, y = self.colonie_joeur.tuile_debut
        if start_x <= x < end_x and start_y <= y < end_y:
            rect = pygame.Rect(x * tile_size, y * tile_size, tile_size, tile_size)
            self.screen.blit(pygame.transform.scale(self.image_etoile, (tile_size, tile_size)), self.camera.apply(rect))



    def placer_colonies(self, min_dist=5, region_size=10):
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
            placed = False
            while not placed:
                x = random.randint(region_x, region_x + region_size - 1)
                y = random.randint(region_y, region_y + region_size - 1)
                if isinstance(self.map_data[y][x], (Terre, Montagne)):
                    self.map_data[y][x].tuile_debut = True
                    self.map_data[y][x].color = couleurs_colonies[curr_couleur]  # Red color for colonies
                    placed = True
                    curr_couleur += 1
                    self.tuiles_debut.append((x, y))

    def get_colonies_coords(self):
        return self.tuiles_debut


    def transformer_tuiles(self):
        vals_noise = self.noise_gen.smoothNoise2d(smoothing_passes=20, upper_value_limit=1)
        for y in range(self.MAP_HEIGHT):
            for x in range(self.MAP_WIDTH):
                self.map_data[y][x].val_noise = vals_noise[y][x]  # Ensure correct indexing
                col = int(vals_noise[y][x] * 255)

                # Convert noise value to color
                if col < int(255 * self.water_amount):  # water
                    self.map_data[y][x] = Eau(x, y, self.TILE_SIZE, self.TILE_SIZE)
                    self.map_data[y][x].color = (0, 0, col)
                elif col < int(255 * (self.water_amount + self.sand_amount)):  # sand

                    self.map_data[y][x] = Sable(x, y, self.TILE_SIZE, self.TILE_SIZE)
                    self.map_data[y][x].color = (col, col, 0)
                elif col < int(255 * (self.water_amount + self.sand_amount + self.land_amount)):  # land

                    self.map_data[y][x] = Terre(x, y, self.TILE_SIZE, self.TILE_SIZE)
                    self.map_data[y][x].color = (0, col, 0)
                else:
                    self.map_data[y][x] = Montagne(x, y, self.TILE_SIZE, self.TILE_SIZE)
                    self.map_data[y][x].color = (0, 0, 0)

    def decouvrir_tuiles(self, x_tuile, y_tuile):
        for y in range(y_tuile - 2, y_tuile+3):
            for x in range(x_tuile - 2, x_tuile+3):
                if abs(x - x_tuile) + abs(y - y_tuile) <= 2:
                    if 0 <= x < self.MAP_WIDTH and 0 <= y < self.MAP_HEIGHT:
                        self.map_data[y][x].toggle_color()

    def draw_top_bar(self):
        bouton = Bouton(self.size[0] - 100, 25, 100, 30, "Options", self.menu_options, police, self.screen,self.objets)
        bouton.add_bordure(pygame.Color(192, 192, 192))
        pygame.draw.rect(self.screen, BLACK, (0, 0, self.size[0], 50))
        font = pygame.font.Font(None, 24)
        fps_info = font.render(f'FPS: {self.clock.get_fps():.2f}', True, YELLOW)
        zoom_info = font.render(f'Zoom: {self.camera.get_zoom() * 100:.2f}%', True, YELLOW)
        self.screen.blit(fps_info, (10, 10))
        self.screen.blit(zoom_info, (10, 30))


    def draw_tiles(self, start_x, start_y, end_x, end_y, tile_size):
        for y in range(start_y, end_y):
            for x in range(start_x, end_x):
                tile = self.map_data[y][x]
                tile_rect = pygame.Rect(x * tile_size, y * tile_size, tile_size, tile_size)
                tile.draw(self.screen, self.camera.apply(tile_rect), self.grid_mode)

    def menu_options(self):
        if self.in_menu:
            self.retour()

        else:
            self.objets.clear()
            surface = pygame.Surface((300, 500))
            surface.fill(BLACK)
            police1 = pygame.font.Font(trouver_font("LowresPixel-Regular.otf"), 36)
            texte_render = police1.render("Options", True, WHITE)
            police2 = pygame.font.Font(trouver_font("LowresPixel-Regular.otf"), 30)
            police_grids = pygame.font.Font(trouver_font("LowresPixel-Regular.otf"), 26)
            self.in_menu = True


            grid_mode_str = "ON" if self.grid_mode else "OFF"
            surface.blit(texte_render, [surface.get_width() / 2 - texte_render.get_rect().width / 2, 10])
            self.screen.blit(surface, (self.size[0] / 2 - 150, self.size[1] / 2 - 250))
            bouton_retour = Bouton(self.size[0] / 2, self.size[1] / 2 + 200, self.size[0] / 8, self.size[1] / 15,
                                   'Retour', self.retour, police2, self.screen, self.objets)
            bouton_grid_mode = Bouton(self.size[0] / 2, self.size[1] / 2 + 100, self.size[0] / 8, self.size[1] / 15,
                                      f'Grids: {grid_mode_str}', self.toggle_grid, police_grids, self.screen, self.objets)
            bouton_quitter = Bouton(self.size[0] / 2, self.size[1] / 2, self.size[0] / 8, self.size[1] / 15,
                                    'Quitter', self.quitter, police2, self.screen, self.objets)

    def toggle_grid(self):
        self.grid_mode = not self.grid_mode
        for obj in self.objets:
            if isinstance(obj, Bouton) and 'Grids' in obj.texte:
                grid_mode_str = "ON" if self.grid_mode else "OFF"
                obj.texte = f'Grids: {grid_mode_str}'

    def menu_principal(self):
        self.objets.clear()
        self.screen.fill('cyan')
        bouton_options = Bouton(self.size[0] - 100, 25, 100, 30, "Options", self.menu_options, police, self.screen,
                                self.objets)
    def retour(self):
        self.objets.clear()
        self.in_menu = False
        self.moving = True

    def quitter(self):
        self.running = False
        self.objets.clear()

    def handle_event(self, event):
        if event.type == pygame.QUIT:
            self.running = False
            self.objets.clear()

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.menu_options() if not self.in_menu else self.retour()
            elif event.key == pygame.K_q:
                self.menu_colonie = not self.menu_colonie

        elif event.type == pygame.MOUSEBUTTONDOWN and not self.in_menu:
            tile_size = (self.TILE_SIZE * self.camera.zoom)
            tile_x = int((self.camera.x + event.pos[0]) // tile_size)
            tile_y = int((self.camera.y + event.pos[1] - 50) // tile_size)
            self.moving= True
            if event.button == 1:  # Left click
                self.camera.start_drag(*event.pos)
                self.colonie_joeur.handle_click(event.pos, tile_x, tile_y, self.screen)
                if (tile_x, tile_y) == self.tuile_debut:
                    self.menu_colonie = not self.menu_colonie

            elif event.button == 4:
                if not self.colonie_joeur.scrolling: # Scroll up
                    self.camera.zoom_camera(*event.pos, "in")
                self.colonie_joeur.handle_scroll("up", event.pos)
            elif event.button == 5:
                if not self.colonie_joeur.scrolling: # Scroll down
                    self.camera.zoom_camera(*event.pos, "out")
                self.colonie_joeur.handle_scroll("down", event.pos)


        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                self.camera.stop_drag()
                self.moving = False

        elif event.type == pygame.MOUSEMOTION:
            self.camera.drag(*event.pos)
            self.colonie_joeur.handle_hover(event.pos)

    def trouver_tuiles_visibles(self) -> tuple:

        tile_size = (self.TILE_SIZE * self.camera.zoom)
        start_x = max(0, int(self.camera.x // tile_size))
        start_y = max(0, int(self.camera.y // tile_size))

        # On s'assure que la tuile de retrouve dans les limites de la carte
        end_x = min(int((self.camera.x + self.size[0]) // tile_size + 1), self.MAP_WIDTH)
        end_y = min(int((self.camera.y + self.size[1]) // tile_size + 1), self.MAP_HEIGHT)

        return start_x, start_y, end_x, end_y

    @profile
    def run(self):

        try:
            tile_size = int(self.TILE_SIZE * self.camera.zoom)
            start_x, start_y, end_x, end_y = self.trouver_tuiles_visibles()
            self.draw_tiles(start_x, start_y, end_x, end_y, tile_size)
            while self.running:
                for event in pygame.event.get():
                    self.handle_event(event)

                tile_size = int(self.TILE_SIZE * self.camera.zoom)
                start_x, start_y, end_x, end_y = self.trouver_tuiles_visibles()



                if not self.in_menu:
                    self.screen.fill(BLACK)
                    self.draw_tiles(start_x, start_y, end_x, end_y, tile_size)

                self.etoile_tuile_debut(start_x, start_y, end_x, end_y, tile_size)
                self.draw_top_bar()

                if self.menu_colonie:
                    self.colonie_joeur.menu_colonie(self.screen)

                if self.colonie_joeur.menu_fourmis_ouvert and self.menu_colonie:
                    self.colonie_joeur.menu_fourmis(self.screen)

                for obj in self.objets:
                    obj.process()

                pygame.display.update()
                self.clock.tick(60)


        finally:
            pygame.quit()

if __name__ == "__main__":
    carte = Carte()
    carte.run()