import pygame
from pygame import Vector2, Color


class Colonie:
    def __init__(self, nom, dt_pointer, screen_pointer, liste_fourmis, x, y, liste_items):
        self.nom = nom
        self.dt = dt_pointer
        self.screen_pointer = screen_pointer
        self.liste_items = liste_items
        self.salles = [Salle(20, 500, "throne", screen_pointer, self, liste_fourmis, dt_pointer, self.screen_pointer),
                       Salle(900, 500, "banque", screen_pointer, self, liste_fourmis, dt_pointer,self.screen_pointer),
                       Salle(800, 300, "meule", screen_pointer, self, liste_fourmis, dt_pointer,self.screen_pointer),
                       Salle(100, 250, "enclume", screen_pointer, self, liste_fourmis, dt_pointer,self.screen_pointer)]
        self.fourmis=[]
        if self.nom=="noire":
            self.fourmis.append(Fourmi("moyen", dt_pointer, self, self.screen_pointer, liste_fourmis, self.liste_items))
        self.liste_fourmis=liste_fourmis
        self.pos=Vector2(x,y)
        # objets.append(self)
    def process(self):
        for salle in self.salles:
            salle.process()
    def draw(self):
        #print("Colonie "+self.nom+" dessinee")

        surface_colonie = pygame.Surface((self.screen_pointer[0].get_width(), self.screen_pointer[0].get_height()))
        surface_colonie.fill("cyan")
        pygame.draw.rect(surface_colonie, 'green', pygame.Rect(0, 25, self.screen_pointer[0].get_width(), 25))
        pygame.draw.rect(surface_colonie, Color(205, 133, 63), pygame.Rect(0, 50, self.screen_pointer[0].get_width(), self.screen_pointer[0].get_height() - 50))
        self.screen_pointer[0].blit(surface_colonie, (0, 0))

        for salle in self.salles:
            salle.draw()

        for fourmi in self.liste_fourmis:
            if fourmi.dans_colonie is not None:
                if fourmi.dans_colonie.nom==self.nom:
                    fourmi.draw()
        for item in self.liste_items:
            if item.dans_colonie is not None and not item.dans_inventaire:
                if item.dans_colonie.nom==self.nom:
                    item.draw()

        """for item in self.liste_items:
            if item.dans_colonie is not None:
                if item.dans_colonie.nom==self.nom:
                    item.draw()"""

class Salle:
    def __init__(self, x, y, sorte,screen,colonie,liste_fourmis,dt_pointer,screen_pointer):
        self.pos = Vector2(x,y)
        self.sorte = sorte
        self.screen=screen
        self.colonie=colonie
        self.liste_fourmis=liste_fourmis
        self.dt_pointer=dt_pointer
        self.screen_pointer=screen_pointer
        self.deja_depose=False
        # self.rectanlge = pygame.Rect()
        if (self.sorte == "throne"):
            self.reine_hp = 1000
            self.largeur = 128
            self.hauteur = 128
            self.image = pygame.image.load('assets/throne_fourmi_'+self.colonie.nom+'.png')
        elif (self.sorte == "banque"):
            self.ressources_max = 1000
            self.ressources = 0
            self.largeur = 256
            self.hauteur = 128
            self.image = pygame.image.load('assets/' + self.sorte + '.png')
        elif (self.sorte == "meule"):
            self.ressources = 0
            self.largeur = 128
            self.hauteur = 128
            self.image = pygame.image.load('assets/' + self.sorte + '.png')
        elif (self.sorte == "enclume"):
            self.ressources = 0
            self.largeur = 128
            self.hauteur = 128
            self.image = pygame.image.load('assets/' + self.sorte + '.png')
        # objets.append(self)

    def process(self):
        if (self.sorte == "throne"):
            for fourmi in self.liste_fourmis:
                if fourmi.dans_colonie is not None:
                    if fourmi.dans_colonie.nom==self.colonie.nom and fourmi.colonie_origine.nom!=self.colonie.nom and self.pos.x < fourmi.pos.x < self.pos.x+self.largeur and self.pos.y < fourmi.pos.y < self.pos.y+self.hauteur:
                        self.reine_hp-=fourmi.attaque*self.dt_pointer[0]
        elif (self.sorte == "banque"):
            for fourmi in self.liste_fourmis:
                if fourmi.dans_colonie is not None:
                    if fourmi.dans_colonie.nom == self.colonie.nom and fourmi.colonie_origine.nom == self.colonie.nom and self.pos.x < fourmi.pos.x < self.pos.x + self.largeur and self.pos.y < fourmi.pos.y < self.pos.y + self.hauteur:
                        if not self.deja_depose:
                            nouveau_inventaire=[]
                            nb_metal=0
                            for item in fourmi.inventaire:
                                if item.sorte!="metal":
                                    nouveau_inventaire.append(item)
                                else:
                                    nb_metal+=1
                            self.ressources+=nb_metal
                            fourmi.inventaire = nouveau_inventaire
                            if nb_metal!=0:
                                self.deja_depose = True
                                print(str(nb_metal)+" métal déposé")
                            if nb_metal==0 and self.ressources>0 and not self.deja_depose:
                                nouveau_inventaire.append(Item(fourmi.pos.x,fourmi.pos.y,None,"metal",self.screen_pointer))
                                self.ressources-=1
                                self.deja_depose=True
                                print("1 metal retiré")
                    elif fourmi.dans_colonie.nom == self.colonie.nom:
                            self.deja_depose=False
        elif (self.sorte == "meule"):
            for fourmi in self.liste_fourmis:
                if fourmi.dans_colonie is not None:
                    if fourmi.dans_colonie.nom == self.colonie.nom and fourmi.colonie_origine.nom == self.colonie.nom and self.pos.x < fourmi.pos.x < self.pos.x + self.largeur and self.pos.y < fourmi.pos.y < self.pos.y + self.hauteur:
                        print("krrrrrrrr")
        elif (self.sorte == "enclume"):
            for fourmi in self.liste_fourmis:
                if fourmi.dans_colonie is not None:
                    if fourmi.dans_colonie.nom == self.colonie.nom and fourmi.colonie_origine.nom == self.colonie.nom and self.pos.x < fourmi.pos.x < self.pos.x + self.largeur and self.pos.y < fourmi.pos.y < self.pos.y + self.hauteur:
                        print("clink")
            #print(self.deja_depose)

    def draw(self):
        #surface_self=pygame.Surface((self.largeur,self.hauteur))
        #surface_self.fill(Color(205, 133, 63))
        #pygame.draw.ellipse(surface_self, Color(139, 69, 19),pygame.Rect(0, 0, self.largeur, self.hauteur))
        police = pygame.font.Font("assets/Minecraft.ttf", 25)
        surface_texte=pygame.surface.Surface((self.largeur+64,64))
        surface_texte.fill(Color(205, 133, 63))
        texte_render=None
        if self.sorte == "throne":
            texte_render = police.render("Reine : " + str(self.reine_hp) + " hp", False, "Black")
        elif self.sorte == "banque":
            texte_render = police.render("Banque : " + str(self.ressources) + " ressources", False, "Black")
        #else:
            #raise Exception("Sorte salle invalide")
        if texte_render is not None:
            surface_texte.blit(texte_render, (0, 0))
        self.screen[0].blit(self.image, (self.pos.x, self.pos.y))
        self.screen[0].blit(surface_texte, (self.pos.x, self.pos.y+self.hauteur))


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
        self.texte_render = police.render(self.texte, False, "black")
        self.deja_clicke = True

    def draw(self):
        position_souris = pygame.mouse.get_pos()
        self.surface_self.fill(self.couleurs['normale'])
        cursor_sur_bouton=False
        if self.rectangle.collidepoint(position_souris):
            # survol:
            self.surface_self.fill(self.couleurs['survol'])
            cursor_sur_bouton=True
            if pygame.mouse.get_pressed(num_buttons=3)[0]:
                # sur click tenu :
                self.surface_self.fill(self.couleurs['clické'])
                if not self.deja_clicke:
                    self.fonction_sur_click()
                self.deja_clicke = True
            else:
                self.deja_clicke = False

        self.surface_self.blit(self.texte_render, [self.rectangle.width / 2 - self.texte_render.get_rect().width / 2,self.rectangle.height / 2 - self.texte_render.get_rect().height / 2])
        pygame.draw.rect(self.surface_self, pygame.Color("black"), self.surface_self.get_rect(), 3)
        self.screen.blit(self.surface_self, (self.x, self.y))
        return cursor_sur_bouton


class Fourmi():
    def __init__(self, type, dt_pointer, colonie_origine, screen, liste_fourmis,liste_items):
        self.pos = Vector2(colonie_origine.salles[0].pos.x,colonie_origine.salles[0].pos.y)
        self.HP_max = 0
        self.poids_max = 0
        self.vitesse_base = 0
        self.dexterite = 0
        self.destination = None
        self.dt=dt_pointer
        self.colonie_origine=colonie_origine
        self.dans_colonie=colonie_origine
        self.screen=screen
        self.type=type
        self.liste_items=liste_items
        self.inventaire=[]
        self.image = pygame.image.load('assets/fourmi_' + self.colonie_origine.nom + '.png')
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
        self.attaque=self.dexterite

    def process(self):
        #print("dest:"+str(self.destination)+" pos:"+str(self.pos)+" ",end='')

        if(self.destination!=None):
            if (self.pos-self.destination).magnitude() < 10:
                #print("destination atteinte",end='')
                self.destination=None
            else:
                #print("fourmi en movement: "+str((self.destination-self.pos).normalize()*self.dt[0]*self.vitesse_base*5),end='')
                #print("dt: "+str(self.dt[0]))
                self.pos+=(self.destination-self.pos).normalize()*self.dt[0]*self.vitesse_base*10
        destination_selectionee=True
        #print()
        if(self.pos.y<25 and self.dans_colonie is not None):
            print("fourmi sortie")
            for item in self.inventaire:
                item.dans_colonie=None
            self.destination=None
            self.pos=self.dans_colonie.pos+((Vector2(self.screen[0].get_width()/2,self.screen[0].get_height()/2)-self.dans_colonie.pos).normalize()*15)
            self.dans_colonie=None
        for item in self.liste_items:
                if item.dans_colonie is not None and self.dans_colonie is not None:
                    if not item.dans_inventaire and item.dans_colonie.nom==self.dans_colonie.nom and (item.pos-self.pos).magnitude()<10:
                        print(item.sorte+" rammassé")
                        item.dans_inventaire=True
                        self.inventaire.append(item)
                elif not item.dans_inventaire and item.dans_colonie is None and self.dans_colonie is None and (item.pos-self.pos).magnitude()<10:
                    print(item.sorte + " rammassé")
                    item.dans_inventaire = True
                    self.inventaire.append(item)
        for item in self.inventaire:
            item.pos=self.pos
        #print()

    def colonie_input_process(self):
        #print("colonie input processed")
        if pygame.mouse.get_pressed(num_buttons=3)[0]:
            #print("position set")
            self.destination=Vector2(pygame.mouse.get_pos())

    def carte_input_process(self):
        #print("carte input processed")
        if pygame.mouse.get_pressed(num_buttons=3)[0]:
            #print("position set")
            self.destination = Vector2(pygame.mouse.get_pos())

    def draw(self):
        self.screen[0].blit(self.image, (self.pos.x, self.pos.y))
        #for item in self.inventaire:
            #item.draw()
            #print(item.sorte,end="")
        #print()
        #print("fourmi dessinée")

class Partie():
    def __init__(self):
        self.tick = 0


    def process(self):
        self.tick += 1

class Carte:
    def __init__(self, screen, colonies, liste_fourmis,liste_items):
        self.screen=screen
        self.colonies=colonies
        self.liste_fourmis=liste_fourmis
        self.liste_items=liste_items
    #def process(self):
    def process(self):
        #print(len(self.fourmis))
        for colonie in self.colonies:
            for fourmi in self.liste_fourmis:
                if fourmi.dans_colonie is None and (fourmi.pos-colonie.pos).magnitude() < 10:
                    print("fourmi entrée dans colonie "+colonie.nom)
                    fourmi.dans_colonie=colonie
                    fourmi.pos=Vector2(self.screen[0].get_width()/2,26)
                    fourmi.destination=None
                    for item in fourmi.inventaire:
                        item.dans_colonie=colonie

    def draw(self):
        #print("carte dessinee")

        surface_carte = pygame.Surface((self.screen[0].get_width(), self.screen[0].get_height()))
        surface_carte.fill("green")
        #pygame.draw.rect(surface_colonie, 'green', pygame.Rect(0, 25, self.screen[0].get_width(), 25))
        #pygame.draw.rect(surface_colonie, Color(205, 133, 63),pygame.Rect(0, 50, self.screen[0].get_width(), self.screen[0].get_height() - 50))
        #for salle in self.salles:
        #    pygame.draw.ellipse(surface_colonie, Color(139, 69, 19),pygame.Rect(salle.x, salle.y, salle.largeur, salle.hauteur))
        for colonie in self.colonies:
            pygame.draw.ellipse(surface_carte, Color(139, 69, 19),pygame.Rect(colonie.pos.x, colonie.pos.y, 20, 20))
        self.screen[0].blit(surface_carte, (0, 0))
        for fourmi in self.liste_fourmis:
            if fourmi.dans_colonie is None:
                fourmi.draw()
        #print("item start carte draw")
        for item in self.liste_items:
            #print(item.sorte)
            if item.dans_colonie is None and not item.dans_inventaire:
                item.draw()

class Item:
    def __init__(self,x,y,dans_colonie,sorte,screen):
        self.pos=Vector2(x,y)
        self.dans_colonie=dans_colonie
        self.sorte=sorte
        self.image = pygame.image.load('assets/' + self.sorte + '.png')
        self.dans_inventaire=False
        self.screen=screen
    def draw(self):
        #print("item drawn")
        self.screen[0].blit(self.image, (self.pos.x, self.pos.y))