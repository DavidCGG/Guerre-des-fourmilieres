import pygame
import sys
import os
from Fourmis import FourmisSprite, Ouvriere, Soldat
from config import WIDTH, HEIGHT

# Initialize Pygame
pygame.init()

# Set up the display
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Menu Principal")

# Define colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Menu options
menu_options = ["Start Game", "Options", "Quit"]

def draw_text(text, font, color, surface, x, y):
    textobj = font.render(text, True, color)
    textrect = textobj.get_rect()
    textrect.topleft = (x, y)
    surface.blit(textobj, textrect)


def trouver_img(nom: str) -> str:
    return os.path.join(os.path.dirname(__file__), "..", "assets", "images", nom)

def trouver_font(nom: str) -> str:
    return os.path.join(os.path.dirname(__file__), "..", "assets", "fonts", nom)

pygame.display.set_icon(pygame.image.load(trouver_img("Fourmi.png")))
font = pygame.font.Font(trouver_font("LowresPixel-Regular.otf"), 74)
small_font = pygame.font.Font(trouver_font("LowresPixel-Regular.otf"), 36)

#spritesheet = pygame.image.load(trouver_img("4-frame-ant.png")).convert_alpha()
#fourmis = Ouvriere(600, 300, 8.5, "random")
#fourmis_sprite = FourmisSprite(fourmis, spritesheet, 16, 16, 4, 300)

#sprites = pygame.sprite.Group()
#sprites.add(fourmis_sprite)


def main_menu():
    selected_option = 0
    clock = pygame.time.Clock()

    while True:
        dt = clock.tick(60)
        screen.fill(pygame.Color("black"))

        # Draw menu options
        for i, option in enumerate(menu_options):
            if i == selected_option:
                draw_text(option, font, WHITE, screen, 100, 100 + i * 100)
            else:
                draw_text(option, small_font, WHITE, screen, 100, 100 + i * 100)

        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    selected_option = (selected_option - 1) % len(menu_options)
                elif event.key == pygame.K_DOWN:
                    selected_option = (selected_option + 1) % len(menu_options)
                elif event.key == pygame.K_RETURN:
                    if selected_option == 0:
                        # Start Game
                        print("Start Game selected")
                    elif selected_option == 1:
                        # Options
                        print("Options selected")
                    elif selected_option == 2:
                        # Quit
                        pygame.quit()
                        sys.exit()

        #sprites.update(dt)
        #sprites.draw(screen)
        pygame.display.update()

if __name__ == "__main__":
    main_menu()