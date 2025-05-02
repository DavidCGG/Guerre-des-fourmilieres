import pygame
from pygame import Vector2, Color

class Colonie:
    def __init__(self, nom, dt_pointer, screen_pointer, liste_fourmis_pointeur, x, y, liste_items_pointeur):
        self.nom = nom
        self.dt = dt_pointer
        self.screen_pointer = screen_pointer
        self.liste_items_pointeur = liste_items_pointeur
        self.salles = [Salle(20, 500, "throne", screen_pointer, self, liste_fourmis_pointeur, dt_pointer, self.screen_pointer, self.liste_items_pointeur),
                       Salle(900, 500, "banque", screen_pointer, self, liste_fourmis_pointeur, dt_pointer, self.screen_pointer, self.liste_items_pointeur),
                       Salle(800, 300, "meule", screen_pointer, self, liste_fourmis_pointeur, dt_pointer, self.screen_pointer, self.liste_items_pointeur),
                       Salle(100, 250, "enclume", screen_pointer, self, liste_fourmis_pointeur, dt_pointer, self.screen_pointer, self.liste_items_pointeur)]
        self.fourmis=[]
        self.fourmis.append(Fourmi("moyen", dt_pointer, self, self.screen_pointer, liste_fourmis_pointeur, self.liste_items_pointeur))
        self.liste_fourmis_pointeur=liste_fourmis_pointeur
        self.pos=Vector2(x,y)
        self.surface = pygame.Surface((self.screen_pointer[0].get_width(), self.screen_pointer[0].get_height()))
        # objets.append(self)
    def process(self,liste_items):
        for salle in self.salles:
            salle.process(liste_items)
    def draw(self,liste_fourmis,liste_items):
        #print("Colonie "+self.nom+" dessinee")
        self.surface.fill("cyan")
        pygame.draw.rect(self.surface, 'green', pygame.Rect(0, 25, self.screen_pointer[0].get_width(), 25))
        pygame.draw.rect(self.surface, Color(205, 133, 63), pygame.Rect(0, 50, self.screen_pointer[0].get_width(), self.screen_pointer[0].get_height() - 50))
        self.screen_pointer[0].blit(self.surface, (0, 0))

        for salle in self.salles:
            salle.draw()

        for fourmi in liste_fourmis:
            if fourmi.dans_colonie is not None:
                if fourmi.dans_colonie.nom==self.nom:
                    fourmi.draw()
        for item in liste_items:
            #print(item.sorte+": "+item.id+" ",end="")
            if item.dans_colonie is not None:
                if item.sorte == "metal" and not item.dans_inventaire and item.dans_colonie.nom==self.nom:
                    item.draw()
                elif item.sorte != "metal" and item.dans_inventaire and item.dans_colonie.nom==self.nom:
                    item.draw()
        #print()

        """for item in self.liste_items:
            if item.dans_colonie is not None:
                if item.dans_colonie.nom==self.nom:
                    item.draw()"""

class Salle:
    def __init__(self, x, y, sorte, screen, colonie, liste_fourmis_pointeur, dt_pointer, screen_pointer, liste_items_pointeur):
        self.pos = Vector2(x,y)
        self.sorte = sorte
        self.screen=screen
        self.colonie=colonie
        self.liste_fourmis_pointeur=liste_fourmis_pointeur
        self.dt_pointer=dt_pointer
        self.screen_pointer=screen_pointer
        self.deja_depose=False
        self.detruit=False
        #self.liste_items_pointeur=liste_items_pointeur
        # self.rectanlge = pygame.Rect()
        if (self.sorte == "throne"):
            self.reine_PV = 200
            self.largeur = 128
            self.hauteur = 128
            self.image = pygame.image.load('../assets/images/throne_fourmi_'+self.colonie.nom+'.png')
        elif (self.sorte == "banque"):
            self.ressources_max = 10
            self.ressources = 0
            self.largeur = 256
            self.hauteur = 128
            self.image = pygame.image.load('../assets/images/' + self.sorte + '.png')
            self.reserve=[]
        elif (self.sorte == "meule"):
            self.ressources = 0
            self.largeur = 128
            self.hauteur = 128
            self.image = pygame.image.load('../assets/images/' + self.sorte + '.png')
        elif (self.sorte == "enclume"):
            self.ressources = 0
            self.largeur = 128
            self.hauteur = 128
            self.image = pygame.image.load('../assets/images/' + self.sorte + '.png')
        # objets.append(self)

    def process(self,liste_items):
        if (self.sorte == "throne"):
            for fourmi in self.liste_fourmis_pointeur[0]:
                if fourmi.dans_colonie is not None:
                    if fourmi.dans_colonie.nom==self.colonie.nom and fourmi.colonie_origine.nom!=self.colonie.nom and self.pos.x < fourmi.pos.x < self.pos.x+self.largeur and self.pos.y < fourmi.pos.y < self.pos.y+self.hauteur:
                        self.reine_PV-= fourmi.attaque * self.dt_pointer[0]
            if(self.reine_PV<=0):
                self.reine_PV=0
                self.detruit=True

        elif (self.sorte == "banque"):
            for fourmi in self.liste_fourmis_pointeur[0]:
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
                                    self.reserve.append(item)
                            self.ressources+=nb_metal
                            fourmi.inventaire = nouveau_inventaire
                            if nb_metal!=0:
                                self.deja_depose = True
                                print(str(nb_metal)+" métal déposé")
                            if nb_metal==0 and self.ressources>0 and not self.deja_depose:
                                nouveau_inventaire.append(self.reserve[len(self.reserve)-1])
                                self.reserve.pop()
                                self.ressources-=1
                                self.deja_depose=True
                                print("1 metal retiré")
                    elif fourmi.dans_colonie.nom == self.colonie.nom:
                            self.deja_depose=False
        elif (self.sorte == "meule"):
            for fourmi in self.liste_fourmis_pointeur[0]:
                if fourmi.dans_colonie is not None:
                    if fourmi.dans_colonie.nom == self.colonie.nom and fourmi.colonie_origine.nom == self.colonie.nom and self.pos.x < fourmi.pos.x < self.pos.x + self.largeur and self.pos.y < fourmi.pos.y < self.pos.y + self.hauteur:
                        index_metal_dans_inventaire=None
                        metal=None
                        deja_epee=False
                        for item in fourmi.inventaire:
                            if item.sorte=="epee":
                                deja_epee=True
                                break
                            elif item.sorte=="metal":
                                index_metal_dans_inventaire=fourmi.inventaire.index(item)
                                metal=item
                        if metal is not None and not deja_epee:
                            fourmi.inventaire[index_metal_dans_inventaire] = Item(fourmi.pos.x, fourmi.pos.y, self.colonie, "epee", self.screen_pointer,True)
                            for item in liste_items:
                                if item.id==metal.id:
                                    liste_items[liste_items.index(item)] = fourmi.inventaire[index_metal_dans_inventaire]

        elif (self.sorte == "enclume"):
            for fourmi in self.liste_fourmis_pointeur[0]:
                if fourmi.dans_colonie is not None:
                    if fourmi.dans_colonie.nom == self.colonie.nom and fourmi.colonie_origine.nom == self.colonie.nom and self.pos.x < fourmi.pos.x < self.pos.x + self.largeur and self.pos.y < fourmi.pos.y < self.pos.y + self.hauteur:
                        index_metal_dans_inventaire = None
                        metal = None
                        deja_epee = False
                        for item in fourmi.inventaire:
                            if item.sorte == "armure":
                                deja_epee = True
                                break
                            elif item.sorte == "metal":
                                index_metal_dans_inventaire = fourmi.inventaire.index(item)
                                metal = item
                        if metal is not None and not deja_epee:
                            fourmi.inventaire[index_metal_dans_inventaire] = Item(fourmi.pos.x, fourmi.pos.y, self.colonie, "armure",self.screen_pointer, True)
                            for item in liste_items:
                                if item.id == metal.id:
                                    liste_items[liste_items.index(item)] = fourmi.inventaire[index_metal_dans_inventaire]
            #print(self.deja_depose)

    def draw(self):
        #surface_self=pygame.Surface((self.largeur,self.hauteur))
        #surface_self.fill(Color(205, 133, 63))
        #pygame.draw.ellipse(surface_self, Color(139, 69, 19),pygame.Rect(0, 0, self.largeur, self.hauteur))
        police = pygame.font.Font("../assets/fonts/Minecraft.ttf", 25)
        surface_texte=pygame.surface.Surface((self.largeur+64,64))
        surface_texte.fill(Color(205, 133, 63))
        texte_render=None
        if self.sorte == "throne":
            if self.detruit:
                self.image=pygame.image.load('../assets/images/Salles/salle_vide.png')
            texte_render = police.render("Reine : " + str(self.reine_PV) + " PV", False, "Black")
        elif self.sorte == "banque":
            texte_render = police.render("Banque : " + str(self.ressources) + " ressources", False, "Black")
        #else:
            #raise Exception("Sorte salle invalide")
        if texte_render is not None:
            surface_texte.blit(texte_render, (0, 0))
        self.screen[0].blit(self.image, (self.pos.x, self.pos.y))
        self.screen[0].blit(surface_texte, (self.pos.x, self.pos.y+self.hauteur))

class Fourmi():
    def __init__(self, type, dt_pointer, colonie_origine, screen, liste_fourmis_pointeur, liste_items_pointeur):
        self.pos = Vector2(colonie_origine.salles[0].pos.x+colonie_origine.salles[0].largeur*2,colonie_origine.salles[0].pos.y)
        self.PV_max = 0
        self.poids_max = 0
        self.vitesse_base = 0
        self.dexterite = 0
        self.destination = None
        self.dt=dt_pointer
        self.colonie_origine=colonie_origine
        self.dans_colonie=colonie_origine
        self.screen=screen
        self.type=type
        self.liste_items_pointeur=liste_items_pointeur
        self.inventaire=[]
        self.image = pygame.image.load('../assets/images/fourmi_' + self.colonie_origine.nom + '.png')
        liste_fourmis_pointeur[0].append(self)
        self.liste_fourmis_pointeur=liste_fourmis_pointeur
        self.vivant=True
        if self.type=='lourd':
            self.PV_max=100
            self.poids_max=100
            self.vitesse_base=25
            self.dexterite=25
        elif self.type=='moyen':
            self.PV_max=75
            self.poids_max=50
            self.vitesse_base=50
            self.dexterite=50
        elif self.type=='leger':
            self.PV_max=50
            self.poids_max=25
            self.vitesse_base=100
            self.dexterite=100
        else:
            raise Exception("Type fourmi invalide")
        self.attaque=self.dexterite
        self.vitesse=self.vitesse_base
        self.PV=self.PV_max
        self.defense=0
        self.charge_disponible = self.poids_max

        self.string = "Fourmi " + self.colonie_origine.nom +" Attaque:" + str(self.attaque) +" Vitesse:" + str(self.vitesse) +" PV:" + str(self.PV) +" Defense:" + str(self.defense) +" Charge disponible:" + str(self.charge_disponible)
        #self.string += "\nInventaire: "
        #for item in self.inventaire:
            #self.string+=item.sorte+" id: "+item.id+", "
        print(self.string)
    def process(self):
        #print("dest:"+str(self.destination)+" pos:"+str(self.pos)+" ",end='')
        if self.vivant:
            if(self.destination!=None):
                if (self.pos-self.destination).magnitude() < 10:
                    #print("destination atteinte",end='')
                    self.destination=None
                else:
                    #print("fourmi en movement: "+str((self.destination-self.pos).normalize()*self.dt[0]*self.vitesse_base*5),end='')
                    #print("dt: "+str(self.dt[0]))
                    self.pos+=(self.destination-self.pos).normalize()*self.dt[0]*self.vitesse*10
            destination_selectionee=True
            #print()
            if(self.pos.y<25 and self.dans_colonie is not None):
                print("fourmi sortie")
                for item in self.inventaire:
                    item.dans_colonie=None
                self.destination=None
                self.pos=self.dans_colonie.pos+((Vector2(self.screen[0].get_width()/2,self.screen[0].get_height()/2)-self.dans_colonie.pos).normalize()*20)
                self.dans_colonie=None
            for item in self.liste_items_pointeur[0]:
                    if item.dans_colonie is not None and self.dans_colonie is not None:
                        if not item.dans_inventaire and item.dans_colonie.nom==self.dans_colonie.nom and (item.pos-self.pos).magnitude()<20 and self.charge_disponible>=item.poids:
                            print(item.sorte+" rammassé")
                            item.dans_inventaire=True
                            self.inventaire.append(item)
                    elif not item.dans_inventaire and item.dans_colonie is None and self.dans_colonie is None and (item.pos-self.pos).magnitude()<20 and self.charge_disponible>=item.poids:
                        print(item.sorte + " rammassé")
                        item.dans_inventaire = True
                        self.inventaire.append(item)

            charge=0
            attaque_multiplicateur=1
            defense_totale=0
            for item in self.inventaire:
                charge+=item.poids
                attaque_multiplicateur+=item.attaque_multiplicateur_bonus
                defense_totale+=item.defense
                item.pos=self.pos
            #print()
            self.attaque = self.dexterite * attaque_multiplicateur
            self.defense = defense_totale
            self.vitesse = self.vitesse_base-charge/2
            self.PV += 10 * self.dt[0]
            if self.PV > self.PV_max:
                self.PV = self.PV_max
            self.charge_disponible = self.poids_max - charge

            nouveau_string = "Fourmi " + self.colonie_origine.nom +" Attaque:" + str(self.attaque) +" Vitesse:" + str(self.vitesse) +" PV:" + str(self.PV) +" Defense:" + str(self.defense) +" Charge disponible:" + str(self.charge_disponible)
            #print(nouveau_string)
            #nouveau_string += "\nInventaire: "
            #for item in self.inventaire:
                #self.string += item.sorte + " id: " + item.id + ", "
            if self.string != nouveau_string:
                self.string=nouveau_string
                print(self.string)

            for fourmi in self.liste_fourmis_pointeur[0]:
                if fourmi.vivant:
                    if fourmi.dans_colonie is not None and self.dans_colonie is not None:
                        if fourmi.dans_colonie.nom == self.dans_colonie.nom and fourmi.colonie_origine.nom != self.colonie_origine.nom and (fourmi.pos-self.pos).magnitude()<20 :
                            self.PV-=(fourmi.attaque-self.defense)*self.dt[0]*10
                            print(str(self.colonie_origine.nom)+str(self.PV))
                            if self.PV<0:
                                self.PV=0
                                self.vivant=False
                    elif fourmi.dans_colonie is None and self.dans_colonie is None:
                        if fourmi.colonie_origine.nom != self.colonie_origine.nom and (fourmi.pos-self.pos).magnitude()<20:
                            self.PV -= fourmi.attaque
                            if self.PV < 0:
                                self.PV = 0
                                self.vivant = False

    def colonie_input_process(self,colonie_joueur):
        #print("colonie input processed")
        if pygame.mouse.get_pressed(num_buttons=3)[0] and self.colonie_origine.nom==colonie_joueur.nom:
            #print("position set")
            self.destination=Vector2(pygame.mouse.get_pos())

    def carte_input_process(self,colonie_joueur) :
        #print("carte input processed")
        if pygame.mouse.get_pressed(num_buttons=3)[0] and self.colonie_origine.nom==colonie_joueur.nom:
            #print("position set")
            self.destination = Vector2(pygame.mouse.get_pos())

    def draw(self):
        if not self.vivant:
            self.image=pygame.image.load('../assets/images/Fourmis/fourmi_morte.png')
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
    def __init__(self, screen, colonies, liste_fourmis_pointeur, liste_items_pointeur):
        self.screen=screen
        self.colonies=colonies
        self.liste_fourmis_pointeur=liste_fourmis_pointeur
        self.liste_items_pointeur=liste_items_pointeur
    #def process(self):
    def process(self):
        #print(len(self.fourmis))
        for colonie in self.colonies:
            for fourmi in self.liste_fourmis_pointeur[0]:
                if fourmi.dans_colonie is None and (fourmi.pos-colonie.pos).magnitude() < 20:
                    print("fourmi entrée dans colonie "+colonie.nom)
                    fourmi.dans_colonie=colonie
                    fourmi.pos=Vector2(self.screen[0].get_width()/2,26)
                    fourmi.destination=None
                    for item in fourmi.inventaire:
                        item.dans_colonie=colonie

    def draw(self,liste_fourmis,liste_itmes):
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
        for fourmi in self.liste_fourmis_pointeur[0]:
            if fourmi.dans_colonie is None:
                fourmi.draw()
        #print("item start carte draw")
        for item in self.liste_items_pointeur[0]:
            #print(item.sorte)
            if item.dans_colonie is None :
                if item.sorte=="metal" and not item.dans_inventaire:
                    item.draw()
                elif item.sorte!="metal" and item.dans_inventaire:
                    item.draw()

class Item:
    conteur_classe=0
    def __init__(self,x,y,dans_colonie,sorte,screen,dans_inventaire):
        self.pos=Vector2(x,y)
        self.dans_colonie=dans_colonie
        self.sorte=sorte
        self.image = pygame.image.load('../assets/images/' + self.sorte + '.png')
        self.dans_inventaire=dans_inventaire
        self.screen=screen
        self.id = str(Item.conteur_classe)
        if self.sorte == "epee":
            self.poids = 10
            self.attaque_multiplicateur_bonus=0.25
            self.defense=1
        elif self.sorte == "armure":
            self.poids = 15
            self.attaque_multiplicateur_bonus = 0
            self.defense=5
        elif self.sorte == "metal":
            self.poids = 25
            self.attaque_multiplicateur_bonus = 0
            self.defense=0
        Item.conteur_classe+=1
    def draw(self):
        #print("item " +self.sorte+self.id+" drawn")
        self.screen[0].blit(self.image, (self.pos.x, self.pos.y))