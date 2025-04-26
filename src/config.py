## Fichier pour declarer les variables de configuration
## et les constantes du jeu
import pygame
import os

SCREEN_WIDTH: int = 1280
SCREEN_HEIGHT: int = 720

WHITE = pygame.Color("white")
BLACK = pygame.Color("black")
BLUE = pygame.Color("blue")
GREEN = pygame.Color("green")
YELLOW = pygame.Color("yellow")
RED = pygame.Color("red")
PURPLE = pygame.Color("purple")
ORANGE = pygame.Color("orange")
AQUA = pygame.Color("aqua")

def trouver_img(nom: str) -> str:
    return os.path.join(os.path.dirname(__file__), "..", "assets", "images", nom)

def trouver_font(nom: str) -> str:
    return os.path.join(os.path.dirname(__file__), "..", "assets", "fonts", nom)