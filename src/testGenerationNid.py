import pygame
import prototypeGraphe as pg
from testGenerationGraphe import generer_graphe

def init() -> pygame.Surface:
    pygame.init()
    pygame.display.set_caption("Test de génération de nids")
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    return screen

def draw(screen, graphe, hauteur_sol = 100) -> None:
    screen.fill((255, 255, 255))
    for noeud in graphe.noeuds:
        pygame.draw.circle(screen, (0, 0, 0), noeud.coord, 10)
        for voisin in noeud.voisins:
            pygame.draw.line(screen, (0, 0, 0), noeud.coord, voisin.coord)

    pygame.draw.rect(screen, (50, 100, 200), (0, 0, SCREEN_WIDTH, hauteur_sol))
    
    pygame.display.flip()

def convertir_coord(coord, scale = 50) -> tuple:
    x = (SCREEN_WIDTH/2) + scale * coord[0]
    y = (SCREEN_HEIGHT/2) + scale * coord[1]
    return (int(x), int(y))

def main():
    running = True

    screen = init()
    graphe: pg.Graph = generer_graphe()
    for noeud in graphe.noeuds:
        noeud.coord = convertir_coord(noeud.coord)

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        
        draw(screen, graphe)


if __name__ == "__main__":
    SCREEN_WIDTH: int = 800
    SCREEN_HEIGHT: int = 600

    main()
    pygame.quit()