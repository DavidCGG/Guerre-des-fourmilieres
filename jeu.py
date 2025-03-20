#import sys
from carte import MapApp
import pygame
from classes import *

from pygame.locals import *

pygame.init()
screen = pygame.display.set_mode((1280,720), pygame.SCALED)
screen_pointer = [screen]
clock = pygame.time.Clock()
running = True
dt=0
dt_pointer=[dt]
objets = []
colonies = []
fourmis=[]
hud=[]
max_fps=30
colonie_presente=[]

police = pygame.font.SysFont("Comic Sans MS",42)

player_pos = pygame.Vector2(screen.get_width()/2,screen.get_height()/2)

pygame.display.set_caption("Guerre des fourmilières")

image_icone=pygame.image.load('assets/fourmi_noire.png')
pygame.display.set_icon(image_icone)

carte=[]

def nouvelle_partie():
    objets.clear()
    partie = Partie()


    print('Nouvelle parite')
    titre="test"
    with open("parties_sauvegardees/"+".txt", "w") as fichier:
        fichier.write("Created using write mode.")

    colonie_joueur=Colonie("joueur",dt_pointer,screen_pointer,fourmis,600,500)
    colonies.append(colonie_joueur)
    entrer_colonie(colonie_joueur)

    carte.append(Carte(screen_pointer, colonies,fourmis))
    #game = MapApp()
    #game.run()

def entrer_carte():
    objets.clear()
    objets.append(carte[0])
    colonie_presente.clear()
    print("carte entré")

def entrer_colonie(colonie_entree):
    objets.clear()
    objets.append(colonie_entree)
    print(colonie_entree.nom)
    colonie_presente.append(colonie_entree)
    print("Colonie " + colonie_entree.nom + " entrée")
    objets.append(Bouton(screen,screen.get_width() / 2, screen.get_height() / 20, screen.get_width()/3, screen.get_height()/15, "Carte du monde", entrer_carte,police))

def menu_options():
    print('menu options')
    objets.clear()
    #pygame.display.update()
    screen.fill('green')
    objets.append(Bouton(screen,screen.get_width() / 2, screen.get_height() * 9 / 10, screen.get_width()/3, screen.get_height()/15, 'Retour', menu_principal,police))

def quitter():
    quit()

def menu_principal():
    objets.clear()
    surface_menu_principal = pygame.Surface((screen.get_width(), screen.get_height()))
    surface_menu_principal.fill('cyan')

    surface_titre = police.render("Guerre des fourmilières",True,'black')
    surface_menu_principal.blit(surface_titre, (screen.get_width()/2-surface_titre.get_rect().width/2,screen.get_height()/10-surface_titre.get_rect().height/2))
    image_menu_principal=pygame.transform.scale(image_icone,(screen.get_height()*image_icone.get_height()/100,screen.get_height()*image_icone.get_height()/100))
    surface_menu_principal.blit(image_menu_principal,(screen.get_width()/2-image_menu_principal.get_width()/2,screen.get_height()*3/10-image_menu_principal.get_height()/2))

    objets.append(Bouton(screen,screen.get_width() / 2, screen.get_height() * 5 / 10, screen.get_width()/3, screen.get_height()/15, 'Nouvelle partie', nouvelle_partie,police))
    objets.append(Bouton(screen,screen.get_width() / 2, screen.get_height() * 6 / 10, screen.get_width()/3, screen.get_height()/15, 'Options', menu_options,police))
    objets.append(Bouton(screen,screen.get_width() / 2, screen.get_height() * 7 / 10, screen.get_width()/3, screen.get_height()/15, 'Quitter', quitter,police))

    screen.blit(surface_menu_principal,(0,0))

menu_principal()
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    #screen.fill(pygame.Color(100,50,0))
    #input manager


    """
    if dt != 0:
        pygame.display.set_caption(str(1/dt))
    """
    for colonie in colonies:
        colonie.process()
    if len(carte)==1:
        carte[0].process()
    for fourmi in fourmis:
        fourmi.process()
        if fourmi.dans_colonie is None:
            fourmi.carte_input_process()
        elif len(colonie_presente)!=0:
            if (fourmi.dans_colonie.nom==colonie_presente[0].nom):
                fourmi.colonie_input_process()
    for objet_a_dessine in objets:
        objet_a_dessine.draw()

    #draw fourmi here instead of carte and colonie
    """for fourmi in fourmis:
        if len(colonie_presente)!=0:
            #print("A")
            if fourmi.dans_colonie is not None:
                #print("C")
                if fourmi.dans_colonie.nom==colonie_presente[0].nom:
                    #print("D")
                    fourmi.draw()
        else:
            #print("B")
            if fourmi.dans_colonie is None:
                fourmi.draw()"""

    pygame.display.flip()

    dt = clock.tick(max_fps) / 1000
    dt_pointer = [dt]
    screen_pointer = [screen]
    #print(dt)

pygame.quit()
#sys.exit()