## Fichier pour declarer les variables de configuration
## et les constantes du jeu
from enum import Enum

import pygame
import os

#SCREEN_WIDTH: int = 1280
#SCREEN_HEIGHT: int = 720

WHITE = pygame.Color("white")
BLACK = pygame.Color("black")
BLUE = pygame.Color("blue")
GREEN = pygame.Color("green")
YELLOW = pygame.Color("yellow")
RED = pygame.Color("red")
PURPLE = pygame.Color("purple")
ORANGE = pygame.Color("orange")
AQUA = pygame.Color("aqua")
BROWN = pygame.Color("saddlebrown")
GRAY = pygame.Color("gray40")
BEIGE = pygame.Color("bisque")
SKY_BLUE= pygame.Color(110, 180, 235)

def trouver_img(nom: str) -> str:
    return os.path.join(os.path.dirname(__file__), "..", "assets", "images", nom)

def trouver_font(nom: str) -> str:
    return os.path.join(os.path.dirname(__file__), "..", "assets", "fonts", nom)

def trouver_audio(nom: str) -> str:
    return os.path.join(os.path.dirname(__file__), "..", "assets", "audio", nom)

class Bouton():
    def __init__(self, screen, x, y, largeur, hauteur, texte, fonction_sur_click, police):
        #self.surface=surface
        self.screen=screen
        self.x = x - largeur / 2
        self.y = y - hauteur / 2
        self.largeur = largeur
        self.hauteur = hauteur
        self.texte = texte
        self.police = police
        self.fonction_sur_click = fonction_sur_click
        self.surface_self = pygame.Surface((self.largeur, self.hauteur))
        self.couleurs = {'normale': '#ffffff',
                         'survol': '#666666',
                         'clické': '#333333'}
        self.rectangle = pygame.Rect(self.x, self.y, self.largeur, self.hauteur)
        self.texte_render = police.render(self.texte, False, "black")
        self.deja_clicke = True

    def draw(self):
        #print("bouton "+self.texte+" drawn")
        position_souris = pygame.mouse.get_pos()
        self.surface_self.fill(self.couleurs['normale'])
        cursor_sur_bouton=False
        if self.rectangle.collidepoint(position_souris):
            # survol:
            self.surface_self.fill(self.couleurs['survol'])
            cursor_sur_bouton=True
            if pygame.mouse.get_pressed(num_buttons=3)[0]:
                # sur click tenu :
                self.surface_self.fill(self.couleurs['clické'])
                if not self.deja_clicke:
                    self.fonction_sur_click()
                self.deja_clicke = True
            else:
                self.deja_clicke = False

        self.surface_self.blit(self.texte_render, [self.rectangle.width / 2 - self.texte_render.get_rect().width / 2,self.rectangle.height / 2 - self.texte_render.get_rect().height / 2])
        pygame.draw.rect(self.surface_self, pygame.Color("black"), self.surface_self.get_rect(), 3)
        self.screen.blit(self.surface_self, (self.x, self.y))
        return cursor_sur_bouton

class TypeItem(Enum):
    #NOM=(weight,image path)
    POMME=(1,trouver_img("Items/pomme.png"))
    METAL=(3,trouver_img("Items/metal.png"))
    BOIS=(2,trouver_img("Items/bois.png"))
    OEUF=(1,trouver_img("Items/oeuf.png"))
    ARMURE=(2,trouver_img("Items/armure.png"))
    EPEE=(1,trouver_img("Items/epee.png"))