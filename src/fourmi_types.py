import pygame
from config import trouver_img
from fourmi import Fourmis, FourmisSprite

class Ouvriere(Fourmis):
    def __init__(self, x0, y0, couleur, colonie_origine, salle_initiale):
        super().__init__(colonie_origine, salle_initiale, hp=100, hp_max=100,atk=40, x0=x0, y0=y0, size=2,couleur=couleur)
        self.base_speed = 3
        self.speed = self.base_speed
        sprite_sheet_image=pygame.image.load(trouver_img(f"Fourmis/sprite_sheet_fourmi_{couleur.name.lower()}.png")).convert_alpha()
        self.type="ouvriere"
        self.sprite = FourmisSprite(self,sprite_sheet_image,32,32,8,100,1)
        self.inventaire_taille_max=1
        self.atk_result_with_epee = 70
        self.hp_max_with_armor = 150

class Soldat(Fourmis):
    def __init__(self, x0, y0, couleur,colonie_origine, salle_initiale):
        super().__init__(colonie_origine, salle_initiale, hp=150, hp_max=150,atk=60, x0=x0, y0=y0, size=2,couleur=couleur)
        self.base_speed = 1.5
        self.speed = self.base_speed
        sprite_sheet_image = pygame.image.load(trouver_img(f"Fourmis/sprite_sheet_fourmi_{couleur.name.lower()}.png")).convert_alpha()
        self.type = "soldat"
        self.sprite = FourmisSprite(self, sprite_sheet_image, 32, 32, 8, 100, 1)
        self.inventaire_taille_max=2
        self.atk_result_with_epee=90
        self.hp_max_with_armor=200