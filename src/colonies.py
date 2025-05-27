import math
import random
import pygame
from pygame import Vector2
from config import trouver_font, trouver_img, TypeItem
from config import BLACK, WHITE, AQUA, GREEN, RED
from config import CouleurFourmi
from fourmi_types import Ouvriere, Soldat
from fourmi import FourmisSprite, Fourmis
from classes_graphe import TypeSalle, Salle


class Colonie:
    def __init__(self, tuile_debut, map_data, tuiles_debut_toutes_colonies,graphe,liste_fourmis_jeu_complet):
        self.sprite_sheet_ouvr = pygame.image.load(trouver_img("Fourmis/sprite_sheet_fourmi_noire.png")).convert_alpha()
        self.sprite_sheet_sold = pygame.image.load(trouver_img("Fourmis/sprite_sheet_fourmi_noire.png")).convert_alpha()
        self.map_data = map_data
        self.tuile_debut = tuile_debut
        self.screen = None

        self.graphe = graphe

        self.hp = 1000
        self.max_hp = 1000
        for salle in self.graphe.salles:
            if salle.type == TypeSalle.SORTIE:
                self.sortie = salle
            elif salle.type == TypeSalle.THRONE:
                self.throne = salle

        self.fourmis_selection = None # fourmi selectionnée dans le menu de fourmis

        self.fourmis = [Ouvriere(self.throne.noeud.coord[0], self.throne.noeud.coord[1], CouleurFourmi.NOIRE, self, self.throne) for _ in range(2)] + [Soldat(self.throne.noeud.coord[0], self.throne.noeud.coord[1], CouleurFourmi.NOIRE, self, self.throne) for _ in range(2)]
        
        for fourmi in self.fourmis:
            liste_fourmis_jeu_complet.append(fourmi)
        self.liste_fourmis_jeu_complet = liste_fourmis_jeu_complet
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
        self.petit_font_menu = pygame.font.Font(trouver_font("LowresPixel-Regular.otf"), 15)
        self.last_tab = self.curr_tab

        self.menu_colonie_surface = pygame.Surface((250, 375))
        self.menu_fourmis_surface = pygame.Surface((250, 375))
        self.menu_a_updater = True # si le menu colonie a besoin d'etre mis a jour
        self.menu_f_a_updater = True # si le menu fourmis a besoin d'etre mis a jour
        self.menu_fourmis_rect = pygame.Rect(0, 720 / 2 - self.menu_fourmis_surface.get_height() / 2, 250, 375)
        self.menu_colonie_rect = pygame.Rect(1280 - self.menu_colonie_surface.get_width(), 720 / 2 - self.menu_colonie_surface.get_height() / 2, 250, 375)
        self.update_menu()
        self.update_menu_fourmis()

        self.tuiles_debut = tuiles_debut_toutes_colonies
        self.stop_processing_salles_other_than_sortie_when_dead = False

    def process(self,dt,tous_les_nids,liste_toutes_colonies):
        # groupe_bouge = False
        # for _, groupe in self.groupes_cache.items():
        #     if groupe.get_nb_fourmis() > 1 and not groupe.est_vide():
        #         dern_x, dern_y = groupe.centre_x_in_map, groupe.centre_y_in_map
        #         groupe.process(dt)
        #         if (dern_x, dern_y) != (groupe.centre_x_in_map, groupe.centre_y_in_map):
        #             groupe_bouge = True

        for f in self.fourmis:
            f.process(dt, self.map_data,tous_les_nids,self.liste_fourmis_jeu_complet,liste_toutes_colonies)

        for salle in self.graphe.salles:
            if salle.type != TypeSalle.SORTIE and not self.stop_processing_salles_other_than_sortie_when_dead:
                salle.process(self.liste_fourmis_jeu_complet, self, dt, self.map_data, liste_toutes_colonies)
            else:
                salle.process(self.liste_fourmis_jeu_complet, self, dt, self.map_data, liste_toutes_colonies)

        if self.menu_fourmis_ouvert:
            self.menu_f_a_updater = True
        if self.menu_colonie_ouvert:
            self.menu_a_updater = True

    def nombre_ouvrieres(self):
        return len([f for f in self.fourmis if isinstance(f, Ouvriere)])

    def nombre_soldats(self):
        return len([f for f in self.fourmis if isinstance(f, Soldat)])

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
                elif item.name=="BOIS":
                    nb_metal+=1

        info_ouvr = f"Ouvrières ({self.nombre_ouvrieres()})"
        info_sold = f"Soldats ({self.nombre_soldats()})"
        info_vie = "Vie: "+str(self.hp)
        info_nourr = "Nourriture: "+str(nb_nourriture)
        info_metal = "Métal: "+str(nb_metal)
        info_bois = "Bois: "+str(nb_metal)

        menu_x = 1280 - self.menu_colonie_surface.get_width()
        menu_y = 720 / 2 - self.menu_colonie_surface.get_height() / 2

        liste_textes = [info_ouvr, info_sold,info_vie, info_nourr, info_metal, info_bois]

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
                if fourmi.digging:
                    ant_info = f'DIGGING - Nid Pos: ({int(fourmi.centre_in_nid[0])}, {int(fourmi.centre_in_nid[1])})'
                else: ant_info = f"HP: {int(fourmi.hp)} Nid Pos: ({int(fourmi.centre_in_nid[0])}, {int(fourmi.centre_in_nid[1])})"
            else:
                ant_info = f"HP: {int(fourmi.hp)} Map Pos: ({int(fourmi.centre_in_map[0])}, {int(fourmi.centre_in_map[1])})"
            if fourmi.is_busy:
                _texte = self.petit_font_menu.render(ant_info, False, RED)
            else:
                _texte = self.petit_font_menu.render(ant_info, False, WHITE)
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

    def handle_click(self, pos, tile_x, tile_y, screen):
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

        self.map_data = map_data  # la carte de jeu
        self.tuiles_ressources = set()
        self.tuile_debut = tuile_debut
        self._dern_search = 0 # temps depuis dernier search de ressources
        self._cache_ressources = set()

        self.screen = None

        self.graphe = graphe

        self.hp = 1000


        for salle in self.graphe.salles:
            if salle.type == TypeSalle.SORTIE:
                self.sortie = salle
            elif salle.type == TypeSalle.THRONE:
                self.trone_coords = salle.noeud.coord
                self.salle_trone = salle
            elif salle.type == TypeSalle.BANQUE:
                self.banque_coords = salle.noeud.coord
                self.salle_banque = salle

        self.toutes_salles = self.sortie.liste_types_salles
        self.salles_manquantes = [salle for salle in self.toutes_salles if salle not in [s.type for s in self.graphe.salles]]
        self.nouv_salles_coords = {s: None for s in self.salles_manquantes}
        self._nouv_salles = {}

        self.couleur_fourmi = CouleurFourmi.ROUGE
        self.fourmis = [Ouvriere(self.trone_coords[0], self.trone_coords[1], CouleurFourmi.ROUGE, self, self.salle_trone) for _ in
                        range(2)] + [Soldat(self.trone_coords[0], self.trone_coords[1], CouleurFourmi.ROUGE, self, self.salle_trone) for
                                     _ in range(2)]

        for fourmi in self.fourmis:
            listes_fourmis_jeu_complet.append(fourmi)

        self.digging_queue_fourmis = {}

        self.tuiles_debut = tuiles_debut_toutes_colonies
        self.liste_fourmis_jeu_complet = listes_fourmis_jeu_complet
        self.toutes_colonies = None


    def process(self, dt, tous_les_nids, liste_toutes_colonies):

        self.toutes_colonies = liste_toutes_colonies
        # Processus de l'IA
        fourmis_bouge = False
        for salle in self.graphe.salles:
            salle.process(self.liste_fourmis_jeu_complet, self, dt, self.map_data, liste_toutes_colonies)

        #self.choix()

        for f in self.fourmis:
            f.process(dt, self.map_data, tous_les_nids, self.liste_fourmis_jeu_complet, liste_toutes_colonies)
            self.gerer_collecte_fourmi(f)
            self.amener_oeufs(f)
            self.gerer_creation_salle(f)

            if not f.is_busy and f.target_in_map is None and f.target_in_nid is None:
                if isinstance(f, Ouvriere):
                    if self.check_nourriture():
                        self.chercher_nourriture(f)
                    elif self.check_banque():
                        self.chercher_bois_metal(f)

        if self.en_danger():
            self.envoyer_fourmis_dans_nid()

    def check_nourriture(self):
        if self.salle_trone.inventaire != self.salle_trone.inventaire_necessaire:
            return True
        return False

    def check_banque(self):
        if len(self.salle_banque.inventaire) < self.salle_banque.inventaire_taille_max:
            return True
        return False

    def en_danger(self):
        if self.ennemis_dans_nid() == 0: return False
        else:
            if self.fourmis_dans_nid()[0] // self.ennemis_dans_nid() < 0.8:

                return True
        return False

    def chercher_nourriture(self, f):
        if len(f.inventaire) >= f.inventaire_taille_max or \
        f.is_busy or \
        f.digging: return

        self.tuiles_ressources = self.trouver_tuiles_ressources()

        if f.target_in_map is None:

            pommes = [p for p in self.tuiles_ressources if self.map_data[p[1]][p[0]].get_ressource() == TypeItem.POMME]
            tuile_proche = self.tuile_ressource_proche(f, pommes)
            if tuile_proche:
                x, y = tuile_proche
                f.set_target_in_map(x, y, self.map_data, self.toutes_colonies)
                self.tuiles_ressources.remove(tuile_proche)
            else:
                self.chercher_bois_metal(f)

    def chercher_bois_metal(self, f):
        if len(f.inventaire) >= f.inventaire_taille_max or \
        f.is_busy or \
        f.digging: return

        self.tuiles_ressources = self.trouver_tuiles_ressources()

        if f.target_in_map is None:
            salle_ouvr = self.check_salle_existe(TypeSalle.TRAINING_OUVRIERE)
            salle_sold = self.check_salle_existe(TypeSalle.TRAINING_SOLDAT)

            if (salle_ouvr is not None and TypeItem.BOIS not in salle_ouvr.inventaire and TypeItem.BOIS not in self.salle_banque.inventaire) or \
            (salle_sold is not None and TypeItem.BOIS not in salle_sold.inventaire and TypeItem.METAL not in self.salle_banque.inventaire):
                liste = [b for b in self.tuiles_ressources if self.map_data[b[1]][b[0]].get_ressource() == TypeItem.BOIS]

            else:
                liste = [b for b in self.tuiles_ressources if self.map_data[b[1]][b[0]].get_ressource() in [TypeItem.METAL, TypeItem.BOIS]]
            tuile_proche = self.tuile_ressource_proche(f, liste)
            if tuile_proche:
                x, y = tuile_proche
                f.set_target_in_map(x, y, self.map_data, self.toutes_colonies)
                self.tuiles_ressources.remove(tuile_proche)
            else:
                pass

    def choisir_salle(self, fourmi, salle_type):
        if salle_type not in self.salles_manquantes:
            return
        intersections = [i for i in self.graphe.salles if i.type == TypeSalle.INTERSECTION]

        if not intersections:
            return

        intersections_valides = [i for i in intersections if len(i.tunnels) < 4]
        if not intersections_valides:
            return

        intersection = random.choice(intersections_valides)
        fourmi.set_target_in_nid(intersection.noeud.coord, self, self.map_data, self.toutes_colonies)

        directions_occupees = []
        for tunnel in intersection.tunnels:
            autre_salle = tunnel.arrivee if tunnel.depart == intersection else tunnel.depart
            dx = autre_salle.noeud.coord[0] - intersection.noeud.coord[0]
            dy = autre_salle.noeud.coord[1] - intersection.noeud.coord[1]
            angle = math.degrees(math.atan2(dy, dx))
            directions_occupees.append(angle)

        angles_possibles = []
        for angle in range(0, 360, 5):
            valide = True
            for dir_occupee in directions_occupees:
                diff_angle = min(abs(angle - dir_occupee), 360 - abs(angle - dir_occupee))
                if diff_angle < 45:
                    valide = False
                    break
            if valide:
                angles_possibles.append(angle)

        if not angles_possibles:
            return

        angle = random.choice(angles_possibles)
        dist = random.randint(250, 350)

        angle_rad = math.radians(angle)
        dx = math.cos(angle_rad) * dist
        dy = math.sin(angle_rad) * dist

        coord_nouv_salle = [
            intersection.noeud.coord[0] + dx,
            intersection.noeud.coord[1] + dy
        ]
        if coord_nouv_salle[1] < 128+100:
            return

        self.digging_queue_fourmis[fourmi] = intersection, coord_nouv_salle, salle_type


    def gerer_creation_salle(self, fourmi):
        if fourmi not in self.digging_queue_fourmis or fourmi.current_colonie is None:
            return

        intersection, coord_salle, salle_type = self.digging_queue_fourmis[fourmi]
        if not (fourmi.centre_in_nid[0], fourmi.centre_in_nid[1]) == (intersection.noeud.coord[0], intersection.noeud.coord[1]):
            return

        fourmi.digging = True
        self.graphe.creer_salle_depuis_intersection(intersection, coord_salle, fourmi)

        nouv_salle = None
        for s in self.graphe.salles:
            if s.type == TypeSalle.INDEFINI:
                nouv_salle = s
                break

        if nouv_salle:
            nouv_salle.type = salle_type
            self.nouv_salles_coords[nouv_salle.type] = nouv_salle.noeud.coord
            self._nouv_salles[nouv_salle.type] = nouv_salle
            self.salles_manquantes.remove(salle_type) if salle_type in self.salles_manquantes else None

            nouv_salle.type_specific_stats_update()
            fourmi.set_target_in_nid(nouv_salle.noeud.coord, self, self.map_data, self.toutes_colonies)
            self.digging_queue_fourmis.pop(fourmi)
            fourmi.digging = False
            return




    def trouver_tuiles_ressources(self, max_radius=25):
        x0, y0 = self.tuile_debut

        dt = pygame.time.get_ticks()
        if dt - self._dern_search < 3000:
            return self._cache_ressources

        toutes_resources = []
        for y in range(max(0, y0 - max_radius), min(len(self.map_data), y0 + max_radius + 1)):
            for x in range(max(0, x0 - max_radius), min(len(self.map_data[0]), x0 + max_radius + 1)):
                if self.map_data[y][x].tuile_ressource and not self.map_data[y][x].collectee:
                    dist = abs(x - x0) + abs(y - y0)
                    if dist <= max_radius:
                        toutes_resources.append((dist, (x, y)))
        toutes_resources.sort()
        tuiles = set(coord for _, coord in toutes_resources)
        if not tuiles:
            if max_radius >= 90:
                return self._cache_ressources
            self.trouver_tuiles_ressources(max_radius+10)
        self._dern_search = dt
        self._cache_ressources = tuiles
        return tuiles

    def tuile_ressource_proche(self, fourmi, tuiles) -> tuple[int, int] | None:
        if not tuiles:
            return None
        tuile_fourmi = None
        if fourmi.current_colonie == self:
            tuile_fourmi = fourmi.current_colonie.tuile_debut
        elif fourmi.current_colonie is None:
            tuile_fourmi = fourmi.get_tuile()
        tuile_proche = None
        min_dist = float('inf')

        for tuile in tuiles:
            dist = abs(tuile[0] - tuile_fourmi[0]) + abs(tuile[1] - tuile_fourmi[1])
            if dist < min_dist:
                min_dist = dist
                tuile_proche = tuile
        return tuile_proche

    def gerer_collecte_fourmi(self, f):

        def gerer_soldats(f):

            if isinstance(f, Soldat):
                if self.ennemis_dans_nid() == 0:
                    f.fourmi_attacking = None
                    f.is_attacking_for_defense_automatique = False
                    f.is_moving = False
                    f.is_busy = False
                    f.target_in_map = None
                    f.target_in_nid_queued = None
                    f.target_in_nid = None
                if not f.is_busy:
                    if f.current_colonie is None or f.current_colonie != self:
                        f.set_target_in_nid(self.trone_coords, self, self.map_data, self.toutes_colonies)
                    else:
                        if not (Vector2(self.salle_trone.noeud.coord[0], self.salle_trone.noeud.coord[1]) - Vector2(f.centre_in_nid[0],f.centre_in_nid[1])).magnitude() < TypeSalle.THRONE.value[0]:
                            if not f.inventaire and not f.current_salle == self.salle_trone:
                                f.set_target_in_nid(self.trone_coords, self, self.map_data, self.toutes_colonies)


        def envoyer_training(ressource):
            salle_ouvr = self.check_salle_existe(TypeSalle.TRAINING_OUVRIERE)
            salle_sold = self.check_salle_existe(TypeSalle.TRAINING_SOLDAT)
            if salle_ouvr is not None:
                if ressource not in salle_ouvr.inventaire and ressource in salle_ouvr.inventaire_necessaire:
                    f.set_target_in_nid(salle_ouvr.noeud.coord, self, self.map_data, self.toutes_colonies)
                    return True
            elif salle_sold is not None:
                if ressource not in salle_sold.inventaire and ressource in salle_sold.inventaire_necessaire:
                    f.set_target_in_nid(salle_sold.noeud.coord, self, self.map_data, self.toutes_colonies)
                    return True
            return False

        # Si sur carte, on send vers une salle (les fourmis restent prises dans des salles sils on la ressource et que la salle l'a deja)
        if f.centre_in_map is not None:
            x, y = f.get_tuile()
            if f.target_in_map is None and (isinstance(f, Ouvriere) or isinstance(f, Soldat)):
                if not f.current_salle == self.salle_trone:
                    f.set_target_in_nid(self.trone_coords, self, self.map_data, self.toutes_colonies)

            elif (f.target_in_map[0], f.target_in_map[1]) == f.get_tuile():
                ress = self.map_data[y][x].get_ressource()
                if not self.map_data[y][x].collectee and len(f.inventaire) < f.inventaire_taille_max:
                    f.inventaire.append(ress)
                    self.map_data[y][x].collectee = True
                if self.map_data[y][x].collectee and ress not in f.inventaire:
                    if ress == TypeItem.POMME:
                        pommes = [p for p in self.tuiles_ressources if self.map_data[p[1]][p[0]].get_ressource() == TypeItem.POMME]
                        tuile_proche = self.tuile_ressource_proche(f, pommes)
                        if tuile_proche:
                            x, y = tuile_proche
                            f.set_target_in_map(x, y, self.map_data, self.toutes_colonies)
                            self.tuiles_ressources.remove(tuile_proche)
                    elif ress in [TypeItem.METAL, TypeItem.BOIS]:
                        bois_metal = [b for b in self.tuiles_ressources if self.map_data[b[1]][b[0]].get_ressource() in [TypeItem.METAL, TypeItem.BOIS]]
                        tuile_proche = self.tuile_ressource_proche(f, bois_metal)
                        if tuile_proche:
                            x, y = tuile_proche
                            f.set_target_in_map(x, y, self.map_data, self.toutes_colonies)
                            self.tuiles_ressources.remove(tuile_proche)

                if ress == TypeItem.POMME and ress in f.inventaire:
                    if not envoyer_training(ress):
                        f.set_target_in_nid(self.trone_coords, self, self.map_data, self.toutes_colonies)
                elif ress in [TypeItem.METAL, TypeItem.BOIS] and ress in f.inventaire:
                    if not envoyer_training(ress):
                        if ress == TypeItem.METAL:
                            if self.check_banque():
                                meule = self.check_salle_existe(TypeSalle.MEULE)
                                enclume = self.check_salle_existe(TypeSalle.ENCLUME)
                                if meule is not None and meule.inventaire != meule.inventaire_necessaire:
                                    f.set_target_in_nid(meule.noeud.coord, self, self.map_data, self.toutes_colonies)
                                elif enclume is not None and enclume.inventaire != enclume.inventaire_necessaire:
                                    f.set_target_in_nid(enclume.noeud.coord, self, self.map_data, self.toutes_colonies)
                                else:
                                    f.set_target_in_nid(self.banque_coords, self, self.map_data, self.toutes_colonies)
                        else: f.set_target_in_nid(self.banque_coords, self, self.map_data, self.toutes_colonies)

        else:
            gerer_soldats(f)
            if isinstance(f, Ouvriere) and not f.is_busy:
                for item in f.inventaire:
                    if item in f.current_salle.inventaire:
                        if f.current_salle.type in [TypeSalle.TRAINING_OUVRIERE, TypeSalle.TRAINING_SOLDAT, TypeSalle.THRONE]:
                            if item == TypeItem.POMME:
                                if not envoyer_training(item):
                                    if self.check_nourriture():
                                        f.set_target_in_nid(self.trone_coords, self, self.map_data, self.toutes_colonies)
                                    else:
                                        f.set_target_in_nid(self.banque_coords, self, self.map_data, self.toutes_colonies)

                            elif item == TypeItem.BOIS:
                                if not envoyer_training(item):
                                    f.set_target_in_nid(self.banque_coords, self, self.map_data, self.toutes_colonies)



    def amener_oeufs(self, f):
        if TypeItem.OEUF not in f.inventaire:
            return

        if any(ant.digging for ant in self.fourmis):
            return

        ouvr, sold = self.get_fourmis_type()
        ouvr_count, sold_count = len(ouvr), len(sold)

        if sold_count == 0:
            target_room_type = TypeSalle.TRAINING_SOLDAT
        elif ouvr_count < sold_count:
            target_room_type = TypeSalle.TRAINING_OUVRIERE
        elif sold_count < ouvr_count / 3:
            target_room_type = TypeSalle.TRAINING_SOLDAT
        else:
            target_room_type = TypeSalle.TRAINING_OUVRIERE

        if target_room_type not in self.salles_manquantes:
            salle = self.check_salle_existe(target_room_type)
            if salle is not None:
                if TypeItem.OEUF not in salle.inventaire:
                    f.set_target_in_nid(salle.noeud.coord, self, self.map_data, self.toutes_colonies)
                else:
                    f.set_target_in_nid(self.banque_coords, self, self.map_data, self.toutes_colonies)
                return

        if (target_room_type in self.salles_manquantes and
                not any(room_type == target_room_type for _, _, room_type in self.digging_queue_fourmis.values())):
            if not f.digging and len(self.digging_queue_fourmis) == 0:
                self.choisir_salle(f, target_room_type)



    def check_salle_existe(self, salle_type) -> Salle:
        if salle_type not in self.salles_manquantes:
            for salle in self.graphe.salles:
                if salle.type == salle_type:
                    return salle
        else:
            return None

    def fourmis_dans_nid(self):
        tot = 0
        f_dans_nid = []
        for f in self.fourmis:
            if f.current_colonie is not None and f.current_colonie == self:
                tot += 1
                f_dans_nid.append(f)
        return tot, f_dans_nid

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
            and f.current_colonie == self
        ]

        return len(ennemis)

    def envoyer_fourmis_dans_nid(self):
        for f in self.fourmis:
            if f.current_colonie is None and f.target_in_map is None:
                f.set_target_in_nid(self.trone_coords, self, self.map_data, self.toutes_colonies)

