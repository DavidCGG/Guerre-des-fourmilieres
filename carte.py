import pygame
from numpy import array
from config import WHITE, BLACK, YELLOW
# Initialize Pygame
class Map:
    def __init__(self):
        pygame.init()

        # Constants
        TILE_SIZE = 32
        MAP_WIDTH = 100
        MAP_HEIGHT = 100
        SCREEN_WIDTH = 800
        SCREEN_HEIGHT = 600

        # Create a map with 100x100 tiles
        map_data = [[0 for _ in range(MAP_WIDTH)] for _ in range(MAP_HEIGHT)]
        arr = array(map_data)
        print(arr.shape)
        # Fill the map with some data (e.g., 1 for walls, 0 for empty space)
        for y in range(MAP_HEIGHT):
            for x in range(MAP_WIDTH):
                if x == 0 or y == 0 or x == MAP_WIDTH - 1 or y == MAP_HEIGHT - 1:
                    map_data[y][x] = 1  # Create a border wall

        # Set up the display
        screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SCALED)
        pygame.display.set_caption("Tile Map with Camera")

        # Define colors
        WHITE = (255, 255, 255)
        BLACK = (0, 0, 0)
        RED = (255, 0, 0)

        # Camera position
        camera_x = 0
        camera_y = 0

        # Main loop
        running = True
        clock = pygame.time.Clock()
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            # Clear the screen
            screen.fill(BLACK)

            ### On calcule les tuiles a dessiner en fonction de la position de la camera
            start_x = camera_x // TILE_SIZE
            start_y = camera_y // TILE_SIZE

            ### On prend le minimum comme ca on s'assure qu'on ne cherche pas en dehors de la map
            ### et on ajoute 1 pour s'assurer qu'on dessine meme les parties qui sont a moitie sur l'ecran
            end_x = min((camera_x + SCREEN_WIDTH) // TILE_SIZE + 1, MAP_WIDTH)
            end_y = min((camera_y + SCREEN_HEIGHT) // TILE_SIZE + 1, MAP_HEIGHT)

            ### On gere les deplacements de la camera
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT]:
                camera_x -= 4
                print(f'start_x: {start_x}, start_y: {start_y}')
                print(f'end_x: {end_x}, end_y: {end_y}')
                print(f'camera_x: {camera_x}, camera_y: {camera_y}')
            if keys[pygame.K_RIGHT]:
                camera_x += 16 ## haute vitesse seulement pour tester
                print(f'start_x: {start_x}, start_y: {start_y}')
                print(f'end_x: {end_x}, end_y: {end_y}')
                print(f'camera_x: {camera_x}, camera_y: {camera_y}')
            if keys[pygame.K_UP]:
                camera_y -= 4
                print(f'start_x: {start_x}, start_y: {start_y}')
                print(f'end_x: {end_x}, end_y: {end_y}')
                print(f'camera_x: {camera_x}, camera_y: {camera_y}')
            if keys[pygame.K_DOWN]:
                print(f'start_x: {start_x}, start_y: {start_y}')
                print(f'end_x: {end_x}, end_y: {end_y}')
                print(f'camera_x: {camera_x}, camera_y: {camera_y}')
                camera_y += 4

            ### La camera commence au coin (0,0) et on voit jusqua (800,600) qui est SCREEN_WIDTH, SCREEN_HEIGHT
            ### MAP_WIDTH * TILE_SIZE - SCREEN_WIDTH soit 3200-800=2400 est la position maximale de la camera en x
            ### MAP_HEIGHT * TILE_SIZE - SCREEN_HEIGHT est la position maximale de la camera en y
            ### Ainsi, si camera_x veut aller vers la gauche, on fait que le max est 0 pour ne pas aller plus loin que la bordure
            ### et
            camera_x = max(0, min(camera_x, MAP_WIDTH * TILE_SIZE - SCREEN_WIDTH))
            camera_y = max(0, min(camera_y, MAP_HEIGHT * TILE_SIZE - SCREEN_HEIGHT))

            for y in range(start_y, end_y):
                for x in range(start_x, end_x):


                    tile = map_data[y][x]
                    tile_rect = pygame.Rect(x * TILE_SIZE - camera_x, y * TILE_SIZE - camera_y, TILE_SIZE, TILE_SIZE)
                    if tile == 1:
                        pygame.draw.rect(screen, RED, tile_rect)
                    else:
                        pygame.draw.rect(screen, WHITE, tile_rect)
                        pygame.draw.rect(screen, BLACK, tile_rect, 1)  # Draw black border

            # Update the display
            font = pygame.font.SysFont(None, 24)
            camera_info = font.render(f'Camera X: {camera_x}, Camera Y: {camera_y}', True, YELLOW)
            screen.blit(camera_info, (10, 10))
            pygame.display.flip()
            clock.tick(60)

        pygame.quit()