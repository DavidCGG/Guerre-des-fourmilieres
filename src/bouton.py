import pygame

class Bouton:
    def __init__(self,x,y,largeur,hauteur,texte,fonction_sur_click, police, screen):
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

        self.screen = screen
        self.screen = screen

        self.avec_bordure = False
        self.couleur_bordure = None

    def process(self):

        position_souris = pygame.mouse.get_pos()
        souris_clique = pygame.mouse.get_pressed(num_buttons=3)

        self.surface.fill(self.couleurs['normale'])
        if self.rectangle.collidepoint(position_souris):
            #survol:
            self.surface.fill(self.couleurs['survol'])

            if souris_clique[0]:
                #sur click tenu :
                self.surface.fill(self.couleurs['clické'])
                if not self.deja_clicke:
                    self.fonction_sur_click()
                    self.deja_clicke=True
            else:
                self.deja_clicke=False
        if self in self.objets:
            self.texte_render = self.police.render(self.texte,True,"black")

            self.surface.blit(self.texte_render,[self.rectangle.width/2-self.texte_render.get_rect().width/2,self.rectangle.height/2-self.texte_render.get_rect().height/2])
            self.screen.blit(self.surface,self.rectangle)
            if self.avec_bordure:
                pygame.draw.rect(self.screen,self.couleur_bordure,self.rectangle,3)

    def add_bordure(self, col):
        self.avec_bordure = True
        self.couleur_bordure = col