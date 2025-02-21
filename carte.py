import pygame
from numpy import array
from config import WHITE, BLACK, YELLOW, RED

class Tuile:
    def __init__(self, x, y, largeur, hauteur, couleur, is_border=False):
        self.x = x
        self.y = y
        self.largeur = largeur
        self.hauteur = hauteur
        self.couleur = couleur
        self.is_border = is_border

    def dessiner(self, ecran):
        pygame.draw.rect(ecran, self.couleur, (self.x, self.y, self.largeur, self.hauteur))

    def process(self):
        pass

class Map:
    def __init__(self):
        pygame.init()

        # Constants
        self.TILE_SIZE = 32
        self.MAP_WIDTH = 100
        self.MAP_HEIGHT = 100
        self.SCREEN_WIDTH = 1280
        self.SCREEN_HEIGHT = 720

        # Create a map with 100x100 tiles
        self.map_data = [[Tuile(x,y,self.TILE_SIZE, self.TILE_SIZE, couleur=pygame.Color("white")) for x in range(self.MAP_WIDTH)] for y in range(self.MAP_HEIGHT)]
        arr = array(self.map_data)
        print(arr.shape)
        # Fill the map with some data (e.g., 1 for walls, 0 for empty space)
        for y in range(self.MAP_HEIGHT):
            for x in range(self.MAP_WIDTH):
                if x == 0 or y == 0 or x == self.MAP_WIDTH - 1 or y == self.MAP_HEIGHT - 1:
                    self.map_data[y][x].is_border = True

        # Set up the display
        self.screen = pygame.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT), pygame.SCALED)
        pygame.display.set_caption("Tile Map with Camera")

        # Define colors
        self.RED = (255, 0, 0)

        # Camera position
        self.camera_x = 0
        self.camera_y = 0
        self.offset_x = 0
        self.offset_y = 0
        self.old_camera_x = 0
        self.old_camera_y = 0
        self.zoom = 1

    def start_game(self):
        # Main loop

        dragging = False
        running = True
        clock = pygame.time.Clock()
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                if event.type == pygame.MOUSEBUTTONDOWN:

                    if event.button == 1:
                        dragging = True
                        mouse_x, mouse_y = event.pos
                        self.offset_x = mouse_x - self.old_camera_x
                        self.offset_y = mouse_y - self.old_camera_y

                    elif event.button == 4:
                        print('scroll up')
                        self.zoom += 0.1


                elif event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1:
                        dragging = False
                        ### On sauvegarde la position de la camera avant de relacher le bouton
                        self.old_camera_x = self.camera_x
                        self.old_camera_y = self.camera_y

                elif event.type == pygame.MOUSEMOTION:
                    if dragging:
                        mouse_x, mouse_y = event.pos
                        ### On calcule la nouvelle position de la camera en fonction de la position de la souris
                        ### tout en gardant la position qu'on avait avant de reglisser
                        self.camera_x = (self.offset_x - mouse_x) + self.old_camera_x*2
                        self.camera_y = (self.offset_y - mouse_y) + self.old_camera_y*2

                        ### La camera commence au coin (0,0) et on voit jusqua (800,600) qui est SCREEN_WIDTH, SCREEN_HEIGHT
                        ### MAP_WIDTH * TILE_SIZE - SCREEN_WIDTH soit 3200-800=2400 est la position maximale de la camera en x
                        ### MAP_HEIGHT * TILE_SIZE - SCREEN_HEIGHT est la position maximale de la camera en y
                        ### Ainsi, si camera_x veut aller vers la gauche, on fait que le max est 0 (aucun mouv.) pour ne pas aller plus loin que la bordure
                        ### On prend le min pour ne pas depasser la bordure de l'ecran droite
                        self.camera_x = max(0, min(self.camera_x, self.MAP_WIDTH * self.TILE_SIZE - self.SCREEN_WIDTH))
                        self.camera_y = max(0, min(self.camera_y, self.MAP_HEIGHT * self.TILE_SIZE - self.SCREEN_HEIGHT + 50))



            ### On calcule les tuiles a dessiner en fonction de la position de la camera
            start_x = self.camera_x // self.TILE_SIZE
            start_y = self.camera_y // self.TILE_SIZE

            ### On prend le minimum comme ca on s'assure qu'on ne cherche pas en dehors de la map
            ### et on ajoute 1 pour s'assurer qu'on dessine meme les parties qui sont a moitie sur l'ecran
            end_x = min((self.camera_x + self.SCREEN_WIDTH) // self.TILE_SIZE + 1, self.MAP_WIDTH)
            end_y = min((self.camera_y + self.SCREEN_HEIGHT) // self.TILE_SIZE + 1, self.MAP_HEIGHT)


            ### On gere les deplacements de la camera
            # keys = pygame.key.get_pressed()
            # if keys[pygame.K_LEFT]:
            #     self.camera_x -= 4
            #     print(f'start_x: {start_x}, start_y: {start_y}')
            #     print(f'end_x: {end_x}, end_y: {end_y}')
            #     print(f'camera_x: {self.camera_x}, camera_y: {self.camera_y}')
            # if keys[pygame.K_RIGHT]:
            #     self.camera_x += 16 ## haute vitesse seulement pour tester
            #     print(f'start_x: {start_x}, start_y: {start_y}')
            #     print(f'end_x: {end_x}, end_y: {end_y}')
            #     print(f'camera_x: {self.camera_x}, camera_y: {self.camera_y}')
            # if keys[pygame.K_UP]:
            #     self.camera_y -= 4
            #     print(f'start_x: {start_x}, start_y: {start_y}')
            #     print(f'end_x: {end_x}, end_y: {end_y}')
            #     print(f'camera_x: {self.camera_x}, camera_y: {self.camera_y}')
            # if keys[pygame.K_DOWN]:
            #     print(f'start_x: {start_x}, start_y: {start_y}')
            #     print(f'end_x: {end_x}, end_y: {end_y}')
            #     print(f'camera_x: {self.camera_x}, camera_y: {self.camera_y}')
            #     self.camera_y += 4

            # On dessine les tuiles avec draw.rect, cest plus simple pour l'instant a la place de blit
            # blit est plus pour les images
            for y in range(start_y, end_y):
                for x in range(start_x, end_x):
                    tile = self.map_data[y][x]
                    tile_rect = pygame.Rect(x * self.TILE_SIZE - self.camera_x, y * self.TILE_SIZE - self.camera_y + 50, self.TILE_SIZE, self.TILE_SIZE)
                    if tile.is_border:
                        pygame.draw.rect(self.screen, self.RED, tile_rect)
                    else:
                        pygame.draw.rect(self.screen, WHITE, tile_rect)
                        pygame.draw.rect(self.screen, BLACK, tile_rect, 1)  # Draw black border

            # Menu et mise a jour de l'ecran
            pygame.draw.rect(self.screen, BLACK, (0, 0, self.SCREEN_WIDTH, 50))
            font = pygame.font.SysFont(None, 24)
            ## J'ajoute la demi des dimensions de l'ecran pour avoir la position de la camera par rapport au centre
            ## on peut l'enlever pour avoir la position par rapport au coin en haut a gauche
            ## je ne sais pas si ca l'importe
            camera_info = font.render(f'Camera X: {self.camera_x+self.SCREEN_WIDTH//2}, Camera Y: {self.camera_y+self.SCREEN_HEIGHT//2}', True, YELLOW)
            self.screen.blit(camera_info, (10, 10))
            pygame.display.flip()
            clock.tick(120)

        pygame.quit()

if __name__ == "__main__":
    game = Map()
    game.start_game()