import pygame

pygame.init()
screen = pygame.display.set_mode((1280,720))
clock = pygame.time.Clock()
running = True
dt=0
objets = []

police_titre = pygame.font.SysFont("Comic Sans MS",50)

player_pos = pygame.Vector2(screen.get_width()/2,screen.get_height()/2)

pygame.display.set_caption("Guerre des fourmilières")

image_icone=pygame.image.load('assets/fourmi_noire.png')
pygame.display.set_icon(image_icone)

class Bouton():
    def __init__(self,x,y,largeur,hauteur,texte,police,fonction_sur_click):
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
            self.PV_max=100
            self.attaque=25
            self.charge_max=100
        elif type=='moyen':
            self.PV_max=75
            self.attaque=75
            self.charge_max=75
        elif type=='leger':
            self.PV_max=75
            self.attaque=100
            self.charge_max=50
        """

class Partie():
    def __init__(self):
        self.temps=0
        objets.append(self)
    def process(self):
        self.temps+=1
        a = pygame.Surface((100, 100))
        a.fill('red')
        screen.blit(a, (screen.get_width()/2, 100))


def nouvelle_partie():
    objets.clear()
    partie = Partie()
    screen.fill('blue')
    pygame.display.update()
    print('Nouvelle parite')



def menu_options():
    print('menu options')
    objets.clear()
    pygame.display.update()
    screen.fill('green')

def menu_principal():
    surface_titre = police_titre.render("Guerre des fourmilières",True,"blue")
    screen.blit(surface_titre, (screen.get_width()/2-surface_titre.get_rect().width/2,screen.get_height()/10-surface_titre.get_rect().height/2))
    bouton_nouvelle_partie = Bouton(screen.get_width() / 2, screen.get_height() / 5, 300, 50, 'Nouvelle partie',police_titre, nouvelle_partie)
    bouton_options = Bouton(screen.get_width() / 2, screen.get_height() * 2 / 5, 300, 50, 'Options',police_titre, menu_options)



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