import random
import tkinter as tk

import pygame

from Fourmis import Ouvriere, Soldat
from src.config import BLACK, trouver_font, WHITE


class Colonie:
    def __init__(self, tuile_debut, objets):
        self.tuile_debut = tuile_debut
        self.vie = 1 # 1 = 100% (vie de la reine)
        self.nourriture = 0

        self.objets = objets
        self.dans_objets = False
        self.ajouter()

        self.fourmis = [Ouvriere(self.tuile_debut[0], self.tuile_debut[1]) for _ in range(5)] + [Soldat(self.tuile_debut[0], self.tuile_debut[1]) for _ in range(2)]

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

    def menu_colonie(self, screen, tile_size):
        font = pygame.font.Font(trouver_font("LowresPixel-Regular.otf"), 20)
        surface_menu = pygame.Surface((300,500))
        surface_menu.fill(BLACK)

        y_offset = 40

        info_ouvr = f"Ouvrières ({self.nombre_ouvrieres()})"
        info_sold = f"Soldats ({self.nombre_soldats()})"
        info_vie = f"Vie: ({self.vie*100}%)"
        info_nourr = f"Nourriture: ({self.nourriture})"

        liste_textes = [info_ouvr, info_sold, info_vie, info_nourr]

        for texte in liste_textes:
            _texte = font.render(texte, True, WHITE)
            surface_menu.blit(_texte, (10, y_offset))
            y_offset += 40

        screen.blit(surface_menu, (1280-300,50))

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
