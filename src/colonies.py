import random
import tkinter as tk

import pygame

from Fourmis import Ouvriere, Soldat
from config import BLACK, trouver_font, WHITE, AQUA


class Colonie:
    def __init__(self, tuile_debut, objets):
        self.tuile_debut = tuile_debut
        self.vie = 1 # 1 = 100% (vie de la reine)
        self.nourriture = 0

        self.objets = objets
        self.dans_objets = False
        self.ajouter()

        self.fourmis = [Ouvriere(self.tuile_debut[0], self.tuile_debut[1]) for _ in range(5)] + [Soldat(self.tuile_debut[0], self.tuile_debut[1]) for _ in range(2)]
        self.texte_rects = {}
        self.couleur_texte = WHITE
        self.hover_texte = None

        self.menu_surface = None
        self.update_menu()





    def process(self):
        for f in self.fourmis:
            f.process()

    def ajouter(self):
        if not any(isinstance(obj, Colonie) and obj.tuile_debut == self.tuile_debut for obj in self.objets):
            self.objets.append(self)
            self.dans_objets = True

    def nombre_ouvrieres(self):
        return len([f for f in self.fourmis if isinstance(f, Ouvriere)])

    def nombre_soldats(self):
        return len([f for f in self.fourmis if isinstance(f, Soldat)])

    def menu_fourmis(self, screen, type_fourmis, pos):
        pass

    def update_menu(self):
        font = pygame.font.Font(trouver_font("LowresPixel-Regular.otf"), 20)
        self.menu_surface = pygame.Surface((250, 375))
        self.menu_surface.fill(BLACK)

        y_offset = 40
        info_ouvr = f"Ouvrières ({self.nombre_ouvrieres()})"
        info_sold = f"Soldats ({self.nombre_soldats()})"
        info_vie = f"Vie: {self.vie * 100}%"
        info_nourr = f"Nourriture: {self.nourriture}"

        menu_x = 1280 - self.menu_surface.get_width()
        menu_y = 720 / 2 - self.menu_surface.get_height() / 2

        liste_textes = [info_ouvr, info_sold, info_vie, info_nourr]

        for texte in liste_textes:
            couleur = AQUA if texte.split()[0] == self.hover_texte else WHITE
            _texte = font.render(texte, True, couleur)
            _texte_rect = _texte.get_rect(center=(self.menu_surface.get_width() / 2, y_offset + _texte.get_height() / 2))
            self.menu_surface.blit(_texte, (self.menu_surface.get_width() / 2 - _texte.get_width() / 2, y_offset))
            if texte.startswith("Ouvrières") or texte.startswith("Soldats"):
                self.texte_rects[texte.split()[0]] = _texte_rect.move(menu_x, menu_y)
            y_offset += 40

    def menu_colonie(self, screen):
        self.update_menu()
        if self.menu_surface is not None:

            screen.blit(self.menu_surface, (1280 - self.menu_surface.get_width(), 720 / 2 - self.menu_surface.get_height() / 2))

    def handle_click(self, pos, tile_x, tile_y, screen):
        if tile_x == self.tuile_debut[0] and tile_y == self.tuile_debut[1]:
            print(self.menu_surface is None)
            self.menu_colonie(screen)
            return

        for key, rect in self.texte_rects.items():
            if rect.collidepoint(pos):
                self.couleur_texte = AQUA
                self.update_menu()
                return


    def handle_hover(self, pos):
        for key, rect in self.texte_rects.items():
            if rect.collidepoint(pos):
                self.hover_texte = key
                self.update_menu()
                return
        self.hover_texte = None
        self.update_menu()

class AIColony:
    def __init__(self, colony_id, position):
        self.colony_id = colony_id
        self.position = position
        self.state = "EXPANDING"
        self.food = 100
        self.worker_ants = 5
        self.soldier_ants = 2

    def check_state_transition(self, player_data):
        """Decide when to change state based on player input."""
        if self.food < 50:
            self.state = "GATHERING"
        elif int(player_data["soldiers"]) > self.soldier_ants:
            self.state = "DEFENDING"
        elif self.should_attack(player_data):
            self.state = "ATTACKING"
        else:
            self.state = "EXPANDING"

    def should_attack(self, player_data):
        """Decide to attack if the player is weak."""
        return int(player_data["soldiers"]) < self.soldier_ants


class AIPrototypeApp:
    def __init__(self, root):
        self.root = root
        self.root.title("AI Colony Prototype")

        # Create three AI colonies
        self.ai_colonies = [
            AIColony(colony_id=1, position=(0, 0)),
            AIColony(colony_id=2, position=(5, 5)),
            AIColony(colony_id=3, position=(10, 10))
        ]

        # Input fields for player colony data
        self.inputs = {}
        self.create_input("Workers:", "workers")
        self.create_input("Soldiers:", "soldiers")
        self.create_input("Owned Tiles:", "tiles")
        self.create_input("Ant Gen (per 10s):", "ant_gen")
        self.create_input("Food Gen (per 5s):", "food_gen")

        # Button to update AI state
        self.update_button = tk.Button(root, text="Update AI", command=self.update_ai)
        self.update_button.pack()

        # AI State Displays
        self.ai_state_labels = []
        for i in range(3):
            label = tk.Label(root, text=f"AI Colony {i + 1} State: {self.ai_colonies[i].state}", font=("Arial", 12))
            label.pack()
            self.ai_state_labels.append(label)

    def create_input(self, label_text, key):
        """Creates a labeled input field."""
        frame = tk.Frame(self.root)
        frame.pack()
        label = tk.Label(frame, text=label_text)
        label.pack(side="left")
        entry = tk.Entry(frame)
        entry.pack(side="right")
        self.inputs[key] = entry  # Store reference to input field

    def update_ai(self):
        """Update AI states based on player inputs and display new states."""
        player_data = {key: entry.get() or "0" for key, entry in self.inputs.items()}

        for i, ai_colony in enumerate(self.ai_colonies):
            ai_colony.check_state_transition(player_data)
            self.ai_state_labels[i].config(text=f"AI Colony {i + 1} State: {ai_colony.state}")


# Run the Tkinter app
# root = tk.Tk()
# app = AIPrototypeApp(root)
# root.mainloop()
