import pygame
import os
from numpy import array
from config import WHITE, BLACK, YELLOW, RED, BLUE
from config import trouver_font
from camera import Camera
from generation_map import GenerationMap
from random_noise import RandomNoise
from bouton import Bouton

pygame.font.init()
police = pygame.font.Font(trouver_font("LowresPixel-Regular.otf"), 22)

class Carte:
    def __init__(self):
        pygame.init()
        self.running = True
        self.size = (1280, 720)
        self.screen = pygame.display.set_mode(self.size, pygame.SCALED)
        pygame.display.set_caption("Guerre des fourmilières")
        self.water_amount = 0.48
        self.sand_amount = 0.007
        self.land_amount = 0.42

        self.TILE_SIZE = 32
        self.MAP_WIDTH = 100
        self.MAP_HEIGHT = 100
        self.gen_map = GenerationMap(self.MAP_WIDTH, self.MAP_HEIGHT, self.TILE_SIZE)
        self.map_data = self.gen_map.liste_tuiles()
        self.objets = []

        self.camera = Camera(self.size[0], self.size[1], self.MAP_WIDTH, self.MAP_HEIGHT, self.TILE_SIZE)
        self.surface_map = pygame.Surface((self.MAP_WIDTH * self.TILE_SIZE, self.MAP_HEIGHT * self.TILE_SIZE))

        self.noise_gen = RandomNoise(self.MAP_WIDTH, self.MAP_HEIGHT, 255, extra=50)
        self.noise_gen.randomize()
        self.transformer_tuiles()

    def transformer_tuiles(self):
        vals_noise = self.noise_gen.smoothNoise2d(smoothing_passes=20, upper_value_limit=1)
        for y in range(self.MAP_HEIGHT):
            for x in range(self.MAP_WIDTH):
                self.map_data[y][x].val_noise = vals_noise[y][x]  # Ensure correct indexing
                col = int(vals_noise[y][x] * 255)

                # Convert noise value to color
                if col < int(255 * self.water_amount):  # water
                    self.map_data[y][x].color = (0, 0, col)
                    self.map_data[y][x].type = "eau"
                elif col < int(255 * (self.water_amount + self.sand_amount)):  # sand
                    self.map_data[y][x].color = (col, col, 0)
                    self.map_data[y][x].type = "sable"
                elif col < int(255 * (self.water_amount + self.sand_amount + self.land_amount)):  # land
                    self.map_data[y][x].color = (0, col, 0)
                    self.map_data[y][x].type = "terre"
                else:
                    self.map_data[y][x].color = (col, col, col)
                    self.map_data[y][x].type = "montagne"

    def decouvrir_tuiles(self, x_tuile, y_tuile):
        for y in range(y_tuile - 2, y_tuile+3):
            for x in range(x_tuile - 2, x_tuile+3):
                if abs(x - x_tuile) + abs(y - y_tuile) <= 2:
                    if 0 <= x < self.MAP_WIDTH and 0 <= y < self.MAP_HEIGHT:
                        self.map_data[y][x].toggle_color()


    def draw_top_bar(self):
        bouton = Bouton(self.size[0]-100, 25, 100, 30, "Options", lambda: print("Bouton cliqué"), police, self.screen)
        pygame.draw.rect(self.screen, BLACK, (0, 0, self.size[0], 50))
        font = pygame.font.Font(None, 24)
        camera_info = font.render(f'Camera X: {int(self.camera.x)}, Camera Y: {int(self.camera.y)}', True, YELLOW)
        zoom_info = font.render(f'Zoom: {self.camera.get_zoom() * 100:.2f}%', True, YELLOW)
        self.screen.blit(camera_info, (10, 10))
        self.screen.blit(zoom_info, (10, 30))
        self.objets.append(bouton)

    def draw_tiles(self, start_x, start_y, end_x, end_y, tile_size):
        for y in range(start_y, end_y):
            for x in range(start_x, end_x):
                tile = self.map_data[y][x]
                tile_rect = pygame.Rect(x * tile_size, y * tile_size, tile_size, tile_size)
                tile.draw(self.screen, self.camera.apply(tile_rect))


    def draw_tiles_experimental(self):
        surface_zoomee = pygame.transform.scale(self.surface_map,(
                    int(self.MAP_WIDTH * self.TILE_SIZE * self.camera.zoom),
                    int(self.MAP_HEIGHT * self.TILE_SIZE * self.camera.zoom)
                    )
        )
        self.screen.blit(surface_zoomee, (-self.camera.x, -self.camera.y + 50))

    def handle_event(self, event):
        if event.type == pygame.QUIT:
            self.running = False

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                self.camera.start_drag(*event.pos)
                tile_size = int(self.TILE_SIZE * self.camera.zoom)
                grid_x = int((event.pos[0] + self.camera.x) // tile_size)
                grid_y = int((event.pos[1] + self.camera.y - 50) // tile_size)

                if 0 <= grid_x < self.MAP_WIDTH and 0 <= grid_y < self.MAP_HEIGHT:
                    self.decouvrir_tuiles(grid_x, grid_y)
                    print(f'Clicked on tile x:{grid_x}, y:{grid_y}')
            elif event.button == 4:  # Scroll up
                self.camera.zoom_camera(*event.pos, "in")
            elif event.button == 5:  # Scroll down
                self.camera.zoom_camera(*event.pos, "out")

        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                self.camera.stop_drag()

        elif event.type == pygame.MOUSEMOTION:
            self.camera.drag(*event.pos)

    def trouver_tuiles_visibles(self) -> tuple:

        tile_size = (self.TILE_SIZE * self.camera.zoom)
        start_x = max(0, int(self.camera.x // tile_size))
        start_y = max(0, int(self.camera.y // tile_size))

        # Ensure end_x and end_y round *up* to include partially visible tiles
        end_x = min(int((self.camera.x + self.size[0]) // tile_size + 1), self.MAP_WIDTH)
        end_y = min(int((self.camera.y + self.size[1]) // tile_size + 1), self.MAP_HEIGHT)

        return start_x, start_y, end_x, end_y

    def run(self):
        clock = pygame.time.Clock()
        while self.running:
            for event in pygame.event.get():
                self.handle_event(event)
            tile_size = int(self.TILE_SIZE * self.camera.zoom)
            start_x, start_y, end_x, end_y = self.trouver_tuiles_visibles()
            self.draw_tiles(start_x, start_y, end_x, end_y, tile_size)
            self.draw_top_bar()

            for obj in self.objets:
                obj.process()

            pygame.display.flip()
            clock.tick(60)
        pygame.quit()

if __name__ == "__main__":
    carte = Carte()
    carte.run()