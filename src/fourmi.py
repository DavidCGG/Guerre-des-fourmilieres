import math
import random
import uuid
from abc import ABC, abstractmethod
from enum import Enum

import pygame
from pygame import Vector2

#from config import SCREEN_WIDTH, SCREEN_HEIGHT
from config import trouver_img, AQUA, BLACK, BROWN
from config import GREEN, TypeItem
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
    def __init__(self, colonie_origine, hp: int, hp_max,atk: int, x0, y0, size, couleur):
        super().__init__()
        self.centre_y_in_map = None
        self.centre_x_in_map = None
        self.target_x_in_map = None
        self.target_y_in_map = None
        self.centre_x_in_nid = x0
        self.centre_y_in_nid = y0
        self.target_x_in_nid = None
        self.target_y_in_nid = None
        self.base_speed = 2
        self.speed = self.base_speed
        self.path = []
        self.nid_speed_factor = 100
        self.is_moving = False
        self.facing = 0 # 0 : droite, 1 : gauche
        self.hp = hp
        self.hp_max = hp_max
        self.atk_base = atk
        self.atk_result = self.atk_base
        self.width = 0
        self.height = 0
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
        self.menu_is_ouvert: bool = False
        self.is_selected: bool = False

        self.menu: pygame.Surface=pygame.Surface((100,100))

        self.target_x_in_nid_queued = None
        self.target_y_in_nid_queued = None

        self.fourmi_attacking = None

    def set_attack(self, fourmi_target,map_data,liste_toutes_colonies):
        print("fourmi attack set")
        self.fourmi_attacking = fourmi_target
        if fourmi_target.in_colonie_map_coords is None:
            self.set_target_in_map(fourmi_target.centre_x_in_map,fourmi_target.centre_y_in_map,map_data,liste_toutes_colonies)
        else:
            self.set_target_in_nid((fourmi_target.centre_x_in_nid,fourmi_target.centre_y_in_nid),fourmi_target.colonie_origine,map_data,liste_toutes_colonies)
        self.fourmi_attacking = None

    def in_map(self):
        if self.in_colonie_map_coords is None:
            in_map = True
        else:
            in_map = False

        return in_map

    def get_colonie_actuelle(self, colonies):
        if self.in_colonie_map_coords is None:
            return None

        for colonie in colonies:
            if colonie.tuile_debut == self.in_colonie_map_coords:
                return colonie

        return None

    def process(self, dt, map_data, nids,liste_fourmis_jeu_complet,liste_toutes_colonies):
        def process_map():
            not_at_target = (self.target_x_in_map != self.centre_x_in_map or self.target_y_in_map != self.centre_y_in_map)
            if not_at_target and self.target_x_in_map is not None and self.target_y_in_map is not None:
                self.a_bouger_depuis_transition_map_ou_nid = True
                self.goto_target(dt, map_data, nids)
            else:
                self.is_moving = False
                #self.is_busy = False
                self.target_x_in_map = None
                self.target_y_in_map = None

                for nid in nids:
                    on_nid = self.centre_x_in_map == nid.tuile_debut[0] and self.centre_y_in_map == nid.tuile_debut[1]
                    if on_nid and self.a_bouger_depuis_transition_map_ou_nid:
                        process_transition_map_nid(nid)

        def process_transition_map_nid(nid):
            self.centre_y_in_map = None
            self.centre_x_in_map = None
            for salle in nid.graphe.salles:
                if salle.type.value[1] == "sortie":
                    self.centre_x_in_nid = salle.noeud.coord[0]
                    self.centre_y_in_nid = salle.noeud.coord[1]

            self.a_bouger_depuis_transition_map_ou_nid = False
            self.in_colonie_map_coords = nid.tuile_debut

            if self.target_x_in_nid_queued is not None and self.target_y_in_nid_queued is not None:
                self.target_x_in_nid = self.target_x_in_nid_queued
                self.target_y_in_nid = self.target_y_in_nid_queued
                self.target_x_in_nid_queued = None
                self.target_y_in_nid_queued = None

        def process_nid():
            not_at_target = (self.target_x_in_nid != self.centre_x_in_nid or self.target_y_in_nid != self.centre_y_in_nid)
            if not_at_target and self.target_x_in_nid is not None and self.target_y_in_nid is not None:
                self.goto_target(dt, map_data, nids)
            else:
                self.is_moving = False
                self.is_busy = False
                self.target_x_in_nid = None
                self.target_y_in_nid = None

        def process_attaque():
            if self.hp <= 0:
                liste_fourmis_jeu_complet.remove(self)
                self.colonie_origine.fourmis.remove(self)
                print("fourmi morte")
            if self.fourmi_attacking is not None:  # attack fourmi
                if self.fourmi_attacking.in_colonie_map_coords is None and self.in_colonie_map_coords is None:  # if both in map
                    if (Vector2(self.fourmi_attacking.centre_x_in_map, self.fourmi_attacking.centre_y_in_map) - Vector2(
                            self.centre_x_in_map, self.centre_y_in_map)).magnitude() <= 1:  # if closer or equal to 1
                        # set all targets to none
                        self.target_x_in_nid = None
                        self.target_y_in_nid = None
                        self.target_x_in_nid_queued = None
                        self.target_x_in_nid_queued = None
                        self.target_x_in_map = None
                        self.target_y_in_map = None
                        # set target fourmi attacking to none
                        self.fourmi_attacking.target_x_in_nid = None
                        self.fourmi_attacking.target_y_in_nid = None
                        self.fourmi_attacking.target_x_in_nid_queued = None
                        self.fourmi_attacking.target_x_in_nid_queued = None
                        self.fourmi_attacking.target_x_in_map = None
                        self.fourmi_attacking.target_y_in_map = None
                        # fight
                        self.is_busy = True
                        self.fourmi_attacking.is_busy = True
                        self.fourmi_attacking.hp -= (self.atk_result * dt) / 1000
                        if self.fourmi_attacking.fourmi_attacking is None:  # if ant i am attacking is not attacking me remove its attack from my healt
                            self.hp -= (self.fourmi_attacking.atk_result * dt) / 1000

                elif self.fourmi_attacking.in_colonie_map_coords == self.in_colonie_map_coords:  # if both in same nid
                    if (Vector2(self.fourmi_attacking.centre_x_in_nid, self.fourmi_attacking.centre_y_in_nid) - Vector2(
                            self.centre_x_in_nid, self.centre_y_in_nid)).magnitude() <= 32:  # if closer or equal to 32
                        # set all targets to none
                        self.target_x_in_nid = None
                        self.target_y_in_nid = None
                        self.target_x_in_nid_queued = None
                        self.target_x_in_nid_queued = None
                        self.target_x_in_map = None
                        self.target_y_in_map = None
                        # set target fourmi attacking to none
                        self.fourmi_attacking.target_x_in_nid = None
                        self.fourmi_attacking.target_y_in_nid = None
                        self.fourmi_attacking.target_x_in_nid_queued = None
                        self.fourmi_attacking.target_x_in_nid_queued = None
                        self.fourmi_attacking.target_x_in_map = None
                        self.fourmi_attacking.target_y_in_map = None
                        # fight
                        self.is_busy = True
                        self.fourmi_attacking.is_busy = True
                        self.fourmi_attacking.hp -= (self.atk_result * dt) / 1000
                        if self.fourmi_attacking.fourmi_attacking is None:  # if ant i am attacking is not attacking me remove its attack from my healt
                            self.hp -= (self.fourmi_attacking.atk_result * dt) / 1000

                if not self.is_busy:  # if self has stopped moving but is not busy=is not attacking
                    # set target to fourmi attacking
                    if self.fourmi_attacking.in_colonie_map_coords is None:
                        self.set_target_in_map(self.fourmi_attacking.centre_x_in_map,
                                               self.fourmi_attacking.centre_y_in_map, map_data, liste_toutes_colonies)
                    else:
                        self.set_target_in_nid(
                            (self.fourmi_attacking.centre_x_in_nid, self.fourmi_attacking.centre_y_in_nid),
                            self.fourmi_attacking.in_colonie_map_coords, map_data, liste_toutes_colonies)

        process_attaque()
        in_map = self.in_map()
        if in_map:
            process_map()
        else:
            process_nid()

    def set_target_in_nid(self, target_pos, target_nid, map_data, colonies):
        in_map = self.in_map()
        current_colonie = self.get_colonie_actuelle(colonies)

        self.is_busy = True
        self.is_moving = True

        if in_map:  # set target in nid from map
            self.set_target_in_map(target_nid.tuile_debut[0], target_nid.tuile_debut[1], map_data, colonies)

            noeud = target_nid.graphe.get_noeud_at_coord(target_pos)
            if noeud is not None:
                self.target_x_in_nid = noeud.coord[0]
                self.target_y_in_nid = noeud.coord[1]

        elif current_colonie.graphe == target_nid.graphe:  # set target in nid from same nid
            noeud = target_nid.graphe.get_noeud_at_coord(target_pos)
            if noeud is not None:
                self.target_x_in_nid = noeud.coord[0]
                self.target_y_in_nid = noeud.coord[1]

        else:  # set target in nid from other nid
            current_colonie = self.get_colonie_actuelle(colonies)
            for salle in current_colonie.graphe.salles:
                if salle.type.value[1] == "sortie":
                    self.set_target_in_nid(salle.noeud.coord, current_colonie, map_data, colonies)

            self.set_target_in_map(target_nid.tuile_debut[0], target_nid.tuile_debut[1], map_data, colonies)

            noeud = target_nid.graphe.get_noeud_at_coord(target_pos)
            if noeud is not None:
                self.target_x_in_nid_queued = noeud.coord[0]
                self.target_y_in_nid_queued = noeud.coord[1]

    def set_target_in_map(self, target_x, target_y, map_data, colonies):
        if isinstance(map_data[target_y][target_x], Eau):
            return

        self.target_x_in_map = target_x
        self.target_y_in_map = target_y

        in_map = self.in_map()
        if in_map:
            self.is_moving = True
            self.is_busy = True
        else:
            # set target vers la sortie du nid
            current_colonie = self.get_colonie_actuelle(colonies)
            for salle in current_colonie.graphe.salles:
                if salle.type.value[1] == "sortie":
                    self.set_target_in_nid(salle.noeud.coord, current_colonie, map_data, colonies)

    def goto_target(self, dt, map_data, nids):
        def calculate_path_nid():
            current_nid = None
            for nid in nids:
                if nid.tuile_debut == self.in_colonie_map_coords:
                    current_nid = nid

            depart = current_nid.graphe.get_noeud_at_coord((self.centre_x_in_nid, self.centre_y_in_nid))
            arrivee = current_nid.graphe.get_noeud_at_coord((self.target_x_in_nid, self.target_y_in_nid))

            path_nodes = current_nid.graphe.dijkstra(depart, arrivee)
            path = []
            for node in path_nodes:
                path.append((node.coord[0], node.coord[1]))
            self.path = path

        in_map = self.in_map()
        if len(self.path) == 0:
            self.a_star(map_data) if in_map else calculate_path_nid()
            return

        next_node = self.path[0]
        next_target_x = next_node[0]
        next_target_y = next_node[1]

        if in_map:
            dx = next_target_x - self.centre_x_in_map
            dy = next_target_y - self.centre_y_in_map
        else:
            dx = next_target_x - self.centre_x_in_nid
            dy = next_target_y - self.centre_y_in_nid
        distance = math.sqrt(dx ** 2 + dy ** 2)

        if (in_map and distance > 0.1) or (not in_map and distance > 0.1 * self.nid_speed_factor):
            if in_map:
                self.centre_x_in_map += self.speed * dx / distance * (dt / 1000)
                self.centre_y_in_map += self.speed * dy / distance * (dt / 1000)
            else:
                self.centre_x_in_nid += self.nid_speed_factor * self.speed * dx / distance * (dt / 1000)
                self.centre_y_in_nid += self.nid_speed_factor * self.speed * dy / distance * (dt / 1000)

            self.is_moving = True
            self.facing = 0 if dx > 0 else 1
        else:
            # Reached the next tile
            if in_map:
                self.centre_x_in_map = next_target_x
                self.centre_y_in_map = next_target_y
            else:
                self.centre_x_in_nid = next_target_x
                self.centre_y_in_nid = next_target_y
            self.path.pop(0)  # Remove the reached tile
    
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
        self.path = chemin

    def dans_carte(self):
        return self.centre_x_in_map is not None and self.centre_y_in_map is not None
    def get_tuile(self):
        return int(self.centre_x_in_map), int(self.centre_y_in_map)

    def get_colonie_pos(self):
        return self.centre_x_in_nid, self.centre_y_in_nid

    def draw_in_nid(self,dt,screen,camera):
        #print("fourmi drawn")
        #image_scaled = pygame.transform.scale(self.image,(self.image.get_width()*camera.zoom,self.image.get_height()*camera.zoom))
        self.sprite.update(dt,camera,None,False)
        screen_pos = camera.apply((self.centre_x_in_nid, self.centre_y_in_nid))
        if self.is_selected:
            pygame.draw.rect(self.sprite.image,GREEN,(0,0,self.sprite.image.get_width(),self.sprite.image.get_height()),int(5*camera.zoom))
        screen.blit(self.sprite.image, (screen_pos[0] - self.sprite.image.get_width() / 2, screen_pos[1] - self.sprite.image.get_height() / 2))

        if self.menu_is_ouvert:
            self.menu=pygame.Surface((5+self.inventaire_taille_max * (100 + 5),5+100+5))
            self.menu.fill(BLACK)
            case_inventaire = pygame.Surface((100, 100))
            case_inventaire.fill(BROWN)
            for i in range(self.inventaire_taille_max):
                self.menu.blit(case_inventaire,(5+i*100,5))
            for i in range(len(self.inventaire)):
                image_item=pygame.transform.scale(pygame.image.load(self.inventaire[i].value[1]),(100,100))
                self.menu.blit(image_item,(5+i*100,5))
            menu_transformed = pygame.transform.scale(self.menu, (self.menu.get_width() * camera.zoom, self.menu.get_height() * camera.zoom))
            screen.blit(menu_transformed, camera.apply((self.centre_x_in_nid - self.menu.get_width() / 2,self.centre_y_in_nid - self.sprite.image.get_height()/2/camera.zoom - self.menu.get_height())))


class Ouvriere(Fourmis):
    def __init__(self, x0, y0, couleur, colonie_origine):
        super().__init__(colonie_origine, hp=100, hp_max=100,atk=40, x0=x0, y0=y0, size=2,couleur=couleur)
        self.base_speed = 3
        self.speed = self.base_speed
        sprite_sheet_image=pygame.image.load(trouver_img(f"Fourmis/sprite_sheet_fourmi_{couleur.name.lower()}.png")).convert_alpha()
        self.type="ouvriere"
        self.sprite = FourmisSprite(self,sprite_sheet_image,32,32,8,100,1)

class Soldat(Fourmis):
    def __init__(self, x0, y0, couleur,colonie_origine):
        super().__init__(colonie_origine, hp=200, hp_max=200,atk=50, x0=x0, y0=y0, size=2,couleur=couleur)
        self.base_speed = 1.5
        self.speed = self.base_speed
        sprite_sheet_image = pygame.image.load(trouver_img("Fourmis/sprite_sheet_fourmi_noire.png")).convert_alpha()
        self.type = "soldat"
        self.sprite = FourmisSprite(self, sprite_sheet_image, 32, 32, 8, 100, 1)

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

        if in_map and self.fourmis.centre_x_in_map is not None and self.fourmis.centre_y_in_map is not None:
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