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

    def process(self):
        position_souris = pygame.mouse.get_pos()
        self.surface.fill(self.couleurs['normale'])
        if self.rectangle.collidepoint(position_souris):
            #survol:
            self.surface.fill(self.couleurs['survol'])

            if pygame.mouse.get_pressed(num_buttons=3)[0]:
                #sur click tenu :
                self.surface.fill(self.couleurs['clické'])
                self.fonction_sur_click()
                self.deja_clicke=True

        self.surface.blit(self.texte_render,[self.rectangle.width/2-self.texte_render.get_rect().width/2,self.rectangle.height/2-self.texte_render.get_rect().height/2])
        pygame.draw.rect(self.surface, pygame.Color("black"), self.surface.get_rect(), 3)
        self.screen.blit(self.surface,self.rectangle)