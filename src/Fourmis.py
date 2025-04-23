import math
import random
from abc import ABC, abstractmethod
import pygame
from config import WIDTH, HEIGHT, trouver_img


class Fourmis(ABC):
    def __init__(self, hp: int, atk: int, scale,  x0, y0):
        super().__init__()
        self.centre_y = y0
        self.centre_x = x0
        self.scale = scale
        self.target_x = x0
        self.target_y = y0
        self.base_speed = 2
        self.speed = self.base_speed * self.scale
        self.path = None
        self.moving = False
        self.facing = 0 # 0 : droite, 1 : gauche
        self.hp = hp
        self.atk = atk
        self.width = 0
        self.height = 0
        self.pause_timer = 0
        self.tient_ressource = False

    @abstractmethod
    def attack(self, other):
        pass

    def process(self, dt):
        if self.target_x != self.centre_x or self.target_y != self.centre_y:
            self.goto_target(dt)

    def random_mouvement(self, dt):
        if self.centre_x == self.target_x and self.centre_y == self.target_y:
            self.set_nouv_target()
            self.pause_timer = random.uniform(800, 2000)

        self.goto_target(dt)

    def set_nouv_target(self):
        angle = random.uniform(0, 2*math.pi)
        distance = random.uniform(40, 150)

        self.target_x = self.centre_x + distance*math.cos(angle)
        self.target_y = self.centre_y + distance*math.sin(angle)


        ## On s'assure que la cible est dans les limites de l'écran
        self.target_x = max(0+self.width//2, min(WIDTH-self.width//2, self.target_x))
        self.target_y = max(0+self.height//2, min(HEIGHT-self.height//2, self.target_y))

    def set_target(self, target_x, target_y):
        self.target_x = target_x
        self.target_y = target_y

    def goto_target(self, dt):

        if not hasattr(self, "path") or not self.path:
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

                self.facing = 0 if dx > 0 else 1
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


class Ouvriere(Fourmis):
    def __init__(self, x0, y0, scale=1.0):
        super().__init__(hp=10, atk=2, scale=scale, x0=x0, y0=y0)
        self.base_speed = 3
        self.speed = self.base_speed * self.scale
        self.size = 1




    def attack(self, other):
        other.hp -= self.atk

class Soldat(Fourmis):
    def __init__(self, x0, y0, scale=1.0):
        super().__init__(hp=25, atk=5, scale=scale, x0=x0, y0=y0)
        self.base_speed = 1.5
        self.speed = self.base_speed * self.scale
        self.size = 2 # prend 2 places dans le groupe

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
        self.rect = camera.apply(self.rect)

class Groupe:
    def __init__(self, tile_x, tile_y, images):
        self.fourmis = []
        self.max_capacite = 5

        self.images = images
        self.image = self.images[0]

        self.centre_x = tile_x
        self.centre_y = tile_y
        self.rect = self.image.get_rect(center=(self.centre_x, self.centre_y))



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
        self.rect = camera.apply(self.rect)


    def ajouter_fourmis(self, fourmis):
        if self.get_size() + fourmis.size <= self.max_capacite:
            self.fourmis.append(fourmis)
        return


    def enlever_fourmis(self, fourmis):
        if fourmis in self.fourmis:
            self.fourmis.remove(fourmis)
        else: print("fourmi pas dans le groupe")

    def get_tuile(self):
        return int(self.centre_x), int(self.centre_y)

    def get_size(self):
        tot = 0
        for fourmi in self.fourmis:
            tot += fourmi.size
        return tot

    def get_nb_fourmis(self):
        return len(self.fourmis)

    def est_vide(self):
        return len(self.fourmis) == 0