import math
import random
from abc import ABC

import pygame
from pygame import Vector2

from config import trouver_img, BLACK, BROWN
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

class Fourmis(ABC):
    def __init__(self, colonie_origine, salle_initiale, hp: int, hp_max,atk: int, x0, y0, size, couleur):
        super().__init__()
        self.centre_in_map: list[float] = None
        self.centre_in_nid: list[float] = [x0, y0]
        self.target_in_map: list[float] = None
        self.target_in_nid: list[float] = None
        self.target_in_nid_queued: list[float] = None
        self.path = []

        self.base_speed = 2
        self.speed = self.base_speed
        self.nid_speed_factor = 100

        self.is_moving: bool = False
        self.is_busy: bool = False
        self.bouge_depuis_transition: bool = True
        self.menu_is_ouvert: bool = False
        self.is_selected: bool = False

        self.facing = 0 # 0 : droite, 1 : gauche
        self.width = 0
        self.height = 0
        self.size = size
        self.couleur = couleur
        self.image = pygame.image.load(self.couleur.value)
        self.image = pygame.transform.scale(self.image,(self.image.get_width() * self.size, self.image.get_height() * self.size))
        self.sprite: FourmisSprite = None

        self.type = "default"
        self.hp = hp
        self.hp_max = hp_max
        self.atk_base = atk
        self.atk_result = self.atk_base
        self.fourmi_attacking = None
        self.is_attacking_for_defense_automatique = False

        self.inventaire: list[TypeItem] = []
        self.inventaire_taille_max = 2
        self.menu: pygame.Surface=pygame.Surface((100,100))
        
        self.colonie_origine = colonie_origine
        self.current_colonie = colonie_origine
        self.current_salle = salle_initiale

        self.digging = False
        self.ready_to_dig = False
        self.digging_target: list[float] = None

    def set_attack(self, fourmi_target, map_data, liste_toutes_colonies):
        self.fourmi_attacking = fourmi_target
        self.is_busy = False

        if fourmi_target.current_colonie is None:
            self.set_target_in_map(round(fourmi_target.centre_in_map[0]),round(fourmi_target.centre_in_map[1]),map_data,liste_toutes_colonies)
        else:
            self.set_target_in_nid((round(fourmi_target.centre_in_nid[0]), round(fourmi_target.centre_in_nid[1])), fourmi_target.current_colonie, map_data,liste_toutes_colonies)

    def in_map(self) -> bool:
        if self.current_colonie is None:
            in_map = True
        else:
            in_map = False

        return in_map
    
    def in_tunnel(self) -> bool:
        if self.current_colonie.graphe is None:
            return False
        
        graphe = self.current_colonie.graphe
        for salle in graphe.salles:
            if (Vector2(self.centre_in_nid[0], self.centre_in_nid[1]) - Vector2(salle.noeud.coord[0], salle.noeud.coord[1])).magnitude() <= salle.type.value[0]:
                return False
            
        return True

    
    def dig_tunnel(self, target_pos: tuple[float, float]):
        if not self.in_tunnel():
            creation_valide: bool = self.current_colonie.graphe.creer_salle_depuis_intersection(self.current_salle, target_pos, self)
            if creation_valide:
                self.digging_target = target_pos

        else:        
            coord_centre = (self.centre_in_nid[0], self.centre_in_nid[1])
            tunnel_infos = self.current_colonie.graphe.get_coord_in_tunnel_at_coord(coord_centre)
            
            if tunnel_infos is not None:
                tunnel_fourmi, _ = tunnel_infos
                creation_valide: bool = self.current_colonie.graphe.creer_salle_depuis_tunnel(tunnel_fourmi, coord_centre, target_pos, self)
                if creation_valide:
                    self.digging_target = target_pos

    def process(self, dt, map_data, nids,liste_fourmis_jeu_complet,liste_toutes_colonies):
        def process_map():
            not_at_target = self.target_in_map is not None and (self.target_in_map[0] != self.centre_in_map[0] or self.target_in_map[1] != self.centre_in_map[1])
            if not_at_target and self.target_in_map is not None:
                self.bouge_depuis_transition = True
                self.goto_target(dt, map_data, nids)
            else:
                self.is_moving = False
                self.is_busy = False
                self.target_in_map = None

                for nid in nids:
                    if self.centre_in_map is not None:
                        on_nid = self.centre_in_map[0] == nid.tuile_debut[0] and self.centre_in_map[1] == nid.tuile_debut[1]
                        if on_nid and self.bouge_depuis_transition:
                            process_transition_map_nid(nid)

        def process_transition_map_nid(nid):
            self.centre_in_map = None

            for salle in nid.graphe.salles:
                if salle.type.value[1] == "Sortie":
                    self.centre_in_nid = salle.noeud.coord
                    self.current_salle = salle

            self.bouge_depuis_transition = False
            self.current_colonie = nid.colonie_owner

            if self.target_in_nid_queued is not None:
                self.target_in_nid = self.target_in_nid_queued
                self.target_in_nid_queued = None

        def process_nid():
            not_at_target = None
            if not self.digging:
                not_at_target = (self.target_in_nid is not None and (self.target_in_nid[0] != self.centre_in_nid[0] or self.target_in_nid[1] != self.centre_in_nid[1]))
            else:
                not_at_target = (self.digging_target is not None and (self.digging_target[0] != self.centre_in_nid[0] or self.digging_target[1] != self.centre_in_nid[1]))

            if not_at_target:
                self.goto_target(dt, map_data, nids)
            else:
                if self.digging_target is not None and self.digging and not self.ready_to_dig:
                    self.ready_to_dig = True

                elif self.digging_target is not None and self.digging and self.ready_to_dig:
                    self.ready_to_dig = False
                    self.digging = False

                self.is_moving = False
                self.target_in_nid = None
                self.digging_target = None

        def process_attaque():
            if self.hp <= 0:
                liste_fourmis_jeu_complet.remove(self)
                self.colonie_origine.fourmis.remove(self)

            if self.fourmi_attacking is not None:  # attack fourmi
                self.set_attack(self.fourmi_attacking,map_data,liste_toutes_colonies)
                if self.fourmi_attacking.current_colonie is None and self.current_colonie is None:  # if both in map
                    if (Vector2(self.fourmi_attacking.centre_in_map[0], self.fourmi_attacking.centre_in_map[1]) - Vector2(self.centre_in_map[0], self.centre_in_map[1])).magnitude() <= 1:  # if closer or equal to 1
                        # set all targets to none
                        self.target_in_nid = None
                        self.target_in_nid_queued = None
                        self.target_in_map = None
                        # set target fourmi attacking to none
                        self.fourmi_attacking.target_in_nid = None
                        self.fourmi_attacking.target_in_nid_queued = None
                        self.fourmi_attacking.target_in_map = None
                        # fight
                        self.is_busy = True
                        self.fourmi_attacking.is_busy = True
                        self.fourmi_attacking.hp -= (self.atk_result * dt) / 1000
                        if self.fourmi_attacking.fourmi_attacking is None:  # if ant i am attacking is not attacking me remove its attack from my healt
                            self.hp -= (self.fourmi_attacking.atk_result * dt) / 1000

                elif self.fourmi_attacking.current_colonie == self.current_colonie:  # if both in same nid
                    if (Vector2(self.fourmi_attacking.centre_in_nid[0], self.fourmi_attacking.centre_in_nid[1]) - Vector2(
                            self.centre_in_nid[0], self.centre_in_nid[1])).magnitude() <= 32:  # if closer or equal to 32
                        # set all targets to none
                        self.target_in_nid = None
                        self.target_in_nid_queued = None
                        self.target_in_map = None
                        # set target fourmi attacking to none
                        self.fourmi_attacking.target_in_nid = None
                        self.fourmi_attacking.target_in_nid_queued = None
                        self.fourmi_attacking.target_in_map = None
                        # fight
                        self.is_busy = True
                        self.fourmi_attacking.is_busy = True
                        self.fourmi_attacking.hp -= (self.atk_result * dt) / 1000
                        if self.fourmi_attacking.fourmi_attacking is None:  # if ant i am attacking is not attacking me remove its attack from my healt
                            self.hp -= (self.fourmi_attacking.atk_result * dt) / 1000

                if not self.is_busy:  # if self has stopped moving but is not busy=is not attacking
                    # set target to fourmi attacking
                    if self.fourmi_attacking.current_colonie is None:
                        self.set_target_in_map(self.fourmi_attacking.centre_in_map[0],self.fourmi_attacking.centre_in_map[1], map_data, liste_toutes_colonies)
                    else:
                        self.set_target_in_nid(self.fourmi_attacking.centre_in_nid, self.fourmi_attacking.current_colonie.tuile_debut, map_data, liste_toutes_colonies)

        def process_pickup():
            if map_data[round(self.centre_in_map[1])][round(self.centre_in_map[0])].tuile_ressource and not map_data[round(self.centre_in_map[1])][round(self.centre_in_map[0])].collectee:
               if len(self.inventaire)<self.inventaire_taille_max and self.target_in_map is None:
                   self.inventaire.append(map_data[round(self.centre_in_map[1])][round(self.centre_in_map[0])].get_ressource())
                   map_data[round(self.centre_in_map[1])][round(self.centre_in_map[0])].collectee=True

        if self.hp <= self.hp_max:
            self.hp += dt/1000
        for item in self.inventaire:
            if item == TypeItem.EPEE:
                self.atk_result=self.atk_result_with_epee
            elif item == TypeItem.ARMURE:
                self.hp_max=self.hp_max_with_armor
        if self.current_colonie is None:
            process_pickup()

        process_attaque()
        in_map = self.in_map()
        if in_map:
            process_map()
        else:
            process_nid()

    def set_target_in_nid(self, target_pos, target_nid, map_data, colonies):
        def find_closet_noeud_to_tunnel(tunnel):            
            chemin = None
            chemin1 = target_nid.graphe.dijkstra(self.current_salle.noeud, tunnel.depart.noeud)
            chemin2 = target_nid.graphe.dijkstra(self.current_salle.noeud, tunnel.arrivee.noeud)

            for noeud in chemin1:
                if noeud == chemin1[-1]:
                    break

                if noeud in (tunnel.depart.noeud, tunnel.arrivee.noeud):
                    chemin = chemin2
            
            if chemin is None:
                chemin = chemin1

            return chemin[-1]
        
        in_map = self.in_map()
        current_colonie = self.current_colonie

        self.is_busy = True
        self.is_moving = True

        if self.digging and not self.ready_to_dig and target_nid.graphe == self.colonie_origine.graphe:
            tunnel_infos = target_nid.graphe.get_coord_in_tunnel_at_coord(target_pos)
            if tunnel_infos is not None:
                tunnel, digging_target = tunnel_infos
                self.digging_target = digging_target

                noeud = find_closet_noeud_to_tunnel(tunnel)
                self.target_in_nid = noeud.coord

        elif self.digging and self.ready_to_dig and target_nid.graphe == self.colonie_origine.graphe:
            self.dig_tunnel(target_pos)

        if in_map:  # set target in nid from map
            self.set_target_in_map(target_nid.tuile_debut[0], target_nid.tuile_debut[1], map_data, colonies)

            noeud = target_nid.graphe.get_noeud_at_coord(target_pos)
            if noeud is not None:
                self.target_in_nid = noeud.coord

        elif self.current_colonie.graphe == target_nid.graphe:  # set target in nid from same nid
            noeud = target_nid.graphe.get_noeud_at_coord(target_pos)
            if noeud is not None:
                self.target_in_nid = noeud.coord

        else:  # set target in nid from other nid
            for salle in self.current_colonie.graphe.salles:
                if salle.type.value[1] == "Sortie":
                    self.set_target_in_nid(salle.noeud.coord, self.current_colonie, map_data, colonies)

            self.set_target_in_map(target_nid.tuile_debut[0], target_nid.tuile_debut[1], map_data, colonies)

            noeud = target_nid.graphe.get_noeud_at_coord(target_pos)
            if noeud is not None:
                self.target_in_nid_queued = noeud.coord

    def set_target_in_map(self, target_x, target_y, map_data, colonies):
        if isinstance(map_data[target_y][target_x], Eau):
            return

        self.target_in_map = [target_x, target_y]

        in_map = self.in_map()
        if in_map:
            self.is_moving = True
            self.is_busy = True
        else:
            # set target vers la sortie du nid
            for salle in self.current_colonie.graphe.salles:
                if salle.type.value[1] == "Sortie":
                    self.set_target_in_nid(salle.noeud.coord, self.current_colonie, map_data, colonies)

    def goto_target(self, dt, map_data, nids):
        def calculate_path_nid():
            current_nid = None
            for nid in nids:
                if nid.tuile_debut == self.current_colonie.tuile_debut:
                    current_nid = nid

            depart = current_nid.graphe.get_noeud_at_coord(self.centre_in_nid)
            arrivee = current_nid.graphe.get_noeud_at_coord(self.target_in_nid)

            path_nodes = current_nid.graphe.dijkstra(depart, arrivee)
            path = []
            for node in path_nodes:
                path.append((node.coord[0], node.coord[1]))

            if self.digging_target is not None:
                path.append(self.digging_target)

            self.path = path

        def update_current_salle():
            for noeud_voisin in self.current_salle.noeud.voisins:
                if self.centre_in_nid == noeud_voisin.coord:
                    for salle in self.current_colonie.graphe.salles:
                        if salle.noeud == noeud_voisin:
                            self.current_salle = salle

        in_map = self.in_map()
        if len(self.path) == 0:
            if self.ready_to_dig:
                self.path.append(self.digging_target)
            else:
                self.a_star(map_data) if in_map else calculate_path_nid()
            
            return

        next_node = self.path[0]
        next_target_x = next_node[0]
        next_target_y = next_node[1]

        if in_map:
            dx = next_target_x - self.centre_in_map[0]
            dy = next_target_y - self.centre_in_map[1]
        else:
            dx = next_target_x - self.centre_in_nid[0]
            dy = next_target_y - self.centre_in_nid[1]
        distance = math.sqrt(dx ** 2 + dy ** 2)

        if (in_map and distance > 0.1) or (not in_map and distance > 0.1 * self.nid_speed_factor):
            if in_map:
                self.centre_in_map[0] += self.speed * dx / distance * (dt / 1000)
                self.centre_in_map[1] += self.speed * dy / distance * (dt / 1000)
            else:
                self.centre_in_nid[0] += self.nid_speed_factor * self.speed * dx / distance * (dt / 1000)
                self.centre_in_nid[1] += self.nid_speed_factor * self.speed * dy / distance * (dt / 1000)

            self.is_moving = True
            self.is_busy = True
            self.facing = 0 if dx > 0 else 1
        else:
            # Reached the next tile
            if in_map:
                self.centre_in_map = [next_target_x, next_target_y]
            else:
                self.centre_in_nid = [next_target_x, next_target_y]
                update_current_salle()
                self.current_salle.salle_fourmi_collision(self, self.current_colonie, dt)
            
            if self.path != []:
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
        arrivee = map_data[self.target_in_map[1]][self.target_in_map[0]]

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
        return self.centre_in_map is not None
    
    def get_tuile(self):
        return int(self.centre_in_map[0]), int(self.centre_in_map[1])

    def get_colonie_pos(self):
        return self.centre_in_nid[0], self.centre_in_nid[1]

    def draw_in_nid(self,dt,screen,camera):
        self.sprite.update(dt,camera,None,False)
        screen_pos = camera.apply((self.centre_in_nid[0], self.centre_in_nid[1]))
        if self.is_selected:
            pygame.draw.rect(self.sprite.image,GREEN,(0,0,self.sprite.image.get_width(),self.sprite.image.get_height()),int(5*camera.zoom))
        for item in self.inventaire:
            if item == TypeItem.ARMURE:
                image_armure_temp=pygame.transform.scale(pygame.image.load(trouver_img("Items/armure.png")),(64*camera.zoom,64*camera.zoom))
                if self.facing==1:
                    image_armure_temp=pygame.transform.flip(image_armure_temp,True,False)
                self.sprite.image.blit(image_armure_temp,(0,0))
            elif item == TypeItem.EPEE:
                image_armure_temp = pygame.transform.scale(pygame.image.load(trouver_img("Items/epee.png")),(64 * camera.zoom, 64 * camera.zoom))
                if self.facing == 1:
                    image_armure_temp = pygame.transform.flip(image_armure_temp, True, False)
                self.sprite.image.blit(image_armure_temp, (0, 0))
        screen.blit(self.sprite.image, (screen_pos[0] - self.sprite.image.get_width() / 2, screen_pos[1] - self.sprite.image.get_height() / 2))

        if self.menu_is_ouvert:
            self.menu = pygame.Surface((5+self.inventaire_taille_max * (100 + 5),5+100+5))
            self.menu.fill(BLACK)
            case_inventaire = pygame.Surface((100, 100))
            case_inventaire.fill(BROWN)
            for i in range(self.inventaire_taille_max):
                self.menu.blit(case_inventaire,(5+i*100,5))
            for i in range(len(self.inventaire)):
                image_item=pygame.transform.scale(pygame.image.load(self.inventaire[i].value[1]),(100,100))
                self.menu.blit(image_item,(5+i*100,5))
            menu_transformed = pygame.transform.scale(self.menu, (self.menu.get_width() * camera.zoom, self.menu.get_height() * camera.zoom))
            screen.blit(menu_transformed, camera.apply((self.centre_in_nid[0] - self.menu.get_width() / 2,self.centre_in_nid[1] - self.sprite.image.get_height()/2/camera.zoom - self.menu.get_height())))

    def draw_in_map(self,dt,screen,camera):
        tile_size = 32
        self.sprite.update(dt,camera,tile_size,True)
        screen_pos = camera.apply((self.centre_in_map[0]*tile_size, self.centre_in_map[1]*tile_size))
        if self.is_selected:
            pygame.draw.rect(self.sprite.image,GREEN,(0,0,self.sprite.image.get_width(),self.sprite.image.get_height()),int(5*camera.zoom))
        scaled_sprite_image=pygame.transform.scale(self.sprite.image,(tile_size*camera.zoom,tile_size*camera.zoom))
        screen.blit(scaled_sprite_image, (screen_pos[0], screen_pos[1]))

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
            menu_transformed = pygame.transform.scale(self.menu, (self.menu.get_width() * camera.zoom/32, self.menu.get_height() * camera.zoom/32))
            screen.blit(menu_transformed, camera.apply((self.centre_in_map[0] * tile_size - self.menu.get_width() / 2,self.centre_in_map[1] * tile_size - self.sprite.image.get_height()/2/camera.zoom - self.menu.get_height())))

class FourmisSprite(pygame.sprite.Sprite):
    def __init__(self, fourmis: Fourmis, spritesheet, frame_width, frame_height, num_frames: int, frame_duration: int, scale):
        super().__init__()
        self.fourmis = fourmis
        self.spritesheet = spritesheet
        if self.fourmis.type == "ouvriere":
            self.spritesheet.blit(pygame.image.load(trouver_img("Fourmis/habit_ouvriere.png")).convert_alpha(),(0, 0))
        elif self.fourmis.type == "soldat":
            self.spritesheet.blit(pygame.image.load(trouver_img("Fourmis/habit_soldat.png")).convert_alpha(), (0, 0))
        
        self.scale = scale
        self.frame_width = frame_width
        self.frame_height = frame_height
        self.num_frames = num_frames
        self.frame_duration = frame_duration
        self.current_frame = 0
        self.timer = 0
        self.frames_LEFT = self.extract_frames()
        self.frames_RIGHT = self.extract_frames(flipped=True)
        self.image = self.frames_LEFT[self.current_frame]
        if fourmis.current_colonie is None:
            self.rect = self.image.get_rect(center=(fourmis.centre_in_map[0], fourmis.centre_in_map[1]))
        else:
            self.rect = self.image.get_rect(center=(fourmis.centre_in_nid[0], fourmis.centre_in_nid[1]))

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

        if in_map and self.fourmis.centre_in_map is not None:
            world_x = self.fourmis.centre_in_map[0] * tile_size
            world_y = self.fourmis.centre_in_map[1] * tile_size
        else:
            world_x = self.fourmis.centre_in_nid[0]
            world_y = self.fourmis.centre_in_nid[1]
        self.rect = self.image.get_rect(center=(world_x+scaled_width/2, world_y+scaled_height/2))
        self.rect = camera.apply_rect(self.rect)