#import sys
from carte import Carte
import config
import pygame
from bouton import Bouton

pygame.init()
screen = pygame.display.set_mode((1280,720), pygame.SCALED)
clock = pygame.time.Clock()
running = True
dt=0
objets = []

police = pygame.font.SysFont("Comic Sans MS",42)

player_pos = pygame.Vector2(screen.get_width()/2,screen.get_height()/2)

pygame.display.set_caption("Guerre des fourmilières")

image_icone=pygame.image.load(config.trouver_img('fourmi_noire.png'))
pygame.display.set_icon(image_icone)

class Fourmiliere():
    def __init__(self,salles):
        self.salles=salles

class Salle():
    def __init__(self,type,salles_reliees):
        self.type=type
        self.salles_reliees=salles_reliees


class Fourmi():
    def __init__(self,x,y):
        self.image=pygame.image.load('assets/fourmi_noire.png')
        self.x=x
        self.y=y

        """
        if type=='lourd':
            self.HP_max=100
            self.poids_max=100
            self.vitesse_base=25
            self.dexterite=25
        elif type=='moyen':
            self.HP_max=75
            self.poids_max=50
            self.vitesse_base=50
            self.dexterite=50
        elif type=='leger':
            self.HP_max=50
            self.poids_max=25
            self.vitesse_max=100
            self.dexterite=100
        """

class Partie():
    def __init__(self):
        self.temps=0
        objets.append(self)
    def process(self):
        self.temps+=1

def nouvelle_partie():
    objets.clear()
    partie = Partie()

    print('Nouvelle parite')
    game = Carte()
    game.run()

def menu_options():
    print('menu options')
    objets.clear()
    #pygame.display.update()
    screen.fill('green')
    bouton_retour = Bouton(screen.get_width() / 2, screen.get_height() * 9 / 10, screen.get_width()/3, screen.get_height()/15, 'Retour', menu_principal, police)
    objets.append(bouton_retour)

def quitter():
    quit()

def menu_principal():
    objets.clear()
    screen.fill('cyan')
    surface_titre = police.render("Guerre des fourmilières",True,'black')
    screen.blit(surface_titre, (screen.get_width()/2-surface_titre.get_rect().width/2,screen.get_height()/10-surface_titre.get_rect().height/2))
    image_menu_principal=pygame.transform.scale(image_icone,(screen.get_height()*image_icone.get_height()/100,screen.get_height()*image_icone.get_height()/100))
    screen.blit(image_menu_principal,(screen.get_width()/2-image_menu_principal.get_width()/2,screen.get_height()*3/10-image_menu_principal.get_height()/2))
    bouton_nouvelle_partie = Bouton(screen.get_width() / 2, screen.get_height() * 5 / 10, screen.get_width()/3, screen.get_height()/15, 'Nouvelle partie', nouvelle_partie, police, screen)
    bouton_options = Bouton(screen.get_width() / 2, screen.get_height() * 6 / 10, screen.get_width()/3, screen.get_height()/15, 'Options', menu_options, police, screen)
    bouton_quitter = Bouton(screen.get_width() / 2, screen.get_height() * 7 / 10, screen.get_width()/3, screen.get_height()/15, 'Quitter', quitter, police, screen)
    objets.append(bouton_nouvelle_partie)
    objets.append(bouton_options)
    objets.append(bouton_quitter)

menu_principal()
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    #screen.fill(pygame.Color(100,50,0))

    """
    if dt != 0:
        pygame.display.set_caption(str(1/dt))
    """

    for object in objets:
        object.process()

    pygame.display.flip()

    dt = clock.tick() / 1000

pygame.quit()
#sys.exit()

