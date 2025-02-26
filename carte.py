import pygame
import os
from numpy import array
from config import WHITE, BLACK, YELLOW, RED, BLUE
from camera import Camera

class Tile:
    def __init__(self, x, y, width, color, height, is_border=False):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = WHITE
        self.is_border = is_border

    def toggle_color(self):
        if self.color == WHITE:
            self.color = BLUE
        else:
            self.color = WHITE

    def draw(self, screen, rect):
        pygame.draw.rect(screen, self.color, rect)
        if not self.is_border:
            pygame.draw.rect(screen, BLACK, rect, 1)

class MapApp:
    def __init__(self):
        pygame.init()
        self.running = True
        self.size = (1280, 720)
        self.screen = pygame.display.set_mode(self.size, pygame.SCALED)
        pygame.display.set_caption("Tile Map with Camera")

        self.TILE_SIZE = 32
        self.MAP_WIDTH = 100
        self.MAP_HEIGHT = 100
        self.map_data = [[Tile(x, y, self.TILE_SIZE, self.TILE_SIZE, WHITE) for x in range(self.MAP_WIDTH)] for y in range(self.MAP_HEIGHT)]
        for y in range(self.MAP_HEIGHT):
            for x in range(self.MAP_WIDTH):
                if x == 0 or y == 0 or x == self.MAP_WIDTH - 1 or y == self.MAP_HEIGHT - 1:
                    self.map_data[y][x].is_border = True
                    self.map_data[y][x].color = RED

        self.camera = Camera(self.size[0], self.size[1], self.MAP_WIDTH, self.MAP_HEIGHT, self.TILE_SIZE)

    def draw_top_bar(self):
        pygame.draw.rect(self.screen, BLACK, (0, 0, self.size[0], 50))
        font = pygame.font.Font(None, 24)
        camera_info = font.render(f'Camera X: {int(self.camera.x)}, Camera Y: {int(self.camera.y)}', True, YELLOW)
        zoom_info = font.render(f'Zoom: {self.camera.get_zoom() * 100:.2f}%', True, YELLOW)
        self.screen.blit(camera_info, (10, 10))
        self.screen.blit(zoom_info, (10, 30))

    def draw_tiles(self):
        tile_size = int(self.TILE_SIZE * self.camera.zoom)
        start_x = max(0, self.camera.x // tile_size)
        start_y = max(0, self.camera.y // tile_size)
        end_x = min((self.camera.x + self.size[0]) // tile_size + 1, self.MAP_WIDTH)
        end_y = min((self.camera.y + self.size[1]) // tile_size + 1, self.MAP_HEIGHT)

        for y in range(int(start_y), int(end_y)):
            for x in range(int(start_x), int(end_x)):
                tile = self.map_data[y][x]
                tile_rect = pygame.Rect(x * tile_size, y * tile_size, tile_size, tile_size)
                tile.draw(self.screen, self.camera.apply(tile_rect))

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
                    self.map_data[grid_y][grid_x].toggle_color()
            elif event.button == 4:  # Scroll up
                self.camera.zoom_camera(*event.pos, "in")
            elif event.button == 5:  # Scroll down
                self.camera.zoom_camera(*event.pos, "out")

        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                self.camera.stop_drag()

        elif event.type == pygame.MOUSEMOTION:
            self.camera.drag(*event.pos)

    def run(self):
        clock = pygame.time.Clock()
        while self.running:
            for event in pygame.event.get():
                self.handle_event(event)
            self.screen.fill(BLACK)
            self.draw_tiles()
            self.draw_top_bar()
            pygame.display.flip()
            clock.tick(120)
        pygame.quit()

if __name__ == "__main__":
    app = MapApp()
    app.run()