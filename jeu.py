import pygame

pygame.init()
screen = pygame.display.set_mode((1280,720))
clock = pygame.time.Clock()
running = True
dt=0
objets = []

player_pos = pygame.Vector2(screen.get_width()/2,screen.get_height()/2)

pygame.display.set_caption("Guerre des fourmilières")
#pygame.display.set_icon()

class Bouton():
    def __init__(self,x,y,largeur,hauteur,texte,police,fonction_sur_click=None):
        self.x=x
        self.y=y
        self.largeur = largeur
        self.hauteur = hauteur
        self.texte = texte
        self.police = police
        self.fonction_sur_click = fonction_sur_click
        self.couleurs = { 'normale': '#ffffff', 'survol': '#666666', 'clické': '#333333'}
        self.surface = pygame.Surface((self.largeur,self.hauteur))
        self.rectangle = pygame.Rect(self.x,self.y,self.largeur,self.hauteur)
        self.texte_render = police.render(self.texte,True,"black")
        self.deja_clicke = False
        objets.append(self)

    def process(self):
        position_souris = pygame.mouse.get_pos()
        self.surface.fill(self.couleurs['normale'])
        if self.rectangle.collidepoint(position_souris):
            #survol:
            self.surface.fill(self.couleurs['survol'])

            if pygame.mouse.get_pressed(num_buttons=3)[0]:
                #sur click tenu :

                if not self.deja_clicke:
                    self.fonction_sur_click()
                    self.deja_clicke=True
            else:
                self.deja_clicke=False

        self.surface.blit(self.texte_render,[self.rectangle.width/2-self.texte_render.get_rect().width/2,self.rectangle.height/2-self.texte_render.get_rect().height/2])
        screen.blit(self.surface,(self.x,self.y))

def menu_options():
    print('menu options')

def menu_principal():
    pygame.font.init()
    police_titre = pygame.font.SysFont("Comic Sans MS",50)
    surface_titre = police_titre.render("Guerre des fourmilières",True,"blue")
    screen.blit(surface_titre, (screen.get_width()/2-surface_titre.get_rect().width/2,screen.get_height()/3-surface_titre.get_rect().height/2))
    bouton1 = Bouton(100,200,300,50,'Bouton',police_titre,menu_options())



menu_principal()
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    #screen.fill(pygame.Color(100,50,0))

    #render game here
    pygame.draw.circle(screen, "red", player_pos, 40)

    keys = pygame.key.get_pressed()
    if keys[pygame.K_w]:
        player_pos.y -= 300 * dt

    if dt != 0:
        pygame.display.set_caption(str(1/dt))

    for object in objets:
        object.process()

    pygame.display.flip()

    dt = clock.tick() / 1000

pygame.quit()