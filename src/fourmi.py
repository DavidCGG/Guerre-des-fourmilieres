import math
import random
import uuid
from abc import ABC, abstractmethod
from enum import Enum

import pygame
from config import SCREEN_WIDTH, SCREEN_HEIGHT
from src.config import trouver_img
from tuile import Tuile, Eau

class FourmiTitleScreen():
    def __init__(self, x0, y0, scale=1.0):
        self.width = 16
        self.height = 16
        self.scale = scale

        self.centre_y = y0
        self.centre_x = x0

        self.target_x = x0
        self.target_y = y0
        self.speed = 5 * self.scale

        self.moving = False
        self.facing = 0 # 0 : droite, 1 : gauche
        self.pause_timer = 0

    def random_mouvement(self, dt):
        if self.pause_timer > 0:
            self.pause_timer -= dt
            return

        if self.centre_x == self.target_x and self.centre_y == self.target_y:
            self.set_nouv_target()
            self.pause_timer = random.uniform(0, 1.5) * 1000

        else:
            self.goto_target(dt)

    def set_nouv_target(self):
        angle = random.uniform(0, 2*math.pi)
        distance = random.uniform(40, 150)

        self.target_x = self.centre_x + distance*math.cos(angle)
        self.target_y = self.centre_y + distance*math.sin(angle)

        # On s'assure que la cible est dans les limites de l'écran
        self.target_x = max(0+self.width * self.scale, min(SCREEN_WIDTH-self.width * self.scale, self.target_x))
        self.target_y = max(0+self.height * self.scale, min(SCREEN_HEIGHT-self.height * self.scale, self.target_y))

    def goto_target(self, dt):
            dx = self.target_x - self.centre_x
            dy = self.target_y - self.centre_y
            distance = math.sqrt(dx ** 2 + dy ** 2)

            if distance > 0.5:
                self.centre_x += self.speed * dx / distance * (dt / 1000)
                self.centre_y += self.speed * dy / distance * (dt / 1000)

                self.moving = True
                self.facing = 0 if dx > 0 else 1

            else:
                self.centre_x = self.target_x
                self.centre_y = self.target_y

                self.moving = False


class FourmiTitleScreenSprite(pygame.sprite.Sprite):
    def __init__(self, fourmi: FourmiTitleScreen, spritesheet, frame_width, frame_height, num_frames: int, frame_duration: int):
        super().__init__()
        self.fourmi = fourmi
        self.spritesheet = spritesheet
        self.frame_width = frame_width
        self.frame_height = frame_height
        self.num_frames = num_frames
        self.frame_duration = frame_duration
        self.current_frame = 0
        self.timer = 0
        self.frames_LEFT = self.extract_frames()
        self.frames_RIGHT = self.extract_frames(flipped=True)
        self.image = self.frames_LEFT[self.current_frame]
        self.rect = self.image.get_rect(center=(fourmi.centre_x, fourmi.centre_y))

    def extract_frames(self, flipped=False):
        frames = []
        frame = None
        for i in range(self.num_frames):
            frame = self.spritesheet.subsurface(pygame.Rect(i*self.frame_width, 0, self.frame_width, self.frame_height))

            if flipped:
                frame = pygame.transform.flip(frame, True, False)
            frames.append(frame)

        self.fourmi.width = frame.get_width()
        self.fourmi.height = frame.get_height()
        return frames


    def update(self, dt):
        if self.fourmi.moving:
            self.timer += dt

            while self.timer > self.frame_duration:
                self.timer -= self.frame_duration
                self.current_frame = (self.current_frame + 1) % self.num_frames

        if self.fourmi.facing == 0:
            self.image = self.frames_RIGHT[self.current_frame]
        else:
            self.image = self.frames_LEFT[self.current_frame]

        width = int(self.image.get_width() * self.fourmi.scale)
        height = int(self.image.get_height() * self.fourmi.scale)
        self.image = pygame.transform.scale(self.image, (width, height))
        self.rect = self.image.get_rect(center=(self.fourmi.centre_x + width/2, self.fourmi.centre_y + height/2))

class CouleurFourmi(Enum):
    NOIRE = (trouver_img("fourmi_noire.png"))
    ROUGE = (trouver_img("fourmi_rouge.png"))

class Fourmis(ABC):
    def __init__(self, hp: int, atk: int, x0, y0, size, couleur):
        super().__init__()
        self.centre_y = y0
        self.centre_x = x0
        self.target_x = x0
        self.target_y = y0
        self.base_speed = 2
        self.speed = self.base_speed
        self.path = None
        self.moving = False
        self.facing = 0 # 0 : droite, 1 : gauche
        self.hp = hp
        self.atk = atk
        self.width = 0
        self.height = 0
        self.pause_timer = 0
        self.tient_ressource = None
        self.size = size
        self.couleur = couleur
        self.image = pygame.image.load(self.couleur.value)
        self.image = pygame.transform.scale(self.image,(self.image.get_width() * self.size, self.image.get_height() * self.size))

    @abstractmethod
    def attack(self, other):
        pass

    def depot(self):
        if self.tient_ressource is not None:
            return self.tient_ressource

        return

    def process(self, dt, map_data):
        #print("Pos:"+str(self.centre_x)+", "+str(self.centre_y))
        if self.target_x != self.centre_x or self.target_y != self.centre_y:
            self.goto_target(dt, map_data)

    def set_target(self, target_x, target_y, map_data):
        if isinstance(map_data[target_y][target_x], Eau):
            return
        
        self.target_x = target_x
        self.target_y = target_y

    def goto_target(self, dt, map_data):
        if not self.path:
            # Calculate path if not already calculated
            self.path = self.a_star(map_data)

        if self.path:
            next_tile = self.path[0]
            target_x = next_tile[0]
            target_y = next_tile[1]

            dx = target_x - self.centre_x
            dy = target_y - self.centre_y
            distance = math.sqrt(dx ** 2 + dy ** 2)

            if distance > 0.1:
                self.centre_x += self.speed * dx / distance * (dt / 1000)
                self.centre_y += self.speed * dy / distance * (dt / 1000)
                self.moving = True

                self.facing = 0 if dx > 0 else 1
            else:
                # Reached the next tile
                self.centre_x = target_x
                self.centre_y = target_y
                self.path.pop(0)  # Remove the reached tile
                self.moving = len(self.path) > 0

        else:
            self.moving = False
    
    def a_star(self, map_data):
        #Note: le path retourné contient des tuiles et non des coordonnées
        def sort_queue(arr):
            if len(arr) <= 1:
                return arr

            mid = len(arr) // 2
            left_half = sort_queue(arr[:mid])
            right_half = sort_queue(arr[mid:])

            return merge(left_half, right_half)

        def merge(left, right):
            sorted_arr = []
            i, j = 0, 0

            while i < len(left) and j < len(right):
                if distance_geo[left[i]] + distance_trajet[left[i]] < distance_geo[right[j]] + distance_trajet[right[j]]:
                    sorted_arr.append(left[i])
                    i += 1
                else:
                    sorted_arr.append(right[j])
                    j += 1

            sorted_arr.extend(left[i:])
            sorted_arr.extend(right[j:])
            
            return sorted_arr
        
        def get_voisins(tuile):
            directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]  # Gauche, Droite, Haut, Bas
            voisins = [] #liste des tuiles adjacentes qui ne sont pas de l'eau

            for dx, dy in directions:
                nx, ny = tuile.x + dx, tuile.y + dy
                if 0 <= nx < len(map_data[0]) and 0 <= ny < len(map_data):
                    voisin = map_data[ny][nx]
                    if not isinstance(voisin, Eau):
                        voisins.append(voisin)

            return voisins

        def calculate_distance(tuile1, tuile2):
            x1 = tuile1.x
            y1 = tuile1.y
            x2 = tuile2.x
            y2 = tuile2.y
            return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
        

        depart = map_data[self.get_tuile()[1]][self.get_tuile()[0]]
        arrivee = map_data[self.target_y][self.target_x]

        queue: list[Tuile] = [] #queue qui permet de savoir quel noeud visiter
        distance_trajet: dict[Tuile : int] = dict() #nb de noeud à parcourir pour arriver à ce noeud
        distance_geo: dict[Tuile : int] = dict() #distance géométrique entre le noeud et la destination {tuile: distance}
        previous: dict[Tuile : Tuile] = dict() #noeud par lequel on est arrivé à ce noeud
        visited: set[Tuile] = set() #noeuds dont tous les voisins ont été visités

        queue.append(depart)
        distance_trajet[depart] = 0
        distance_geo[depart] = calculate_distance(depart, arrivee)
        previous[depart] = None
        
        #Naviguation
        while queue[0] != arrivee:
            sort_queue(queue)
            current: Tuile = queue[0]

            for v in get_voisins(current):
                if v in visited:
                    continue

                if v not in queue:
                    queue.append(v)
                    distance_trajet[v] = distance_trajet[current] + 1
                    distance_geo[v] = calculate_distance(v, arrivee)
                    previous[v] = current
                    continue

                elif distance_trajet[current] + 1 < distance_trajet[v]:
                    distance_trajet[v] = distance_trajet[current] + 1
                    previous[v] = current
            
            visited.add(current)
            queue.pop(0)

        #Reconstruction du chemin
        chemin: list[tuple[int, int]] = [] #le chemin pris pour arriver à la fin
        current = arrivee

        while current != None:
            chemin.append((current.x, current.y))
            current = previous[current]

        chemin.reverse()
        return chemin

    def get_tuile(self):
        return int(self.centre_x), int(self.centre_y)

class Ouvriere(Fourmis):
    def __init__(self, x0, y0, couleur):
        super().__init__(hp=10, atk=2, x0=x0, y0=y0, size=2,couleur=couleur)
        self.base_speed = 3
        self.speed = self.base_speed


    def attack(self, other):
        other.hp -= self.atk

class Soldat(Fourmis):
    def __init__(self, x0, y0, couleur):
        super().__init__(hp=25, atk=5, x0=x0, y0=y0, size=2,couleur=couleur)
        self.base_speed = 1.5
        self.speed = self.base_speed

    def attack(self, other):
        other.hp -= self.atk

class FourmisSprite(pygame.sprite.Sprite):
    def __init__(self, fourmis: Fourmis, spritesheet, frame_width, frame_height, num_frames: int, frame_duration: int):
        super().__init__()
        self.fourmis = fourmis
        self.spritesheet = spritesheet
        self.frame_width = frame_width
        self.frame_height = frame_height
        self.num_frames = num_frames
        self.frame_duration = frame_duration
        self.current_frame = 0
        self.timer = 0
        self.frames_LEFT = self.extract_frames()
        self.frames_RIGHT = self.extract_frames(flipped=True)
        self.image = self.frames_LEFT[self.current_frame]
        self.rect = self.image.get_rect(center=(fourmis.centre_x, fourmis.centre_y))

    def extract_frames(self, flipped=False):
        frames = []
        frame = None
        for i in range(self.num_frames):
            frame = self.spritesheet.subsurface(pygame.Rect(i*self.frame_width, 0, self.frame_width, self.frame_height))

            if flipped:
                frame = pygame.transform.flip(frame, True, False)
            frames.append(frame)

        self.fourmis.width = frame.get_width()
        self.fourmis.height = frame.get_height()
        return frames


    def update(self, dt, camera, tile_size):
        if self.fourmis.moving:
            self.timer += dt

            while self.timer > self.frame_duration:
                self.timer -= self.frame_duration
                self.current_frame = (self.current_frame + 1) % self.num_frames
        if self.fourmis.facing == 0:
            self.image = self.frames_RIGHT[self.current_frame]
        else:
            self.image = self.frames_LEFT[self.current_frame]

        zoom = camera.zoom
        scaled_width = int(self.image.get_width() * zoom * 2)
        scaled_height = int(self.image.get_height() * zoom * 2)
        self.image = pygame.transform.scale(self.image, (scaled_width, scaled_height))

        world_x = self.fourmis.centre_x * tile_size
        world_y = self.fourmis.centre_y * tile_size

        self.rect = self.image.get_rect(center=(world_x+scaled_width/2, world_y+scaled_height/2))
        self.rect = camera.apply_rect(self.rect)

class Groupe:
    def __init__(self, tile_x, tile_y, images):
        self.id = str(uuid.uuid4())
        self.fourmis = []
        self.max_capacite = 5
        self.images = images
        self.image = self.images[0]
        self.speed = 2
        self.centre_x = tile_x
        self.centre_y = tile_y
        self.target_x = self.centre_x
        self.target_y = self.centre_y
        self.rect = self.image.get_rect(center=(self.centre_x, self.centre_y))
        self.moving = False
        self.path = None
        self.indexe_fourmis = 0 # indexe de la fourmi qui va collecter la ressource

    def process(self, dt):
        dern_x, dern_y = self.centre_x, self.centre_y

        if self.target_x != self.centre_x or self.target_y != self.centre_y:
            self.goto_target(dt)

            if (dern_x, dern_y) != (self.centre_x, self.centre_y):
                for f in self.fourmis:
                    f.centre_x = self.centre_x
                    f.centre_y = self.centre_y

    def set_target(self, target_x, target_y):
        self.target_x = target_x
        self.target_y = target_y

    def goto_target(self, dt):
        if not self.path:
            # Calculate path if not already calculated
            self.path = self.calculate_path()

        if self.path:
            next_tile = self.path[0]
            target_x = next_tile[0]
            target_y = next_tile[1]

            dx = target_x - self.centre_x
            dy = target_y - self.centre_y
            distance = math.sqrt(dx ** 2 + dy ** 2)

            if distance > 0.1:
                self.centre_x += self.speed * dx / distance * (dt / 1000)
                self.centre_y += self.speed * dy / distance * (dt / 1000)
                self.moving = True

            else:
                # Reached the next tile
                self.centre_x = target_x
                self.centre_y = target_y
                self.path.pop(0)  # Remove the reached tile
                self.moving = len(self.path) > 0


        else:
            self.moving = False


    def calculate_path(self):
        start_tile = self.get_tuile()

        target_tile = (self.target_x, self.target_y)

        # Example: Simple straight-line path (replace with A* for complex maps)
        path = []
        x, y = start_tile
        while (x, y) != target_tile:
            if x < target_tile[0]:
                x += 1
            elif x > target_tile[0]:
                x -= 1
            elif y < target_tile[1]:
                y += 1
            elif y > target_tile[1]:
                y -= 1
            path.append((x, y))

        return path

    def get_tuile(self):
        return int(self.centre_x), int(self.centre_y)

    def update(self, camera, tile_size):
        match self.get_nb_fourmis():
            case 2:
                self.image = self.images[0]
            case 3:
                self.image = self.images[1]
            case 4:
                self.image = self.images[2]
            case 5:
                self.image = self.images[3]

        zoom = camera.zoom
        scaled_width = int(self.image.get_width() * zoom * 2)
        scaled_height = int(self.image.get_height() * zoom * 2)
        self.image = pygame.transform.scale(self.image, (scaled_width, scaled_height))

        world_x = self.centre_x * tile_size
        world_y = self.centre_y * tile_size

        self.rect = self.image.get_rect(center=(world_x + scaled_width / 2, world_y + scaled_height / 2))
        self.rect = camera.apply_rect(self.rect)


    def ajouter_fourmis(self, fourmis):
        if self.get_size() + fourmis.size <= self.max_capacite:
            self.fourmis.append(fourmis)
        return


    def enlever_fourmis(self, fourmis):
        if fourmis in self.fourmis:
            self.fourmis.remove(fourmis)
        else: print("fourmi pas dans le groupe")

    def collecter_ressource(self, ressource) -> bool:
        if self.indexe_fourmis < len(self.fourmis):
            if self.fourmis[self.indexe_fourmis].tient_ressource is None:
                self.fourmis[self.indexe_fourmis].tient_ressource = ressource
                self.indexe_fourmis += 1
                return True
        return False

    def deposer_ressources(self):
        metal = 0
        nourr = 0
        for fourmi in self.fourmis:
            if fourmi.tient_ressource == "metal":
                metal += 1
            elif fourmi.tient_ressource == "pomme":
                nourr += 1
            fourmi.tient_ressource = None
        self.indexe_fourmis = 0
        return nourr, metal

    def get_size(self):
        tot = 0
        for fourmi in self.fourmis:
            tot += fourmi.size
        return tot

    def get_nb_fourmis(self):
        return len(self.fourmis)

    def est_vide(self):
        return len(self.fourmis) == 0