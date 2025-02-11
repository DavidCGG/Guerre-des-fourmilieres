import math
import random
from abc import ABC, abstractmethod
import pygame




class Fourmis(ABC):
    def __init__(self, hp: int, atk: int, scale,  x0, y0, mouvement=None):
        super().__init__()
        self.centre_y = y0
        self.centre_x = x0
        self.scale = scale
        self.target_x = x0
        self.target_y = y0
        self.speed = 2
        self.type_mouvement = mouvement
        self.facing = 0 # 0 bright
        self.hp = hp
        self.atk = atk

    @abstractmethod
    def attack(self, other):
        pass

    def update(self):
        if self.type_mouvement == "random":
            self.random_mouvement()
        elif self.type_mouvement == "pathfind":
            self.pathfind_mouvement()
        elif self.type_mouvement is None:
            pass

    def random_mouvement(self):
        if self.centre_x == self.target_x and self.centre_y == self.target_y:
            self.set_nouv_target()

        self.goto_target()

    def set_nouv_target(self):
        angle = random.uniform(0, 2*math.pi)
        distance = random.uniform(20,100)
        self.target_x = self.centre_x + distance*math.cos(angle)
        self.target_y = self.centre_y + distance*math.sin(angle)

    def goto_target(self):
        dx = self.target_x - self.centre_x
        dy = self.target_y - self.centre_y
        distance = math.sqrt(dx**2 + dy**2)

        if distance > self.speed:
            self.centre_x += self.speed*dx/distance
            self.centre_y += self.speed*dy/distance
        else:
            self.centre_x = self.target_x
            self.centre_y = self.target_y

    def pathfind_mouvement(self):
        pass


class Ouvriere(Fourmis):
    def __init__(self, x0, y0, scale=1.0, mouvement=None):
        super().__init__(hp=10, atk=2, scale=scale, x0=x0, y0=y0, mouvement=mouvement)
        self.speed = 2.5

    def attack(self, other):
        other.hp -= self.atk

class Soldat(Fourmis):
    def __init__(self, x0, y0, scale=1.0, mouvement="random"):
        super().__init__(hp=25, atk=5, scale=scale, x0=x0, y0=y0, mouvement=mouvement)
        self.speed = 1.5

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
        self.frames = self.extract_frames()
        self.image = self.frames[self.current_frame]
        self.rect = self.image.get_rect(center=(self.fourmis.centre_x, self.fourmis.centre_y))

    def extract_frames(self):
        frames = []
        for i in range(self.num_frames):
            frame = self.spritesheet.subsurface(pygame.Rect(i*self.frame_width, 0, self.frame_width, self.frame_height))
            frame = pygame.transform.scale(frame, (int(self.frame_width*self.fourmis.scale), int(self.frame_height*self.fourmis.scale)))
            frames.append(frame)
        return frames

    def update(self, dt):
        self.fourmis.update()
        self.timer += dt
        while self.timer > self.frame_duration:
            self.timer -= self.frame_duration
            self.current_frame = (self.current_frame + 1) % self.num_frames
            self.image = self.frames[self.current_frame]