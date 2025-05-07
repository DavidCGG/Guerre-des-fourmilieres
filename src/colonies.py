import tkinter as tk
import pygame
from fourmi import Ouvriere, Soldat, Groupe, Fourmis
from config import BLACK, trouver_font, WHITE, AQUA, trouver_img, GREEN, RED, TypeItem
from fourmi import FourmisSprite
from fourmi import CouleurFourmi

class Colonie:
    def __init__(self, tuile_debut, map_data, tuiles_debut_toutes_colonies,graphe,listes_fourmis_jeu_complet):
        #self.graphe = graphe
        #print("a")
        self.sprite_sheet_ouvr = pygame.image.load(trouver_img("Fourmis/sprite_sheet_fourmi_noire.png")).convert_alpha()
        self.sprite_sheet_sold = pygame.image.load(trouver_img("Fourmis/sprite_sheet_fourmi_noire.png")).convert_alpha()
        self.map_data = map_data # la carte de jeu
        self.tuile_debut = tuile_debut
        self.vie = 1 # 1 = 100% (vie de la reine)
        self.inventaire=[]
        self.taille_inventaire_max=10

        self.graphe=graphe

        self.hp=1000

        #debug only pour voir si graphe est avec la bonne tuile debut/ colonie
        #self.sortie_coords=None
        for salle in self.graphe.salles:
            #print(salle.type.value[1])
            if salle.type.value[1] == "sortie":
                self.sortie_coords=salle.noeud.coord
        #print("Tuile debut: "+str(tuile_debut)+" Sortie debut: "+str(self.sortie_coords))

        self.fourmis_selection = None # fourmi selectionnée dans le menu de fourmis
        self.groupe_selection = None

        self.fourmis = [Ouvriere(self.tuile_debut[0], self.tuile_debut[1], CouleurFourmi.NOIRE, self) for _ in range(2)] + [Soldat(self.tuile_debut[0], self.tuile_debut[1], CouleurFourmi.NOIRE,self) for _ in range(2)]
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

        self.tuiles_debut=tuiles_debut_toutes_colonies


    def process(self,dt,tous_les_nids,listes_fourmis_jeu_complet):
        groupe_bouge = False
        for _, groupe in self.groupes_cache.items():
            if groupe.get_nb_fourmis() > 1 and not groupe.est_vide():
                dern_x, dern_y = groupe.centre_x_in_map, groupe.centre_y_in_map
                groupe.process(dt)
                if (dern_x, dern_y) != (groupe.centre_x_in_map, groupe.centre_y_in_map):
                    groupe_bouge = True

        fourmis_bouge = False

        for f in self.fourmis:
            if not self.fourmi_dans_groupe(f):
                dern_x, dern_y = f.centre_x_in_map, f.centre_y_in_map
                f.process(dt, self.map_data, tous_les_nids)
                if (dern_x, dern_y) != (f.centre_x_in_map, f.centre_y_in_map):
                    fourmis_bouge = True
                """
                if f.in_colonie_map_coords is None and f.get_tuile() == self.tuile_debut:
                    ress = f.depot()
                    self.nourriture += 1 if ress == "pomme" else 0
                    self.metal += 1 if ress == "metal" else 0
                    f.tient_ressource = None
                """

        for salle in self.graphe.salles:
            salle.process(listes_fourmis_jeu_complet, self, dt)

        if fourmis_bouge or groupe_bouge:
            self.cache_groupes_a_updater = True
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
        for item in self.inventaire:
            if item.name=="POMME":
                nb_nourriture+=1
            elif item.name=="METAL":
                nb_metal+=1

        info_ouvr = f"Ouvrières ({self.nombre_ouvrieres()})"
        info_sold = f"Soldats ({self.nombre_soldats()})"
        info_groupes = f"Groupes ({self.get_vrai_nb_groupes()})"
        info_vie = f"Vie: {self.vie * 100}%"
        info_nourr = "Nourriture: "+str(nb_nourriture)
        info_metal = "Métal: "+str(nb_metal)

        menu_x = 1280 - self.menu_colonie_surface.get_width()
        menu_y = 720 / 2 - self.menu_colonie_surface.get_height() / 2

        liste_textes = [info_ouvr, info_sold, info_groupes,info_vie, info_nourr, info_metal]

        for texte in liste_textes:
            couleur = AQUA if texte.split()[0] == self.hover_texte else WHITE
            _texte = self.font_menu.render(texte, True, couleur)
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
            if fourmi.in_colonie_map_coords is not None:
                ant_info = f"HP: {fourmi.hp} Nid Pos: ({int(fourmi.centre_x_in_nid)}, {int(fourmi.centre_y_in_nid)})"
            else:
                ant_info = f"HP: {fourmi.hp} Map Pos: ({int(fourmi.centre_x_in_map)}, {int(fourmi.centre_y_in_map)})"
            if fourmi.is_busy:
                _texte = self.font_menu.render(ant_info, True, RED)
            else:
                _texte = self.font_menu.render(ant_info, True, WHITE)
            list_surface.blit(_texte, (50, y_offset))

            rect = pygame.Rect(0, y_offset - 15, 250, 50)
            if self.fourmis_selection == fourmi:
                pygame.draw.rect(list_surface, GREEN, rect, 2)

            # elif rect.collidepoint((rel_x, rel_y)):
            #     pygame.draw.rect(list_surface, AQUA, rect, 2)

            y_offset += 50

        self.menu_fourmis_surface.blit(list_surface, (0, -self.scroll_offset))
        self.menu_f_a_updater = False


    def menu_colonie(self, screen):
        #print("menu colonie drawn")
        self.update_menu()
        screen.blit(self.menu_colonie_surface, (screen.get_width() - self.menu_colonie_surface.get_width(), screen.get_height() / 2 - self.menu_colonie_surface.get_height() / 2))

    def menu_fourmis(self, screen):
        #print("menu fourmi drawn")
        self.update_menu_fourmis()
        screen.blit(self.menu_fourmis_surface, (0, screen.get_height() / 2 - self.menu_fourmis_surface.get_height() / 2))


    def load_sprites(self):
        for f in self.fourmis:
            sprite = FourmisSprite(f, self.sprite_sheets[type(f)], 32, 32, 8, 100,1/2)
            self.sprite_dict[f] = sprite
            self.sprites.append(sprite)

    def update_cache_groupes(self):
        ants_by_tile = {}
        for f in self.fourmis:
            if f.in_colonie_map_coords is None:
                tuile = f.get_tuile()
                if tuile not in ants_by_tile:
                    ants_by_tile[tuile] = []
                ants_by_tile[tuile].append(f)

        # Track tiles that need updating
        modif_tuiles = set()

        # Update existing groups or create new ones
        nouv_groupe = {}
        for tuile, ants in ants_by_tile.items():
            # Find existing group at this tile
            existing_group = next((g for g in self.groupes.values()
                                   if g.get_tuile() == tuile), None)

            if existing_group:
                # Update existing group
                existing_group.fourmis = []
                for ant in ants:
                    existing_group.ajouter_fourmis(ant)
                nouv_groupe[tuile] = existing_group
            else:
                # Create new group
                new_group = Groupe(tuile[0], tuile[1], self.groupe_images)
                self.groupes[new_group.id] = new_group
                for ant in ants:
                    new_group.ajouter_fourmis(ant)
                nouv_groupe[tuile] = new_group

            # Mark tile as modified
            if tuile not in self.groupes_cache or self.groupes_cache[tuile] != nouv_groupe[tuile]:
                modif_tuiles.add(tuile)

        # Find tiles that no longer have groups
        for tuile in self.groupes_cache:
            if tuile not in nouv_groupe:
                modif_tuiles.add(tuile)

        # Clean up empty groups
        for group_id in list(self.groupes.keys()):
            group = self.groupes[group_id]
            if group.est_vide() or group not in nouv_groupe.values():
                del self.groupes[group_id]

        self.groupes_cache = nouv_groupe
        self.cache_groupes_a_updater = False
        self.menu_a_updater = True

        self.update_fourmis_tuiles(modif_tuiles)


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
            if isinstance(groupe, Fourmis) and len(groupe.inventaire) <groupe.inventaire_taille_max:
                print("fourmi collecte")
                groupe.inventaire.append(ress)
                self.map_data[y][x].collectee = True
            elif isinstance(groupe, Groupe):
                if groupe.collecter_ressource(ress):
                    print("groupe collecte")
                    self.map_data[y][x].collectee = True

    def gerer_depot(self, tuile, groupe):
        if tuile == self.tuile_debut:
            occupants = self.get_fourmis_de_groupe(groupe)
            if isinstance(occupants, Fourmis):
                if occupants.tient_ressource == "metal":
                    print("depot fourmi metal")
                    self.metal += 1
                elif occupants.tient_ressource == "pomme":
                    print("depot fourmi pomme")
                    self.nourriture += 1
                occupants.tient_ressource = None
            if isinstance(groupe, Groupe) and groupe.get_nb_fourmis() > 1:
                print("depot groupe")
                nourr, metal = groupe.deposer_ressources()
                print(nourr, metal, groupe)
                self.metal += metal
                self.nourriture += nourr
            self.menu_a_updater = True
            self.update_menu()
            print(self.nourriture, self.metal)

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

    def render_ants(self, tile_size, screen, camera):
        if self.cache_groupes_a_updater:
            self.update_cache_groupes()

        for tuile, groupe in self.groupes_cache.items():
            if groupe.get_nb_fourmis() > 1:
                groupe.update(camera, tile_size)
                screen.blit(groupe.image, groupe.rect)
            elif not groupe.est_vide():
                f = groupe.fourmis[0]
                if f.in_colonie_map_coords is None:
                    sprite = self.sprite_dict[f]
                    sprite.update(pygame.time.get_ticks() / 1000, camera, tile_size)
                    if screen.get_rect().colliderect(sprite.rect):
                        #print("fourmi drawn outside")
                        screen.blit(sprite.image, sprite.rect)
                else:
                    sprite = self.sprite_dict[f]
                    sprite.update(pygame.time.get_ticks() / 1000, camera, tile_size)
                    if screen.get_rect().colliderect(sprite.rect):
                        screen.blit(sprite.image, sprite.rect)


    def handle_click(self, pos, tile_x, tile_y, screen):
        if self.map_data[tile_y][tile_x].fourmis is not None:
            occupants = self.map_data[tile_y][tile_x].fourmis
            if isinstance(occupants, Fourmis):
                if occupants == self.fourmis_selection:
                    self.fourmis_selection = None
                else:
                    self.fourmis_selection = occupants
                self.menu_f_a_updater = True
                return

            if isinstance(occupants, Groupe):
                if self.groupe_selection == occupants:
                    self.groupe_selection = None
                else:
                    self.groupe_selection = occupants
                    print("groupe select")

                self.menu_f_a_updater = True
                return

        if tile_x == self.tuile_debut[0] and tile_y == self.tuile_debut[1]:
            self.menu_colonie(screen)
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
        elif self.curr_tab == "Groupes":
            max_offset = max(0, self.get_vrai_nb_groupes() * 50 - 335)

        if self.menu_fourmis_rect.collidepoint(pos): # On scroll seulement si la souris est dans le rect du menu
            if dir == "up":
                self.scroll_offset = max(0, self.scroll_offset - self.scroll_speed)
            elif dir  == "down":
                self.scroll_offset = min(max_offset, self.scroll_offset + self.scroll_speed)
            self.scrolling = True
            self.menu_f_a_updater = True
            self.update_menu_fourmis()
        else: self.scrolling = False

class PrototypeIA:
    def __init__(self, root):
        self.root = root
        self.root.title("Prototype IA")

        self.colonie_ia = ColonieIA(0, (0, 0))

        # Creation de frames pour joueur et IA
        self.player_frame = tk.Frame(root)
        self.player_frame.pack(side="left", padx=10, pady=10)

        self.ai_frame = tk.Frame(root)
        self.ai_frame.pack(side="right", padx=10, pady=10)

        # Labels pour joueur et IA
        player_label = tk.Label(self.player_frame, text="Joueur", font=("Arial", 14))
        player_label.pack(pady=5)

        ai_label = tk.Label(self.ai_frame, text="IA", font=("Arial", 14))
        ai_label.pack(pady=5)

        # Inputs pour joueur
        self.player_inputs = {}
        self.create_input("Ouvrières:", "player_ouvr", self.player_inputs, self.player_frame)
        self.create_input("Soldats:", "player_sold", self.player_inputs, self.player_frame)
        self.create_input("Nourriture:", "player_nourr", self.player_inputs, self.player_frame)

        # Bouton pour mettre à jour l'IA
        self.update_button = tk.Button(root, text="Update IA", command=self.update_ai)
        self.update_button.pack(side="bottom", pady=10)

        # Label pour l'état de l'IA
        self.ai_state_label = tk.Label(root, text=f"État: {self.colonie_ia.state}", font=("Arial", 12))
        self.ai_state_label.pack(side="bottom", pady=10)

        # Meme input pour l'IA
        self.ai_inputs = {}
        self.create_input("Ouvrières:", "ai_ouvr", self.ai_inputs, self.ai_frame)
        self.create_input("Soldats:", "ai_sold", self.ai_inputs, self.ai_frame)
        self.create_input("Nourriture:", "ai_nourr", self.ai_inputs, self.ai_frame)



    def create_input(self, label_text, key, input_dict, frame):
        sub_frame = tk.Frame(frame)
        sub_frame.pack(pady=5)
        label = tk.Label(sub_frame, text=label_text)
        label.pack(side="left")
        entry = tk.Entry(sub_frame)
        entry.pack(side="right")
        input_dict[key] = entry

    def update_ai(self):
        player_data = {key: entry.get() or "0" for key, entry in self.player_inputs.items()}
        ia_data = {key: entry.get() or "0" for key, entry in self.ai_inputs.items()}

        self.colonie_ia.check_state_transition(player_data, ia_data)
        self.ai_state_label.config(text=f"État: {self.colonie_ia.state}")

class ColonieIA:
    def __init__(self, colony_id, position):
        self.colony_id = colony_id
        self.position = position
        self.state = "EXPLORATION"

    def check_state_transition(self, player_data, ia_data):
        if int(ia_data["ai_nourr"]) < int(ia_data["ai_ouvr"]) / 2:
            self.state = "COLLECTE"

        elif int(player_data["player_sold"]) > (int(ia_data["ai_sold"]) * 1.5):
            self.state = "DÉFENCE"

        elif int(player_data["player_nourr"]) != 0:
            if  int(player_data["player_ouvr"]) / int(player_data["player_nourr"]) < 5 or 1.25 < int(ia_data["ai_sold"]) / int(player_data["player_sold"]):
                self.state = "ATTAQUE"

        else:
            self.state = "EXPLORATION"


if __name__ == "__main__":
    root = tk.Tk()
    app = PrototypeIA(root)
    root.mainloop()
