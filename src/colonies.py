import random
import tkinter as tk

import pygame
from pygame.examples.scroll import scroll_view

from Fourmis import Ouvriere, Soldat, Groupe
from config import BLACK, trouver_font, WHITE, AQUA, trouver_img, GREEN
from Fourmis import FourmisSprite
from classes import Bouton


class Colonie:
    def __init__(self, tuile_debut, map_data):
        self.sprite_sheet_ouvr = pygame.image.load(trouver_img("ouvriere_sheet.png")).convert_alpha()
        self.sprite_sheet_sold = pygame.image.load(trouver_img("4-frame-ant.png")).convert_alpha()
        self.map_data = map_data # la carte de jeu
        self.tuile_debut = tuile_debut
        self.vie = 1 # 1 = 100% (vie de la reine)
        self.nourriture = 0
        self.metal = 0

        self.fourmis_selection = None # fourmi selectionnée dans le menu de fourmis

        self.fourmis = [Ouvriere(self.tuile_debut[0], self.tuile_debut[1]) for _ in range(9)] + [Soldat(self.tuile_debut[0], self.tuile_debut[1]) for _ in range(2)]
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


    def process(self,dt):
        fourmis_bouge = False
        for f in self.fourmis:
            dern_tuile = f.get_tuile()
            f.process(dt)
            if f.get_tuile() != dern_tuile:
                fourmis_bouge = True

        if fourmis_bouge:
            self.cache_groupes_a_updater = True
            if self.menu_fourmis_ouvert:
                self.menu_f_a_updater = True

    def nombre_ouvrieres(self):
        return len([f for f in self.fourmis if isinstance(f, Ouvriere)])

    def nombre_soldats(self):
        return len([f for f in self.fourmis if isinstance(f, Soldat)])


    def update_menu(self):
        if not self.menu_a_updater or not self.menu_colonie_ouvert:
            return
        self.menu_colonie_surface.fill(BLACK)

        y_offset = 40
        info_ouvr = f"Ouvrières ({self.nombre_ouvrieres()})"
        info_sold = f"Soldats ({self.nombre_soldats()})"
        info_vie = f"Vie: {self.vie * 100}%"
        info_nourr = f"Nourriture: {self.nourriture}"
        info_metal = f"Métal: {self.metal}"

        menu_x = 1280 - self.menu_colonie_surface.get_width()
        menu_y = 720 / 2 - self.menu_colonie_surface.get_height() / 2

        liste_textes = [info_ouvr, info_sold, info_vie, info_nourr, info_metal]

        for texte in liste_textes:
            couleur = AQUA if texte.split()[0] == self.hover_texte else WHITE
            _texte = self.font_menu.render(texte, True, couleur)
            _texte_rect = _texte.get_rect(
                center=(self.menu_colonie_surface.get_width() / 2, y_offset + _texte.get_height() / 2))
            self.menu_colonie_surface.blit(_texte, (
            self.menu_colonie_surface.get_width() / 2 - _texte.get_width() / 2, y_offset))
            if texte.startswith("Ouvrières") or texte.startswith("Soldats"):
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

            sprite = FourmisSprite(fourmi, sprite_sheet, 16, 16, 4, 500).extract_frames()[0]
            sprite = pygame.transform.scale(sprite, (32, 32))
            list_surface.blit(sprite, (10, y_offset - 10))
            ant_info = f"HP: {fourmi.hp} Pos: ({int(fourmi.centre_x)}, {int(fourmi.centre_y)})"
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
        self.update_menu()
        screen.blit(self.menu_colonie_surface, (1280 - self.menu_colonie_surface.get_width(), 720 / 2 - self.menu_colonie_surface.get_height() / 2))

    def menu_fourmis(self, screen):
        self.update_menu_fourmis()
        screen.blit(self.menu_fourmis_surface, (0, 720 / 2 - self.menu_fourmis_surface.get_height() / 2))


    def load_sprites(self):
        for f in self.fourmis:
            sprite = FourmisSprite(f, self.sprite_sheets[type(f)], 16, 16, 4, 300)
            self.sprite_dict[f] = sprite
            self.sprites.append(sprite)

    def update_cache_groupes(self):
        dern_positions = {}
        for tuile, groupe in self.groupes_cache.items():
            for f in groupe.fourmis:
                dern_positions[f] = tuile

        nouv_groupe = {}
        for f in self.fourmis:
            tuile = f.get_tuile()
            if tuile not in nouv_groupe:
                nouv_groupe[tuile] = Groupe(tuile[0], tuile[1], self.groupe_images)
            nouv_groupe[tuile].ajouter_fourmis(f)

        modif_tuiles = set()
        for f in self.fourmis:
            if f in dern_positions and dern_positions[f] != (int(f.centre_x), int(f.centre_y)):
                modif_tuiles.add(dern_positions[f])
                modif_tuiles.add((int(f.centre_x), int(f.centre_y)))

        self.groupes_cache = nouv_groupe
        self.cache_groupes_a_updater = False

        self.update_fourmis_tuiles(modif_tuiles)


    def update_fourmis_tuiles(self, modif_tuiles):
        if modif_tuiles is None:
            for y in self.map_data:
                for tuile in y:
                    tuile.fourmis = []

            for tuile, groupe in self.groupes_cache.items():
                self.map_data[tuile[1]][tuile[0]].fourmis = groupe
        else:
            for tuile in modif_tuiles:
                self.map_data[tuile[1]][tuile[0]].fourmis = []
            for tuile, groupe in self.groupes_cache.items():
                if tuile in modif_tuiles:
                    self.map_data[tuile[1]][tuile[0]].fourmis = groupe
        
    def ajouter_fourmis_tuile(self):
        for tuile, groupe in self.groupes_cache.items():
            self.map_data[tuile[1]][tuile[0]].fourmis = groupe

    def load_groupe_images(self):
        for x in range(2,6):
            self.groupe_images.append(pygame.image.load(trouver_img(f"numero-{x}.png")))

    def render_ants(self, tile_size, screen, camera):
        if self.cache_groupes_a_updater:
            self.update_cache_groupes()

        for tuile, groupe in self.groupes_cache.items():
            if groupe.get_nb_fourmis() > 1:
                groupe.update(camera, tile_size)
                screen.blit(groupe.image, groupe.rect)
            else:
                f = groupe.fourmis[0]
                sprite = self.sprite_dict[f]
                sprite.update(pygame.time.get_ticks() / 1000, camera, tile_size)
                if screen.get_rect().colliderect(sprite.rect):
                    screen.blit(sprite.image, sprite.rect)


    def handle_click(self, pos, tile_x, tile_y, screen):
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
            else:
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
