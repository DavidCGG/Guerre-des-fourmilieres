import pygame
from pygame import Vector2


class Colonie:
    def __init__(self, nom, dt,screen,liste_fourmis):
        self.nom = nom
        self.dt = dt
        self.salles = [Salle(100, 600, "Throne"),Salle(900, 500, "Banque"), ]
        self.screen = screen
        self.fourmis=[Fourmi("moyen",dt,self,self.screen,liste_fourmis)]
        # objets.append(self)
    def process(self):
        for salle in self.salles:
            salle.process()
    def draw(self):
        print("Colonie "+self.nom+" dessinee")

class Salle:
    def __init__(self, x, y, sorte):
        self.x = x
        self.y = y
        self.sorte = sorte

        # self.rectanlge = pygame.Rect()
        if (self.sorte == "Throne"):
            self.reine_hp = 1000
            self.largeur = 400
            self.hauteur = 400
        elif (self.sorte == "Banque"):
            self.ressources_max = 1000
            self.ressources = 0
            self.largeur = 300
            self.hauteur = 150
        # objets.append(self)

    def process(self):
        if (self.sorte == "Throne"):
            self.reine_hp += 1
            police = pygame.font.SysFont("Comic Sans MS", 42)
        elif (self.sorte == "Banque"):
            self.ressources += 2
            if(self.ressources>self.ressources_max):
                self.ressources=self.ressources_max


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
        self.texte_render = police.render(self.texte, True, "black")
        self.deja_clicke = False

    def draw(self):
        position_souris = pygame.mouse.get_pos()
        self.surface_self.fill(self.couleurs['normale'])
        clicke=False
        if self.rectangle.collidepoint(position_souris):
            # survol:
            self.surface_self.fill(self.couleurs['survol'])

            if pygame.mouse.get_pressed(num_buttons=3)[0]:
                # sur click tenu :
                self.surface_self.fill(self.couleurs['clické'])
                self.deja_clicke = True
                clicke=True

        self.surface_self.blit(self.texte_render, [self.rectangle.width / 2 - self.texte_render.get_rect().width / 2,self.rectangle.height / 2 - self.texte_render.get_rect().height / 2 - 3])
        pygame.draw.rect(self.surface_self, pygame.Color("black"), self.surface_self.get_rect(), 3)
        self.screen.blit(self.surface_self, (self.x, self.y))
        if(clicke):
            self.fonction_sur_click()


class Fourmi():
    def __init__(self, type, dt, colonie_origine,screen,liste_fourmis):
        self.image = pygame.image.load('assets/fourmi_noire.png')
        self.pos = Vector2(colonie_origine.salles[0].x,colonie_origine.salles[0].y)
        self.HP_max = 0
        self.poids_max = 0
        self.vitesse_base = 0
        self.dexterite = 0
        self.destination = None
        self.dt=dt
        self.colonie_origine=colonie_origine
        self.dans_colonie=colonie_origine
        self.screen=screen
        self.type=type
        liste_fourmis.append(self)
        if self.type=='lourd':
            self.HP_max=100
            self.poids_max=100
            self.vitesse_base=25
            self.dexterite=25
        elif self.type=='moyen':
            self.HP_max=75
            self.poids_max=50
            self.vitesse_base=50
            self.dexterite=50
        elif self.type=='leger':
            self.HP_max=50
            self.poids_max=25
            self.vitesse_base=100
            self.dexterite=100
        else:
            raise Exception("Type fourmi invalide")

    def process(self):
        print("dest:"+str(self.destination))
        print("pos:"+str(self.pos))

        if(self.destination!=None):
            if(abs((self.pos-self.destination).magnitude()) < 10):
                print("destination atteinte")
                self.destination=None
            else:
                print("fourmi en movement: "+str((self.destination-self.pos).normalize()*self.dt[0]*self.vitesse_base*5))
                self.pos+=(self.destination-self.pos).normalize()*self.dt[0]*self.vitesse_base*5
        destination_selectionee=True
        if pygame.mouse.get_pressed(num_buttons=3)[0]:
            print("position set")
            self.destination=Vector2(pygame.mouse.get_pos())

    def draw(self):
        self.screen[0].blit(self.image, (self.pos.x, self.pos.y))
        print("fourmi dessinée")

class Partie():
    def __init__(self):
        self.temps = 0


    def process(self):
        self.temps += 1