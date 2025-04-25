import random

from config import WHITE, BLACK, BLUE
import pygame

from src.config import trouver_img


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
        self.en_utilisation = False

        self.tuile_ressource = self.rand_ressource()
        self.collectee = False if self.tuile_ressource else None
        self.image_metal = pygame.image.load(trouver_img("metal.png")).convert_alpha() if self.tuile_ressource else None
        self.image_pomme = pygame.image.load(trouver_img("pomme.png")).convert_alpha() if self.tuile_ressource else None

    def rand_ressource(self):
        if isinstance(self, Sable):
            rand = random.randint(0, 8)
            if rand == 5:
                return True
        if isinstance(self, Terre):
            rand = random.randint(0, 32)
            if rand == 10:
                return True

        else: return False

    def toggle_color(self):
        if self.color == BLACK and not self.is_border:
            self.color = WHITE


    def draw(self, screen, rect, grid_mode):
        pygame.draw.rect(screen, self.color, rect)
        if grid_mode:
            pygame.draw.rect(screen, BLACK, rect, 1)
        if self.tuile_ressource and not self.collectee and not self.tuile_debut:
            if isinstance(self, Sable):
                scaled_img = pygame.transform.scale(self.image_metal, (rect.width, rect.height) )
                screen.blit(scaled_img, rect)
            if isinstance(self, Terre):
                scaled_img = pygame.transform.scale(self.image_pomme, (rect.width, rect.height) )
                screen.blit(scaled_img, rect)


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
