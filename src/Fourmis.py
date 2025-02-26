import math
import random
from abc import ABC, abstractmethod
import pygame
from config import WIDTH, HEIGHT


class Fourmis(ABC):
    def __init__(self, hp: int, atk: int, scale,  x0, y0, mouvement=None):
        super().__init__()
        self.centre_y = y0
        self.centre_x = x0
        self.scale = scale
        self.target_x = x0
        self.target_y = y0
        self.base_speed = 2
        self.speed = self.base_speed * self.scale
        self.type_mouvement = mouvement
        self.facing = 0 # 0 : droite, 1 : gauche
        self.hp = hp
        self.atk = atk
        self.width = 0
        self.height = 0
        self.pause_timer = 0

    @abstractmethod
    def attack(self, other):
        pass

    def update(self, dt):
        if self.pause_timer > 0:
            self.pause_timer -= dt
            return

        if self.type_mouvement == "random":
            self.random_mouvement(dt)
        elif self.type_mouvement == "pathfind":
            self.pathfind_mouvement(dt)
        elif self.type_mouvement is None:
            pass

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


    def goto_target(self, dt):
        dx = self.target_x - self.centre_x
        dy = self.target_y - self.centre_y
        distance = math.sqrt(dx**2 + dy**2)

        if distance > 0.5:
            self.centre_x += self.speed * dx/distance * (dt/1000)
            self.centre_y += self.speed * dy/distance * (dt/1000)

        else:
            self.centre_x = self.target_x
            self.centre_y = self.target_y

        if dx > 0:
            self.facing = 0
        else:
            self.facing = 1

    def pathfind_mouvement(self):
        pass


class Ouvriere(Fourmis):
    def __init__(self, x0, y0, scale=1.0, mouvement=None):
        super().__init__(hp=10, atk=2, scale=scale, x0=x0, y0=y0, mouvement=mouvement)
        self.base_speed = 3
        self.speed = self.base_speed * self.scale

    def attack(self, other):
        other.hp -= self.atk

class Soldat(Fourmis):
    def __init__(self, x0, y0, scale=1.0, mouvement="random"):
        super().__init__(hp=25, atk=5, scale=scale, x0=x0, y0=y0, mouvement=mouvement)
        self.base_speed = 1.5
        self.speed = self.base_speed * self.scale

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
        self.rect = self.image.get_rect(center=(self.fourmis.centre_x, self.fourmis.centre_y))

    def extract_frames(self, flipped=False):
        frames = []
        frame = None
        for i in range(self.num_frames):
            frame = self.spritesheet.subsurface(pygame.Rect(i*self.frame_width, 0, self.frame_width, self.frame_height))
            frame = pygame.transform.scale(frame, (int(self.frame_width*self.fourmis.scale), int(self.frame_height*self.fourmis.scale)))
            if flipped:
                frame = pygame.transform.flip(frame, True, False)
            frames.append(frame)

        self.fourmis.width = frame.get_width()
        self.fourmis.height = frame.get_height()
        return frames

    def update(self, dt):
        self.fourmis.update(dt)
        if self.fourmis.pause_timer > 0:
            return

        self.timer += dt

        while self.timer > self.frame_duration:
            self.timer -= self.frame_duration
            self.current_frame = (self.current_frame + 1) % self.num_frames
        if self.fourmis.facing == 0:
            self.image = self.frames_RIGHT[self.current_frame]
        else:
            self.image = self.frames_LEFT[self.current_frame]
        self.rect.center = (self.fourmis.centre_x, self.fourmis.centre_y)