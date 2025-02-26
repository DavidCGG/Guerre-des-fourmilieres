from config import WHITE, BLACK, BLUE
import pygame

class Tuile:
    def __init__(self, x, y, width, height, is_border=False):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = BLACK
        self.is_border = is_border
        self.tuile_debut = False
        self.decouverte = False if not self.tuile_debut else True
        self.proprietaire = None
        self.tuile_debut = False


    def toggle_color(self):
        if self.color == BLACK and not self.is_border:
            self.color = WHITE


    def draw(self, screen, rect):
        pygame.draw.rect(screen, self.color, rect)
        if not self.is_border:
            pygame.draw.rect(screen, BLACK, rect, 1)



