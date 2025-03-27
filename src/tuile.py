from config import WHITE, BLACK, BLUE
import pygame

class Tuile:
    def __init__(self, x, y, width, height, is_border=False):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.is_border = is_border
        self.tuile_debut = False
        self.decouverte = False if not self.tuile_debut else True
        self.color = BLACK if not self.decouverte else WHITE
        self.proprietaire = None
        self.val_noise = 0
        self.type = None
        self.fourmis = []
        self.en_utilisation = False #


    def toggle_color(self):
        if self.color == BLACK and not self.is_border:
            self.color = WHITE


    def draw(self, screen, rect, grid_mode):
        pygame.draw.rect(screen, self.color, rect)
        if grid_mode:
            pygame.draw.rect(screen, BLACK, rect, 1)

    def get_fourmis(self):
        if self.decouverte:
            return self.fourmis

class Eau(Tuile):
    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height)
    def process(self):
        pass
class Sable(Tuile):
    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height)
    def process(self):
        pass
class Terre(Tuile):
    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height)
    def process(self):
        pass
class Montagne(Tuile):
    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height)

    def process(self):
        pass
