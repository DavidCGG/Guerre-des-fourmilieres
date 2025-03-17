import pygame

class Colonie:
    def __init__(self, nom):
        self.nom = nom
        self.salles = [Salle(100, 600, "Throne"),Salle(900, 500, "Banque"), ]
        # objets.append(self)
    def process(self):
        for salle in self.salles:
            salle.process()

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

    def process(self):
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
    def __init__(self, pos, type, dt, equipe,dans_colonie):
        self.image = pygame.image.load('assets/fourmi_noire.png')
        self.pos = pos
        self.HP_max = 0
        self.poids_max = 0
        self.vitesse_base = 0
        self.dexterite = 0
        self.destination = None
        self.dt=dt
        self.equipe=equipe
        self.dans_colonie=equipe
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

    def process(self):
        if(self.destination!=None):
            if(self.pos==self.destination):
                self.destination=None
            else:
                self.pos=self.pos+(self.pos-self.destination).Normalize()*self.dt*self.vitesse_base



class Partie():
    def __init__(self):
        self.temps = 0


    def process(self):
        self.temps += 1