import random

from config import WHITE, BLACK, BLUE
import pygame

from config import trouver_img
from config import TypeItem


class Tuile:
    def __init__(self, x, y, width, height, texture_string="Monde/noise32x32.png",is_border=False):
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
        self.fourmis = None
        self.en_utilisation = False

        self.tuile_ressource = self.rand_ressource()
        self.collectee = False if self.tuile_ressource else None
        self.timer = 0
        self.image_metal = pygame.image.load(trouver_img("Items/metal.png")).convert_alpha() if self.tuile_ressource else None
        self.image_pomme = pygame.image.load(trouver_img("Items/pomme.png")).convert_alpha() if self.tuile_ressource else None
        self.image_bois = pygame.image.load(trouver_img("Items/bois.png")).convert_alpha() if self.tuile_ressource else None

        #créer image de tuile selon couleur
        #self.image = pygame.image.load(trouver_img("Monde/noise32x32.png")).convert_alpha()
        #self.image = pygame.image.load(trouver_img("Test64x64.png"))
        self.image = pygame.image.load(trouver_img(texture_string)).convert_alpha()
        self.last_color=self.color


    def rand_ressource(self):
        if self.tuile_debut: return False
        if isinstance(self, Sable):
            rand = random.randint(0, 8)
            if rand == 5:
                self.type = "Metal"
                return True
        if isinstance(self, Terre):
            rand = random.randint(0, 32)
            if rand == 10:
                rand = random.randint(0, 1)
                if rand == 1:
                    self.type = "Pomme"
                else: self.type = "Bois"
                return True
        else: return False

    def toggle_color(self):
        if self.color == BLACK and not self.is_border:
            self.color = WHITE


    def draw(self, screen, rect, grid_mode, dt):
        if self.collectee:
            self.timer += dt
        if self.timer >= 5000:
            self.collectee = False
            self.timer = 0

        if self.color!=self.last_color:
            #modifie la texture noise pour donner la couleur
            surf = pygame.Surface(self.image.get_rect().size, pygame.SRCALPHA)
            surf.fill((int(self.color[0]**2/255),int(self.color[1]**2/255),int(self.color[2]**2/255)))
            self.image.blit(surf, (0, 0), None, pygame.BLEND_MULT)

            self.last_color=self.color

        #draw image plutot que rectangle couleur
        scaled_img = pygame.transform.scale(self.image, (rect.width, rect.height))
        screen.blit(scaled_img,rect)

        #pygame.draw.rect(screen, self.color, rect)
        if grid_mode:
            pygame.draw.rect(screen, BLACK, rect, 1)
        if self.tuile_ressource and not self.collectee and not self.tuile_debut:
            if isinstance(self, Sable):
                scaled_img = pygame.transform.scale(self.image_metal, (rect.width, rect.height) )
                screen.blit(scaled_img, rect)
            if isinstance(self, Terre):
                if self.type == "Pomme":
                    scaled_img = pygame.transform.scale(self.image_pomme, (rect.width, rect.height))
                elif self.type == "Bois":
                    scaled_img = pygame.transform.scale(self.image_bois, (rect.width, rect.height))
                screen.blit(scaled_img, rect)


    def get_fourmis(self):
        if self.decouverte:
            return self.fourmis

    def get_ressource(self):
        if isinstance(self, Sable):
            return TypeItem.METAL
        elif isinstance(self, Terre):
            if self.type == "Pomme":
                return TypeItem.POMME
            if self.type == "Bois":
                return TypeItem.BOIS

class Eau(Tuile):
    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height,"Monde/eau32x32.png")
    def process(self):
        pass
class Sable(Tuile):
    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height,"Monde/sable32x32.png")
    def process(self):
        pass
class Terre(Tuile):
    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height,"Monde/terre32x32.png")
    def process(self):
        pass
class Montagne(Tuile):
    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height,"Monde/montagne32x32.png")

    def process(self):
        pass
