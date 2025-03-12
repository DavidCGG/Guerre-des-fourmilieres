## Fichier pour declarer les variables de configuration
## et les constantes du jeu
import pygame
import os

WIDTH = 800
HEIGHT = 600

WHITE = pygame.Color("white")
BLACK = pygame.Color("black")
BLUE = pygame.Color("blue")
GREEN = pygame.Color("green")
YELLOW = pygame.Color("yellow")
RED = pygame.Color("red")
PURPLE = pygame.Color("purple")
ORANGE = pygame.Color("orange")

def trouver_img(nom: str) -> str:
    return os.path.join(os.path.dirname(__file__), "..", "assets", "images", nom)

def trouver_font(nom: str) -> str:
    return os.path.join(os.path.dirname(__file__), "..", "assets", "fonts", nom)