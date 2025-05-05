import math
import random
import uuid
from abc import ABC, abstractmethod
from curses.textpad import rectangle
from enum import Enum

import pygame
from pygame import Vector2

#from config import SCREEN_WIDTH, SCREEN_HEIGHT
from config import trouver_img, AQUA, BLACK, BROWN
from src.config import GREEN, TypeItem
from tuile import Tuile, Eau

class FourmiTitleScreen():
    def __init__(self, x0, y0, screen, scale=1.0):
        self.width = 16
        self.height = 16
        self.scale = scale

        self.centre_y = y0
        self.centre_x = x0

        self.target_x = x0
        self.target_y = y0
        self.speed = 5 * self.scale

        self.is_moving = False
        self.facing = 0 # 0 : droite, 1 : gauche
        self.pause_timer = 0
        self.screen=screen

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
        self.target_x = max(0+self.width * self.scale, min(self.screen.get_width()-self.width * self.scale, self.target_x))
        self.target_y = max(0+self.height * self.scale, min(self.screen.get_height()-self.height * self.scale, self.target_y))

    def goto_target(self, dt):
            dx = self.target_x - self.centre_x
            dy = self.target_y - self.centre_y
            distance = math.sqrt(dx ** 2 + dy ** 2)

            if distance > 0.5:
                self.centre_x += self.speed * dx / distance * (dt / 1000)
                self.centre_y += self.speed * dy / distance * (dt / 1000)

                self.is_moving = True
                self.facing = 0 if dx > 0 else 1

            else:
                self.centre_x = self.target_x
                self.centre_y = self.target_y

                self.is_moving = False


class FourmiTitleScreenSprite(pygame.sprite.Sprite):
    def __init__(self, fourmi: FourmiTitleScreen, spritesheet, frame_width, frame_height, num_frames: int, frame_duration: int):
        super().__init__()
        self.fourmi = fourmi
        self.spritesheet = pygame.transform.flip(spritesheet,True,False)
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
        if self.fourmi.is_moving:
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
    NOIRE = (trouver_img("Fourmis/fourmi_noire.png"))
    ROUGE = (trouver_img("Fourmis/fourmi_rouge.png"))

class Fourmis(ABC):
    def __init__(self, colonie_origine, hp: int, atk: int, x0, y0, size, couleur):
        super().__init__()
        self.centre_y_in_map = None
        self.centre_x_in_map = None
        self.target_x_in_map = None
        self.target_y_in_map = None
        #self.centre_x_in_nid = 0
        #self.centre_y_in_nid = 0
        self.target_x_in_nid = None
        self.target_y_in_nid = None
        for salle in colonie_origine.graphe.salles:
            if salle.type.value[1]=="throne":
                self.centre_x_in_nid = salle.noeud.coord[0]
                self.centre_y_in_nid = salle.noeud.coord[1]
        self.base_speed = 2
        self.speed = self.base_speed
        self.path = None
        self.is_moving = False
        self.facing = 0 # 0 : droite, 1 : gauche
        self.hp = hp
        self.atk = atk
        self.width = 0
        self.height = 0
        self.pause_timer = 0
        self.inventaire: list[TypeItem] = []
        self.inventaire_taille_max = 1
        self.size = size
        self.couleur = couleur
        self.image = pygame.image.load(self.couleur.value)
        self.image = pygame.transform.scale(self.image,(self.image.get_width() * self.size, self.image.get_height() * self.size))
        self.is_busy = False
        self.colonie_origine = colonie_origine
        self.in_colonie_map_coords = colonie_origine.tuile_debut
        self.a_bouger_depuis_transition_map_ou_nid=True

        #self.image = pygame.image.load(trouver_img("Test64x64.png")).convert_alpha()
        self.image_armure = pygame.image.load(trouver_img("Items/epee.png"))

        self.sprite: FourmisSprite
        self.type = "default"
        self.menu_is_ouvert: bool = True
        self.is_selected: bool = False

        self.menu: pygame.Surface=pygame.Surface((100,100))

    @abstractmethod
    def attack(self, other):
        pass

    def process(self, dt, map_data,tuiles_debut_toutes_colonies,tous_les_nids):
        #print("Map Pos:" + str(self.centre_x_in_map) + ", " + str(self.centre_y_in_map))
        #print("Map Target: " + str(self.target_x_in_map) + ", " + str(self.target_y_in_map))
        #print("Nid Pos:" + str(self.centre_x_in_nid) + ", " + str(self.centre_y_in_nid))
        #print("Nid Target: " + str(self.target_x_in_nid) + ", " + str(self.target_y_in_nid))
        #print("In colonie at pos: "+str(self.in_colonie_map_coords))
        #print(str(self.a_bouger_depuis_transition_map_ou_nid))
        if self.in_colonie_map_coords is None:#if sur la carte
            #process sur la carte
            if (self.target_x_in_map != self.centre_x_in_map or self.target_y_in_map != self.centre_y_in_map) and self.target_x_in_map is not None and self.target_y_in_map is not None:
                #print("fourmi bouge")
                self.a_bouger_depuis_transition_map_ou_nid=True
                self.goto_target_in_map(dt, map_data)
            else:
                self.is_moving=False
                self.is_busy=False
                self.target_x_in_map = None
                self.target_y_in_map = None
                for nid in tous_les_nids:
                    if self.centre_x_in_map == nid.tuile_debut[0] and self.centre_y_in_map == nid.tuile_debut[1] and self.a_bouger_depuis_transition_map_ou_nid==True:
                        print("entered colonie at "+str(nid.tuile_debut))
                        self.centre_y_in_map = None
                        self.centre_x_in_map = None
                        self.target_x_in_map = None
                        self.target_y_in_map = None
                        self.centre_x_in_nid = nid.salles_sorties[0].noeud.coord[0]
                        self.centre_y_in_nid = nid.salles_sorties[0].noeud.coord[1]
                        self.target_x_in_nid = None
                        self.target_y_in_nid = None

                        self.a_bouger_depuis_transition_map_ou_nid=False
                        self.in_colonie_map_coords=nid.tuile_debut

        else:
            #sortir colonie
            #if self.target_x_in_map != self.in_colonie_map_coords[0] and self.target_y_in_map != self.in_colonie_map_coords[1]:
                #self.in_colonie_map_coords=None
            #process dans le nid
            if self.target_x_in_nid is not None and self.target_y_in_nid is not None:
                self.goto_target_in_nid(dt)
    def set_target_in_nid(self, target_pos):
        #print("set target in nid")
        if not self.is_busy and self.centre_x_in_nid!=target_pos[0] and self.centre_y_in_nid!=target_pos[1]:
            self.target_x_in_nid=target_pos[0]
            self.target_y_in_nid=target_pos[1]
            self.is_busy=True
            self.is_moving=True

    def goto_target_in_nid(self,dt):
        self.colonie_origine.menu_f_a_updater = True
        #print("moving to target in nid")
        pos=Vector2(self.centre_x_in_nid,self.centre_y_in_nid)
        target=Vector2(self.target_x_in_nid,self.target_y_in_nid)
        movement=Vector2(0,0)
        if target!=pos:
            movement=(target-pos).normalize()*dt*self.speed/10
        self.centre_x_in_nid+=movement.x
        self.centre_y_in_nid+=movement.y
        #check if movement is to the right
        if movement.x==0:
            pass
        elif movement.x/abs(movement.x) > 0:
            self.facing=0
        elif movement.x/abs(movement.x) < 0:
            self.facing = 1
        if self.target_x_in_nid-abs(movement.x) < self.centre_x_in_nid < self.target_x_in_nid+abs(movement.x) and self.target_y_in_nid-abs(movement.y) < self.centre_y_in_nid < self.target_y_in_nid+abs(movement.y):
            self.centre_x_in_nid=self.target_x_in_nid
            self.centre_y_in_nid = self.target_y_in_nid
            self.target_x_in_nid = None
            self.target_y_in_nid = None
            self.is_busy = False
            self.is_moving = False
            #print("target in nid reached")

    def set_target_in_map(self, target_x, target_y, map_data):
        if isinstance(map_data[target_y][target_x], Eau):
            return
        if not self.is_busy:
            self.target_x_in_map = target_x
            self.target_y_in_map = target_y
            self.is_moving = True
            self.is_busy = True

    def goto_target_in_map(self, dt, map_data):
        if not self.path and self.is_moving:
            # Calculate path if not already calculated
            self.path = self.a_star(map_data)

        if self.path:
            next_tile = self.path[0]
            target_x_of_next_tile = next_tile[0]
            target_y_of_next_tile = next_tile[1]

            dx = target_x_of_next_tile - self.centre_x_in_map
            dy = target_y_of_next_tile - self.centre_y_in_map
            distance = math.sqrt(dx ** 2 + dy ** 2)

            if distance > 0.1:
                self.centre_x_in_map += self.speed * dx / distance * (dt / 1000)
                self.centre_y_in_map += self.speed * dy / distance * (dt / 1000)
                self.is_moving = True

                self.facing = 0 if dx > 0 else 1
            else:
                # Reached the next tile
                self.centre_x_in_map = target_x_of_next_tile
                self.centre_y_in_map = target_y_of_next_tile
                self.path.pop(0)  # Remove the reached tile
                self.is_moving = len(self.path) > 0
    
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
        arrivee = map_data[self.target_y_in_map][self.target_x_in_map]

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
        return int(self.centre_x_in_map), int(self.centre_y_in_map)

    def draw_in_nid(self,dt,screen,camera):
        #print("fourmi drawn")
        #image_scaled = pygame.transform.scale(self.image,(self.image.get_width()*camera.zoom,self.image.get_height()*camera.zoom))
        self.sprite.update(dt,camera,None,False)
        screen_pos = camera.apply((self.centre_x_in_nid, self.centre_y_in_nid))
        if self.is_selected:
            pygame.draw.rect(self.sprite.image,GREEN,(0,0,self.sprite.image.get_width(),self.sprite.image.get_height()),int(5*camera.zoom))
        screen.blit(self.sprite.image, (screen_pos[0] - self.sprite.image.get_width() / 2, screen_pos[1] - self.sprite.image.get_height() / 2))

        if self.menu_is_ouvert:
            self.menu=pygame.Surface((15+self.inventaire_taille_max * (100 + 15),15+100+15))
            self.menu.fill(BLACK)
            case_inventaire = pygame.Surface((100, 100))
            case_inventaire.fill(BROWN)
            for i in range(self.inventaire_taille_max):
                self.menu.blit(case_inventaire,(15+i*100,15))
            for i in range(len(self.inventaire)):
                image_item=pygame.transform.scale(pygame.image.load(self.inventaire[i].value[1]),(100,100))
                self.menu.blit(image_item,(15+i*100,15))
            menu_transformed = pygame.transform.scale(self.menu, (self.menu.get_width() * camera.zoom, self.menu.get_height() * camera.zoom))
            screen.blit(menu_transformed, camera.apply((self.centre_x_in_nid - self.menu.get_width() / 2,self.centre_y_in_nid - self.sprite.image.get_height()/2/camera.zoom - self.menu.get_height())))


class Ouvriere(Fourmis):
    def __init__(self, x0, y0, couleur, colonie_origine):
        super().__init__(colonie_origine, hp=10, atk=2, x0=x0, y0=y0, size=2,couleur=couleur)
        self.base_speed = 3
        self.speed = self.base_speed
        sprite_sheet_image=pygame.image.load(trouver_img("Fourmis/sprite_sheet_fourmi_noire.png")).convert_alpha()
        self.type="ouvriere"
        self.sprite = FourmisSprite(self,sprite_sheet_image,32,32,8,100,1)


    def attack(self, other):
        other.hp -= self.atk

class Soldat(Fourmis):
    def __init__(self, x0, y0, couleur,colonie_origine):
        super().__init__(colonie_origine, hp=25, atk=5, x0=x0, y0=y0, size=2,couleur=couleur)
        self.base_speed = 1.5
        self.speed = self.base_speed
        sprite_sheet_image = pygame.image.load(trouver_img("Fourmis/sprite_sheet_fourmi_noire.png")).convert_alpha()
        self.type="soldat"
        self.sprite = FourmisSprite(self, sprite_sheet_image, 32, 32, 8, 100, 1)


    def attack(self, other):
        other.hp -= self.atk

class FourmisSprite(pygame.sprite.Sprite):
    def __init__(self, fourmis: Fourmis, spritesheet, frame_width, frame_height, num_frames: int, frame_duration: int, scale):
        super().__init__()
        self.fourmis = fourmis
        self.spritesheet = spritesheet
        if self.fourmis.type == "ouvriere":
            #print("fourmi is ouvirere")
            self.spritesheet.blit(pygame.image.load(trouver_img("Fourmis/habit_ouvriere.png")).convert_alpha(),(0, 0))
        elif self.fourmis.type == "soldat":
            self.spritesheet.blit(pygame.image.load(trouver_img("Fourmis/habit_soldat.png")).convert_alpha(), (0, 0))
        #self.spritesheet = pygame.transform.flip(self.spritesheet,True,False)
        self.scale=scale
        self.frame_width = frame_width
        self.frame_height = frame_height
        self.num_frames = num_frames
        self.frame_duration = frame_duration
        self.current_frame = 0
        self.timer = 0
        self.frames_LEFT = self.extract_frames()
        self.frames_RIGHT = self.extract_frames(flipped=True)
        self.image = self.frames_LEFT[self.current_frame]
        if fourmis.in_colonie_map_coords is None:
            self.rect = self.image.get_rect(center=(fourmis.centre_x_in_map, fourmis.centre_y_in_map))
        else:
            self.rect = self.image.get_rect(center=(fourmis.centre_x_in_nid, fourmis.centre_y_in_nid))

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


    def update(self, dt, camera, tile_size, in_map=True):
        if self.fourmis.is_moving:
            self.timer += dt

            while self.timer > self.frame_duration:
                self.timer -= self.frame_duration
                self.current_frame = (self.current_frame + 1) % self.num_frames
        if self.fourmis.facing == 0:
            self.image = self.frames_RIGHT[self.current_frame]
        else:
            self.image = self.frames_LEFT[self.current_frame]
        #flip image for sprite that goes to the left
        self.image=pygame.transform.flip(self.image,True,False)
        zoom = camera.zoom
        scaled_width = int(self.image.get_width() * zoom * 2 * self.scale)
        scaled_height = int(self.image.get_height() * zoom * 2 * self.scale)
        self.image = pygame.transform.scale(self.image, (scaled_width, scaled_height))

        if in_map:
            world_x = self.fourmis.centre_x_in_map * tile_size
            world_y = self.fourmis.centre_y_in_map * tile_size
        else:
            world_x = self.fourmis.centre_x_in_nid
            world_y = self.fourmis.centre_y_in_nid
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
        self.is_busy=False
        self.is_moving=False

    def process(self, dt):
        dern_x, dern_y = self.centre_x, self.centre_y

        if self.target_x != self.centre_x or self.target_y != self.centre_y:
            self.goto_target(dt)

            if (dern_x, dern_y) != (self.centre_x, self.centre_y):
                for f in self.fourmis:
                    f.centre_x_in_map = self.centre_x
                    f.centre_y_in_map = self.centre_y

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