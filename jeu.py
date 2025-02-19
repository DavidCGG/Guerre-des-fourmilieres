#import sys
from carte import Map
import pygame

from pygame.locals import *

pygame.init()
screen = pygame.display.set_mode((1280,720), pygame.SCALED)
clock = pygame.time.Clock()
running = True
dt=0
objets = []

police = pygame.font.SysFont("Comic Sans MS",45)

player_pos = pygame.Vector2(screen.get_width()/2,screen.get_height()/2)

pygame.display.set_caption("Guerre des fourmilières")

image_icone=pygame.image.load('assets/fourmi_noire.png')
pygame.display.set_icon(image_icone)

class Bouton():
    def __init__(self,x,y,largeur,hauteur,texte,fonction_sur_click):
        self.x=x-largeur/2
        self.y=y-hauteur/2
        self.largeur = largeur
        self.hauteur = hauteur
        self.texte = texte
        self.police = police
        self.fonction_sur_click = fonction_sur_click
        self.couleurs = { 'normale': '#ffffff',
                          'survol': '#666666',
                          'clické': '#333333'}
        self.surface = pygame.Surface((self.largeur,self.hauteur))
        self.rectangle = pygame.Rect(self.x,self.y,self.largeur,self.hauteur)
        self.texte_render = police.render(self.texte,True,"black")
        self.deja_clicke = False
        objets.append(self)

        self.pas_encore_blit=True

        print(self.x, self.y)

    def process(self):
        position_souris = pygame.mouse.get_pos()
        self.surface.fill(self.couleurs['normale'])
        if self.rectangle.collidepoint(position_souris):
            #survol:
            self.surface.fill(self.couleurs['survol'])

            if pygame.mouse.get_pressed(num_buttons=3)[0]:
                #sur click tenu :
                self.surface.fill(self.couleurs['clické'])
                if not self.deja_clicke:
                    print('Bouton \''+self.texte+'\' clické')
                    self.fonction_sur_click()
                    self.deja_clicke=True
            else:
                self.deja_clicke=False

        if self.pas_encore_blit:
            self.surface.blit(self.texte_render,[self.rectangle.width/2-self.texte_render.get_rect().width/2,self.rectangle.height/2-self.texte_render.get_rect().height/2])
            screen.blit(self.surface,self.rectangle)
            self.pas_encore_blit=False

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
    screen.fill('blue')
    #pygame.display.update()
    print('Nouvelle parite')
    game = Map()
    game.start_game()

def menu_options():
    print('menu options')
    objets.clear()
    #pygame.display.update()
    screen.fill('green')
    bouton_retour = Bouton(screen.get_width() / 2, screen.get_height() * 9 / 10, screen.get_width()/3, screen.get_height()/15, 'Retour', menu_principal)

def quitter():
    quit()

def menu_principal():
    objets.clear()
    screen.fill('cyan')
    surface_titre = police.render("Guerre des fourmilières",True,'black')
    screen.blit(surface_titre, (screen.get_width()/2-surface_titre.get_rect().width/2,screen.get_height()/10-surface_titre.get_rect().height/2))
    image_menu_principal=pygame.transform.scale(image_icone,(screen.get_height()*image_icone.get_height()/100,screen.get_height()*image_icone.get_height()/100))
    screen.blit(image_menu_principal,(screen.get_width()/2-image_menu_principal.get_width()/2,screen.get_height()*3/10-image_menu_principal.get_height()/2))
    bouton_nouvelle_partie = Bouton(screen.get_width() / 2, screen.get_height() * 5 / 10, screen.get_width()/3, screen.get_height()/15, 'Nouvelle partie', nouvelle_partie)
    bouton_options = Bouton(screen.get_width() / 2, screen.get_height() * 6 / 10, screen.get_width()/3, screen.get_height()/15, 'Options', menu_options)
    bouton_quitter = Bouton(screen.get_width() / 2, screen.get_height() * 7 / 10, screen.get_width()/3, screen.get_height()/15, 'Quitter', quitter)

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