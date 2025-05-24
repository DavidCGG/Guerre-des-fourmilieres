import random
import pygame
from config import trouver_font, trouver_img
from config import BLACK, WHITE, AQUA, GREEN, RED
from config import CouleurFourmi
from fourmi_types import Ouvriere, Soldat
from fourmi import FourmisSprite, Groupe, Fourmis
from classes_graphe import TypeSalle

class Colonie:
    def __init__(self, tuile_debut, map_data, tuiles_debut_toutes_colonies,graphe,listes_fourmis_jeu_complet):
        self.sprite_sheet_ouvr = pygame.image.load(trouver_img("Fourmis/sprite_sheet_fourmi_noire.png")).convert_alpha()
        self.sprite_sheet_sold = pygame.image.load(trouver_img("Fourmis/sprite_sheet_fourmi_noire.png")).convert_alpha()
        self.map_data = map_data
        self.tuile_debut = tuile_debut
        self.screen = None
        self.vie = 1 # 1 = 100% (vie de la reine)

        self.graphe = graphe

        self.hp = 1000
        self.max_hp = 1000
        for salle in self.graphe.salles:
            if salle.type == TypeSalle.SORTIE:
                self.sortie = salle
            elif salle.type == TypeSalle.THRONE:
                self.throne = salle

        self.fourmis_selection = None # fourmi selectionnée dans le menu de fourmis
        self.groupe_selection = None

        self.fourmis = [Ouvriere(self.throne.noeud.coord[0], self.throne.noeud.coord[1], CouleurFourmi.NOIRE, self, self.throne) for _ in range(1)] + [Soldat(self.throne.noeud.coord[0], self.throne.noeud.coord[1], CouleurFourmi.NOIRE, self, self.throne) for _ in range(1)]
        
        for fourmi in self.fourmis:
            listes_fourmis_jeu_complet.append(fourmi)
        self.groupes = {}
        #self.fourmis_presentes = self.fourmis
        #self.groupes_presents = self.groupes
        self.texte_rects = {} # les rects dans le menu colonie pour changer leur coloeur trop cool
        self.couleur_texte = WHITE
        self.hover_texte = None # soit Ouvrieres ou Soldats dans menu colonie

        self.menu_colonie_ouvert = False
        self.menu_fourmis_ouvert = False
        self.scrolling = False # si on scroll dans le menu fourmis, pour eviter de zoomer la carte
        self.scroll_offset = 0
        self.scroll_speed = 10
        self.curr_tab = "Ouvrières"
        self.font_menu = pygame.font.Font(trouver_font("LowresPixel-Regular.otf"), 20)
        self.last_tab = self.curr_tab

        self.boutons = [] # pas en utilisation en ce moment

        self.menu_colonie_surface = pygame.Surface((250, 375))
        self.menu_fourmis_surface = pygame.Surface((250, 375))
        self.menu_a_updater = True # si le menu colonie a besoin d'etre mis a jour
        self.menu_f_a_updater = True # si le menu fourmis a besoin d'etre mis a jour
        self.menu_fourmis_rect = pygame.Rect(0, 720 / 2 - self.menu_fourmis_surface.get_height() / 2, 250, 375)
        self.menu_colonie_rect = pygame.Rect(1280 - self.menu_colonie_surface.get_width(), 720 / 2 - self.menu_colonie_surface.get_height() / 2, 250, 375)
        self.update_menu()
        self.update_menu_fourmis()

        self.sprite_sheets = {
            Ouvriere: self.sprite_sheet_ouvr,
            Soldat: self.sprite_sheet_sold
        }
        self.sprite_dict = {}
        self.sprites = []
        self.load_sprites()

        self.groupe_images = []
        self.load_groupe_images()
        self.cache_groupes_a_updater = False
        self.groupes_cache = {}

        self.tuiles_debut = tuiles_debut_toutes_colonies
        self.stop_processing_salles_other_than_sortie_when_dead = False

    def process(self,dt,tous_les_nids,liste_fourmis_jeu_complet,liste_toutes_colonies,map_data):
        # groupe_bouge = False
        # for _, groupe in self.groupes_cache.items():
        #     if groupe.get_nb_fourmis() > 1 and not groupe.est_vide():
        #         dern_x, dern_y = groupe.centre_x_in_map, groupe.centre_y_in_map
        #         groupe.process(dt)
        #         if (dern_x, dern_y) != (groupe.centre_x_in_map, groupe.centre_y_in_map):
        #             groupe_bouge = True

        fourmis_bouge = False
        for f in self.fourmis:
            f.process(dt, self.map_data,tous_les_nids,liste_fourmis_jeu_complet,liste_toutes_colonies)

        for salle in self.graphe.salles:
            if salle.type != TypeSalle.SORTIE and not self.stop_processing_salles_other_than_sortie_when_dead:
                salle.process(liste_fourmis_jeu_complet, self, dt, map_data, liste_toutes_colonies)
            else:
                salle.process(liste_fourmis_jeu_complet, self, dt, map_data, liste_toutes_colonies)

        if fourmis_bouge: # or groupe_bouge
            self.cache_groupes_a_updater = True
        if self.menu_fourmis_ouvert:
            self.menu_f_a_updater = True
        if self.menu_colonie_ouvert:
            self.menu_a_updater = True

    def check_mort(self):
        return len(self.fourmis) == 0

    def nombre_ouvrieres(self):
        return len([f for f in self.fourmis if isinstance(f, Ouvriere)])

    def nombre_soldats(self):
        return len([f for f in self.fourmis if isinstance(f, Soldat)])

    def update_fourmi_tuile(self, fourmi, dern_x, dern_y):
        if fourmi in self.map_data[int(dern_y)][int(dern_x)].fourmis and self.map_data[int(dern_y)][int(dern_x)].fourmis is not None:
            self.map_data[int(dern_y)][int(dern_x)].fourmis.remove(fourmi)
        else:
            self.map_data[fourmi.get_tuile()[1]][fourmi.get_tuile()[0]].fourmis.append(fourmi)

    def collecte_fourmi(self, f):
        x, y = f.get_tuile()
        if self.map_data[y][x].tuile_ressource and not self.map_data[y][x].collectee and (x, y) == (f.target_in_map[0], f.target_in_map[1]):
            ress = self.map_data[y][x].get_ressource()
            if isinstance(f, Fourmis) and len(f.inventaire) < f.inventaire_taille_max:
                f.inventaire.append(ress)
                self.map_data[y][x].collectee = True

    def update_menu(self):
        if not self.menu_a_updater or not self.menu_colonie_ouvert:
            return
        self.menu_colonie_surface.fill(BLACK)

        y_offset = 40
        nb_metal=0
        nb_nourriture=0
        for salle in self.graphe.salles:
            for item in salle.inventaire:
                if item is None:
                    pass
                elif item.name=="POMME":
                    nb_nourriture+=1
                elif item.name=="METAL":
                    nb_metal+=1

        info_ouvr = f"Ouvrières ({self.nombre_ouvrieres()})"
        info_sold = f"Soldats ({self.nombre_soldats()})"
        info_groupes = f"Groupes ({self.get_vrai_nb_groupes()})"
        info_vie = "Vie: "+str(self.hp)
        info_nourr = "Nourriture: "+str(nb_nourriture)
        info_metal = "Métal: "+str(nb_metal)

        menu_x = 1280 - self.menu_colonie_surface.get_width()
        menu_y = 720 / 2 - self.menu_colonie_surface.get_height() / 2

        liste_textes = [info_ouvr, info_sold, info_groupes,info_vie, info_nourr, info_metal]

        for texte in liste_textes:
            couleur = AQUA if texte.split()[0] == self.hover_texte else WHITE
            _texte = self.font_menu.render(texte, False, couleur)
            _texte_rect = _texte.get_rect(
                center=(self.menu_colonie_surface.get_width() / 2, y_offset + _texte.get_height() / 2))
            self.menu_colonie_surface.blit(_texte, (
            self.menu_colonie_surface.get_width() / 2 - _texte.get_width() / 2, y_offset))
            if texte.startswith("Ouvrières") or texte.startswith("Soldats") or texte.startswith("Groupes"):
                self.texte_rects[texte.split()[0]] = _texte_rect.move(menu_x, menu_y)
            y_offset += 40
        self.menu_a_updater = False

    def update_menu_fourmis(self):
        if not self.menu_f_a_updater or not self.menu_fourmis_ouvert:
            return
        self.menu_fourmis_surface.fill(BLACK)

        y_offset = 40

        list_surface = pygame.Surface((250, max(len(self.fourmis) * 50, 375)))
        list_surface.fill(BLACK)


        if self.curr_tab == "Ouvrières":
            fourmis = [f for f in self.fourmis if isinstance(f, Ouvriere)]
        else:
            fourmis = [f for f in self.fourmis if isinstance(f, Soldat)]


        for fourmi in fourmis:
            if isinstance(fourmi, Ouvriere):
                sprite_sheet = self.sprite_sheet_ouvr
            elif isinstance(fourmi, Soldat):
                sprite_sheet = self.sprite_sheet_sold

            sprite = FourmisSprite(fourmi, sprite_sheet, 32, 32, 8, 250, 1/2).extract_frames()[0]
            #sprite = pygame.transform.scale(sprite, (32, 32))
            list_surface.blit(sprite, (10, y_offset - 10))
            #ant_info=""
            if fourmi.current_colonie is not None:
                ant_info = f"HP: {int(fourmi.hp)} Nid Pos: ({int(fourmi.centre_in_nid[0])}, {int(fourmi.centre_in_nid[1])})"
            else:
                ant_info = f"HP: {int(fourmi.hp)} Map Pos: ({int(fourmi.centre_in_map[0])}, {int(fourmi.centre_in_map[1])})"
            if fourmi.is_busy:
                _texte = self.font_menu.render(ant_info, False, RED)
            else:
                _texte = self.font_menu.render(ant_info, False, WHITE)
            list_surface.blit(_texte, (50, y_offset))

            rect = pygame.Rect(0, y_offset - 15, 250, 50)
            if self.fourmis_selection == fourmi:
                pygame.draw.rect(list_surface, GREEN, rect, 2)

            # elif rect.collidepoint((rel_x, rel_y)):
            #     pygame.draw.rect(list_surface, AQUA, rect, 2)

            y_offset += 50

        self.menu_fourmis_surface.blit(list_surface, (0, -self.scroll_offset))
        self.menu_f_a_updater = False


    def menu_colonie(self):
        self.update_menu()
        self.screen.blit(self.menu_colonie_surface, (self.screen.get_width() - self.menu_colonie_surface.get_width(), self.screen.get_height() / 2 - self.menu_colonie_surface.get_height() / 2))

    def menu_fourmis(self):
        self.update_menu_fourmis()
        self.screen.blit(self.menu_fourmis_surface, (0, self.screen.get_height() / 2 - self.menu_fourmis_surface.get_height() / 2))

    def load_sprites(self):
        for f in self.fourmis:
            sprite = FourmisSprite(f, self.sprite_sheets[type(f)], 32, 32, 8, 100,1/2)
            self.sprite_dict[f] = sprite
            self.sprites.append(sprite)

    def update_fourmis_tuiles(self, modif_tuiles):
        for tuile in modif_tuiles:
            self.map_data[tuile[1]][tuile[0]].fourmis = None

        for tuile, groupe in self.groupes_cache.items():

            self.gerer_collection(tuile, groupe)
            self.map_data[tuile[1]][tuile[0]].fourmis = self.get_fourmis_de_groupe(groupe)

    def gerer_collection(self, tuile, _groupe):
        x, y = tuile
        if self.map_data[y][x].tuile_ressource and not self.map_data[y][x].collectee:
            ress = self.map_data[y][x].get_ressource()
            groupe = self.get_fourmis_de_groupe(_groupe)
            if isinstance(groupe, Fourmis) and len(groupe.inventaire) < groupe.inventaire_taille_max:
                groupe.inventaire.append(ress)
                self.map_data[y][x].collectee = True
            elif isinstance(groupe, Groupe):
                if groupe.collecter_ressource(ress):
                    self.map_data[y][x].collectee = True

    def gerer_depot(self, tuile, groupe):
        if tuile == self.tuile_debut:
            occupants = self.get_fourmis_de_groupe(groupe)
            if isinstance(occupants, Fourmis):
                if occupants.tient_ressource == "metal":
                    self.metal += 1
                elif occupants.tient_ressource == "pomme":
                    self.nourriture += 1
                occupants.tient_ressource = None
            if isinstance(groupe, Groupe) and groupe.get_nb_fourmis() > 1:
                nourr, metal = groupe.deposer_ressources()
                self.metal += metal
                self.nourriture += nourr
            self.menu_a_updater = True
            self.update_menu()

    def fourmi_dans_groupe(self, fourmi):
        for _, groupe in self.groupes_cache.items():
            if groupe.get_nb_fourmis() >1 and fourmi in groupe.fourmis:
                return True
    def get_fourmis_de_groupe(self, groupe) -> Fourmis | Groupe:
        if groupe.get_nb_fourmis() == 1:
            return groupe.fourmis[0] # Retourne une fourmi particuliere
        return groupe

    def get_vrai_nb_groupes(self):
        tot = 0
        for tuile, groupe in self.groupes_cache.items():
            if groupe.get_nb_fourmis() > 1:
                tot += 1
        return tot

    def load_groupe_images(self):
        for x in range(2,6):
            self.groupe_images.append(pygame.image.load(trouver_img("UI/"+f"numero-{x}.png")))

    def render_ants(self, tile_size, screen, camera,dt):
        for fourmi in self.fourmis:
            fourmi.draw_in_map(dt,screen,camera)

    def handle_click(self, pos, tile_x, tile_y, screen):
        if self.map_data[tile_y][tile_x].fourmis is not None:
            occupants = self.map_data[tile_y][tile_x].fourmis
            if isinstance(occupants, Fourmis):
                if occupants == self.fourmis_selection:
                    self.fourmis_selection = None
                else:
                    self.fourmis_selection = occupants

                keys = pygame.key.get_pressed()
                if keys[pygame.K_d]:
                    occupants.digging = not occupants.digging

                self.menu_f_a_updater = True
                return

            if isinstance(occupants, Groupe):
                if self.groupe_selection == occupants:
                    self.groupe_selection = None
                else:
                    self.groupe_selection = occupants

                self.menu_f_a_updater = True
                return

        for f in self.fourmis:
            if f.dans_carte() and f.get_tuile() == (tile_x, tile_y):
                if self.fourmis_selection == f:
                    self.fourmis_selection = None
                else:
                    self.fourmis_selection = f
                self.menu_f_a_updater = True
                return

        if tile_x == self.tuile_debut[0] and tile_y == self.tuile_debut[1]:
            self.menu_colonie()
            return

        for key, rect in self.texte_rects.items():
            if rect.collidepoint(pos):
                self.last_tab = self.curr_tab
                if key=="Ouvrières":
                    self.curr_tab = "Ouvrières"
                elif key=="Soldats":
                    self.curr_tab = "Soldats"
                elif key=="Groupes":
                    self.curr_tab = "Groupes"
                self.scroll_offset = 0
                self.couleur_texte = AQUA
                # On ferme le menu si on re clique sur le meme tab
                self.menu_fourmis_ouvert = not self.menu_fourmis_ouvert if key == self.last_tab else True

                self.menu_a_updater = True
                self.menu_f_a_updater = True
                return

        if self.menu_fourmis_ouvert and self.menu_fourmis_rect.collidepoint(pos):
            rel_x = pos[0] - self.menu_fourmis_rect.x
            rel_y = pos[1] - self.menu_fourmis_rect.y + self.scroll_offset

            y_offset = 40
            if self.curr_tab == "Ouvrières":
                fourmis = [f for f in self.fourmis if isinstance(f, Ouvriere)]
            elif self.curr_tab == "Soldats":
                fourmis = [f for f in self.fourmis if isinstance(f, Soldat)]

            for fourmi in fourmis:
                rect = pygame.Rect(0, y_offset - 5, 250, 50)

                if rect.collidepoint((rel_x, rel_y)):
                    if self.fourmis_selection == fourmi:
                        self.fourmis_selection = None

                    else:
                        self.fourmis_selection = fourmi

                    self.menu_f_a_updater = True
                    return

                y_offset += 50


    def handle_hover(self, pos):
        if self.menu_colonie_rect.collidepoint(pos):
            for key, rect in self.texte_rects.items():
                if rect.collidepoint(pos):
                    self.hover_texte = key
                    self.menu_a_updater = True
                    self.update_menu()
                    return
                else:
                    self.hover_texte = None
                    self.menu_a_updater = True
                    self.update_menu()


    def handle_scroll(self, dir, pos):
        if self.curr_tab == "Ouvrières":
            max_offset = max(0, self.nombre_ouvrieres() * 50 - 335)
        elif self.curr_tab == "Soldats":
            max_offset = max(0, self.nombre_soldats() * 50 - 335)

        if self.menu_fourmis_rect.collidepoint(pos): # On scroll seulement si la souris est dans le rect du menu
            if dir == "up":
                self.scroll_offset = max(0, self.scroll_offset - self.scroll_speed)
            elif dir  == "down":
                self.scroll_offset = min(max_offset, self.scroll_offset + self.scroll_speed)
            self.scrolling = True
            self.menu_f_a_updater = True
            self.update_menu_fourmis()
        else: self.scrolling = False

class ColonieIA:
    def __init__(self, tuile_debut, map_data, tuiles_debut_toutes_colonies,graphe,listes_fourmis_jeu_complet):
        self.sprite_sheet_ouvr = pygame.image.load(trouver_img("Fourmis/sprite_sheet_fourmi_rouge.png")).convert_alpha()
        self.sprite_sheet_sold = pygame.image.load(trouver_img("Fourmis/sprite_sheet_fourmi_rouge.png")).convert_alpha()
        self.map_data = map_data  # la carte de jeu
        self.tuile_debut = tuile_debut
        self.screen = None
        self.vie = 1  # 1 = 100% (vie de la reine)
        self.nourriture = 0
        self.choix_timer = 0

        self.graphe = graphe

        self.hp = 1000

        for salle in self.graphe.salles:
            if salle.type == TypeSalle.SORTIE:
                self.sortie = salle
            elif salle.type == TypeSalle.THRONE:
                self.throne = salle

        self.fourmis = [Ouvriere(self.throne.noeud.coord[0], self.throne.noeud.coord[1], CouleurFourmi.ROUGE, self, self.throne) for _ in
                        range(2)] + [Soldat(self.throne.noeud.coord[0], self.throne.noeud.coord[1], CouleurFourmi.ROUGE, self, self.throne) for
                                     _ in range(2)]
        
        for fourmi in self.fourmis:
            listes_fourmis_jeu_complet.append(fourmi)

        self.sprite_sheets = {
            Ouvriere: self.sprite_sheet_ouvr,
            Soldat: self.sprite_sheet_sold
        }
        self.sprite_dict = {}
        self.sprites = []
        self.load_sprites()

        self.tuiles_debut = tuiles_debut_toutes_colonies
        self.tuiles_ressource = set()
        self.liste_fourmis_jeu_complet = listes_fourmis_jeu_complet
        self.toutes_colonies = None


    def process(self, dt, tous_les_nids, liste_fourmis_jeu_complet, liste_toutes_colonies, map_data):
        self.toutes_colonies = liste_toutes_colonies
        # Processus de l'IA
        fourmis_bouge = False
        self.choix_timer += dt
        if self.choix_timer >= 3000:

            # Choisir une action pour l'IA
            self.choix()
            self.choix_timer = 0


        for f in self.fourmis:
            f.process(dt, self.map_data, tous_les_nids, liste_fourmis_jeu_complet, liste_toutes_colonies)

            if not f.dans_carte():
                continue

            dern_x, dern_y = f.centre_in_map[0], f.centre_in_map[1]
            if (dern_x, dern_y) != (f.centre_in_map[0], f.centre_in_map[1]):
                fourmis_bouge = True
                self.collecte_fourmi(f)

        for salle in self.graphe.salles:
            salle.process(liste_fourmis_jeu_complet,self,dt, map_data, liste_toutes_colonies)

    def choix(self):
        if self.en_danger():
            self.envoyer_fourmis_dans_nid()
        else:
            self.meilleure_action()

    def meilleure_action(self):
        if self.check_nourriture():
            self.chercher_nourriture()

    def check_nourriture(self):
        if self.nourriture < len(self.get_fourmis_type()[0]):
            return True
        return False

    def en_danger(self):
        if self.ennemis_dans_nid() == 0: return False
        else:
            if self.fourmis_dans_nid()[0] / self.ennemis_dans_nid() < 0.8:
                return True
        return False

    def chercher_nourriture(self):
        tuiles = self.trouver_tuiles_ressources()
        partie = int(len(self.get_fourmis_type()[0]) * 0.65)
        ouvr_a_envoyer = random.sample(self.get_fourmis_type()[0], partie)
        for f in ouvr_a_envoyer:
            if not f.is_busy:
                if (f.target_in_map is None) and len(f.inventaire) < f.inventaire_taille_max:
                    tuile = random.choice(tuiles)
                    f.set_target_in_map(tuile[0], tuile[1], self.map_data, self.toutes_colonies)

    def trouver_tuiles_ressources(self):
        tuiles = []
        for y in range(self.tuile_debut[1]-20, self.tuile_debut[1]+20):
            for x in range(self.tuile_debut[0]-20, self.tuile_debut[0]+20):
                if 0 <= y < 100 and 0 <= x < 100:
                    if self.map_data[y][x].tuile_ressource and not self.map_data[y][x].collectee:
                        tuiles.append((x, y))
        return tuiles

    def envoyer_fourmis_dans_nid(self):
        pass

    def fourmis_dans_nid(self):
        tot = 0
        f_dans_nid = []
        for f in self.fourmis:
            if f.current_colonie == self:
                tot += 1
                f_dans_nid.append(f)
        return (tot, f_dans_nid)

    def get_fourmis_type(self):
        ouvr = []
        sold = []
        for f in self.fourmis:
            if isinstance(f, Ouvriere):
                ouvr.append(f)
            if isinstance(f, Soldat):
                sold.append(f)
        return ouvr, sold

    def ennemis_dans_nid(self):
        ennemis = [
        f for f in self.liste_fourmis_jeu_complet
            if f not in self.fourmis
        ]

        return len(ennemis)

    def collecte_fourmi(self, f):
        x, y = f.get_tuile()
        if self.map_data[y][x].tuile_ressource and not self.map_data[y][x].collectee and (x, y) == (f.target_in_map[0], f.target_in_map[1]):
            ress = self.map_data[y][x].get_ressource()
            if len(f.inventaire) < f.inventaire_taille_max:
                f.inventaire.append(ress)
                self.map_data[y][x].collectee = True
                f.set_target_in_nid(self.throne.noeud.coord, self, self.map_data, self.toutes_colonies)

    def load_sprites(self):
        for f in self.fourmis:
            sprite = FourmisSprite(f, self.sprite_sheets[type(f)], 32, 32, 8, 100,1/2)
            self.sprite_dict[f] = sprite
            self.sprites.append(sprite)

    def render_ants(self, tile_size, screen, camera):
        for fourmi in self.fourmis:
            if fourmi.current_colonie is None:
                sprite = self.sprite_dict[fourmi]
                sprite.update(pygame.time.get_ticks() / 1000, camera, tile_size)
                if screen.get_rect().colliderect(sprite.rect):
                    screen.blit(sprite.image, sprite.rect)

