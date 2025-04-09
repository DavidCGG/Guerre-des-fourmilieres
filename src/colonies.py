import random
import tkinter as tk

import pygame
from pygame.examples.scroll import scroll_view

from Fourmis import Ouvriere, Soldat
from config import BLACK, trouver_font, WHITE, AQUA, trouver_img, GREEN
from Fourmis import FourmisSprite
from classes import Bouton


class Colonie:
    def __init__(self, tuile_debut, objets):
        self.sprite_sheet_ouvr = pygame.image.load(trouver_img("ouvriere_sheet.png")).convert_alpha()
        self.sprite_sheet_sold = pygame.image.load(trouver_img("4-frame-ant.png")).convert_alpha()

        self.tuile_debut = tuile_debut
        self.vie = 1 # 1 = 100% (vie de la reine)
        self.nourriture = 0

        self.objets = objets
        self.dans_objets = False
        self.ajouter()

        self.fourmis_selection = None
        self.last_fourmis_selection = None

        self.fourmis = [Ouvriere(self.tuile_debut[0], self.tuile_debut[1]) for _ in range(9)] + [Soldat(self.tuile_debut[0], self.tuile_debut[1]) for _ in range(2)]
        self.texte_rects = {}
        self.couleur_texte = WHITE
        self.hover_texte = None

        self.menu_fourmis_ouvert = False
        self.scrolling = False
        self.scroll_offset = 0
        self.scroll_speed = 10
        self.curr_tab = "Ouvrières"
        self.last_tab = self.curr_tab
        self.menu_fourmis_texte_rects = {}

        self.boutons = []

        self.menu_colonie_surface = pygame.Surface((250, 375))
        self.menu_fourmis_surface = pygame.Surface((250, 375))
        self.menu_a_updater = True
        self.menu_f_a_updater = True
        self.menu_fourmis_rect = pygame.Rect(0, 720 / 2 - self.menu_fourmis_surface.get_height() / 2, 250, 375)
        self.update_menu()
        self.update_menu_fourmis()


        self.sprites = pygame.sprite.Group()


    def process(self,dt,tile_size):
        for f in self.fourmis:
            f.process(dt, tile_size)

    def ajouter(self):
        if not any(isinstance(obj, Colonie) and obj.tuile_debut == self.tuile_debut for obj in self.objets):
            self.objets.append(self)
            self.dans_objets = True

    def nombre_ouvrieres(self):
        return len([f for f in self.fourmis if isinstance(f, Ouvriere)])

    def nombre_soldats(self):
        return len([f for f in self.fourmis if isinstance(f, Soldat)])

    def deplacer_fourmi(self):
        pass

    def update_menu(self):
        if not self.menu_a_updater:
            return

        font = pygame.font.Font(trouver_font("LowresPixel-Regular.otf"), 20)
        self.menu_colonie_surface.fill(BLACK)

        y_offset = 40
        info_ouvr = f"Ouvrières ({self.nombre_ouvrieres()})"
        info_sold = f"Soldats ({self.nombre_soldats()})"
        info_vie = f"Vie: {self.vie * 100}%"
        info_nourr = f"Nourriture: {self.nourriture}"

        menu_x = 1280 - self.menu_colonie_surface.get_width()
        menu_y = 720 / 2 - self.menu_colonie_surface.get_height() / 2

        liste_textes = [info_ouvr, info_sold, info_vie, info_nourr]

        for texte in liste_textes:
            couleur = AQUA if texte.split()[0] == self.hover_texte else WHITE
            _texte = font.render(texte, True, couleur)
            _texte_rect = _texte.get_rect(
                center=(self.menu_colonie_surface.get_width() / 2, y_offset + _texte.get_height() / 2))
            self.menu_colonie_surface.blit(_texte, (
            self.menu_colonie_surface.get_width() / 2 - _texte.get_width() / 2, y_offset))
            if texte.startswith("Ouvrières") or texte.startswith("Soldats"):
                self.texte_rects[texte.split()[0]] = _texte_rect.move(menu_x, menu_y)
            y_offset += 40
        self.menu_a_updater = False
    def update_menu_fourmis(self):
        if not self.menu_f_a_updater:
            return

        font = pygame.font.Font(trouver_font("LowresPixel-Regular.otf"), 20)
        self.menu_fourmis_surface.fill(BLACK)

        y_offset = 40

        mouse_x, mouse_y = pygame.mouse.get_pos()
        rel_x = mouse_x - self.menu_fourmis_rect.x
        rel_y = mouse_y - self.menu_fourmis_rect.y + self.scroll_offset

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
            fourmi.scale = 2
            sprite = FourmisSprite(fourmi, sprite_sheet, 16, 16, 4, 300).extract_frames()[0]

            list_surface.blit(sprite, (10, y_offset - 5))
            ant_info = f"HP: {fourmi.hp} Pos: ({fourmi.centre_x}, {fourmi.centre_y})"
            _texte = font.render(ant_info, True, WHITE)
            list_surface.blit(_texte, (50, y_offset))

            rect = pygame.Rect(0, y_offset - 5, 250, 50)
            if self.fourmis_selection == fourmi:
                pygame.draw.rect(list_surface, GREEN, rect, 2)

            # elif rect.collidepoint((rel_x, rel_y)):
            #     pygame.draw.rect(list_surface, AQUA, rect, 2)

            y_offset += 50

        self.menu_fourmis_surface.blit(list_surface, (0, -self.scroll_offset))
        self.menu_f_a_updater = False


    def menu_colonie(self, screen):
        if not self.menu_fourmis_ouvert:
            self.update_menu()

        if self.menu_colonie_surface is not None:
            screen.blit(self.menu_colonie_surface, (1280 - self.menu_colonie_surface.get_width(), 720 / 2 - self.menu_colonie_surface.get_height() / 2))

    def menu_fourmis(self, screen):
        self.update_menu_fourmis()

        if self.menu_fourmis_surface is not None and self.menu_fourmis_ouvert:
            screen.blit(self.menu_fourmis_surface, (0, 720 / 2 - self.menu_fourmis_surface.get_height() / 2))




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
                if not self.menu_fourmis_ouvert:
                    self.objets.clear()
                self.menu_a_updater = True
                self.menu_f_a_updater = True
                return

        if self.menu_fourmis_ouvert and self.menu_fourmis_rect.collidepoint(pos):
            rel_x = pos[0] - self.menu_fourmis_rect.x
            rel_y = pos[1] - self.menu_fourmis_rect.y + self.scroll_offset

            y_offset = 40
            for fourmi in self.fourmis:
                rect = pygame.Rect(0, y_offset - 5, 250, 50)

                if rect.collidepoint((rel_x, rel_y)):
                    if self.fourmis_selection == fourmi:
                        self.fourmis_selection = None

                    else:
                        self.fourmis_selection = fourmi

                    self.menu_f_a_updater = True
                    print(self.fourmis_selection)
                    return

                y_offset += 50



    def handle_hover(self, pos):
        for key, rect in self.texte_rects.items():
            if rect.collidepoint(pos):
                self.hover_texte = key
                self.menu_a_updater = True
                return

        if self.menu_fourmis_rect.collidepoint(pos):

            self.scrolling = True
            self.menu_f_a_updater = True


        else:
            self.scrolling = False
            self.objets.clear()


        self.hover_texte = None


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

            self.menu_f_a_updater = True
            self.update_menu_fourmis()

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
