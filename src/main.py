import pygame
import carte2 as carte
import affichage_nid as nid
from config import trouver_font, trouver_img
from config import SCREEN_WIDTH, SCREEN_HEIGHT
from config import WHITE, BLACK, YELLOW
from classes import Bouton
from Fourmis import FourmiTitleScreen, FourmiTitleScreenSprite

#Variables globales
screen: pygame.Surface = None
clock: pygame.time.Clock = pygame.time.Clock()

font = pygame.font.Font(trouver_font("LowresPixel-Regular.otf"), 74)
small_font = pygame.font.Font(trouver_font("LowresPixel-Regular.otf"), 36)
tiny_font = pygame.font.Font(trouver_font("LowresPixel-Regular.otf"), 18)
liste_boutons: list[Bouton] = []

running: bool = True
in_menu_principal: bool = True
in_menu_secondaire: bool = False
in_carte: bool = False
in_nid: bool = False

#Variables du menu principal
selected_option: int = 0
liste_options = ["Nouvelle partie", "Options", "Quitter"]

spritesheet: pygame.image = None
fourmi: FourmiTitleScreen = None
fourmi_sprite: FourmiTitleScreenSprite = None
sprites = pygame.sprite.Group()

#Variables du jeu
carte_jeu: carte.Carte = None
nids: list[nid.Nid] =[]
current_nid: nid.Nid = None

def initialiser() -> None:
    """
    Initialise Pygame, la fenêtre de jeu et les éléments du menu principal
    Args:
        None
    Returns:
        None
    """
    global screen
    global spritesheet
    global fourmi
    global fourmi_sprite
    global sprites

    pygame.init()
    pygame.font.init()
    pygame.display.set_caption("Guerre des fourmillières")
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

    spritesheet = pygame.image.load(trouver_img("4-frame-ant.png")).convert_alpha()
    icon = spritesheet.subsurface(pygame.Rect(16, 0, 16, 16))
    pygame.display.set_icon(icon)

    fourmi = FourmiTitleScreen(3 * SCREEN_WIDTH // 5, 3 * SCREEN_HEIGHT // 5, 8)
    fourmi_sprite = FourmiTitleScreenSprite(fourmi, spritesheet, 16, 16, 4, 300)
    sprites.add(fourmi_sprite)

def draw() -> None:
    """
    Dessine l'écran de jeu ou le menu principal
    Args:
        None
    Returns:
        None
    """
    def draw_menu_principal() -> None:
        """
        Dessine la fourmi et le texte du menu principal en appelant draw_text_menu_principal
        Args:
            None
        Returns:
            None
        """
        screen.fill(BLACK)
        sprites.draw(screen)

        for i in range(len(liste_options)):
            y = SCREEN_HEIGHT // 2 - (150 * (len(liste_options) - 1)) // 2 - small_font.get_height() // 2 + i * 150

            if i == selected_option:
                draw_text_menu_principal(liste_options[i], font, 100, y)
            else:
                draw_text_menu_principal(liste_options[i], small_font, 100, y)
        
    def draw_text_menu_principal(text, font, x, y) -> None:
        """
        Dessine le texte d'une option du menu principal
        Args:
            text (str): Le texte à dessiner
            font (pygame.font.Font): La police de caractères
            x (int): La position x du texte
            y (int): La position y du texte
        Returns:
            None
        """
        textobj = font.render(text, True, WHITE)
        textrect = textobj.get_rect()
        textrect.topleft = (x, y)
        screen.blit(textobj, textrect)

    def draw_top_bar() -> None:
        """
        Dessine la barre supérieure de l'écran de jeu pour la carte ou un nid
        Args:
            None
        Returns:
            None
        """
        global liste_boutons

        camera = carte_jeu.camera if in_carte else current_nid.camera

        if  not any(isinstance(bouton, Bouton) and bouton.texte == "Options" for bouton in liste_boutons):
            bouton = Bouton(screen, SCREEN_WIDTH - 100, 25, 100, 30, "Options", menu_options, pygame.font.Font(trouver_font("LowresPixel-Regular.otf"), 22))
            liste_boutons.append(bouton)

        pygame.draw.rect(screen, BLACK, (0, 0, SCREEN_WIDTH, 50))

        fps_info = tiny_font.render(f'FPS: {clock.get_fps():.0f}', True, YELLOW)
        zoom_info = tiny_font.render(f'Zoom: {camera.zoom * 100:.2f}%', True, YELLOW)

        screen.blit(fps_info, (10, 5))
        screen.blit(zoom_info, (10, 25))

        titre_message: str = None
        if in_carte:
            titre_message = f"Carte"
        elif in_nid and nids.index(current_nid) == 0:
            titre_message = f"Nid joueur"
        else:
            titre_message = f"Nid ennemi {nids.index(current_nid)}"

        titre = small_font.render(titre_message, True, WHITE)
        screen.blit(titre, (SCREEN_WIDTH / 2 - titre.get_width() / 2, 10))

    if in_menu_principal:
        draw_menu_principal()
    elif in_carte and not in_menu_secondaire:
        carte_jeu.draw(screen)
    elif in_nid and not in_menu_secondaire:
        current_nid.draw(screen)

    if in_carte or in_nid:
        draw_top_bar()
        for bouton in liste_boutons:
            bouton.draw()

    pygame.display.update()

def menu_options() -> None:
    """
    Affiche le menu des options de la carte et du nid
    Args:
        None
    Returns:
        None
    """
    global liste_boutons
    global in_menu_secondaire

    in_menu_secondaire = True

    surface = pygame.Surface((300, 400))
    surface.fill(BLACK)

    texte_render = pygame.font.Font(trouver_font("LowresPixel-Regular.otf"), 36).render("Options", True, WHITE)
    police_boutons = pygame.font.Font(trouver_font("LowresPixel-Regular.otf"), 30)

    surface.blit(texte_render, [surface.get_width() / 2 - texte_render.get_rect().width / 2, 10])
    screen.blit(surface, (SCREEN_WIDTH / 2 - 150, SCREEN_HEIGHT / 2 - 250))

    grid_mode_str = "ON" if carte_jeu.grid_mode else "OFF"

    liste_boutons.append(Bouton(screen, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 - 100, SCREEN_WIDTH / 8, SCREEN_HEIGHT / 15,
                            'Retour', retour, police_boutons))
    liste_boutons.append(Bouton(screen,SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2, SCREEN_WIDTH / 8, SCREEN_HEIGHT / 15,
                                  f'Grids: {grid_mode_str}', toggle_grid, police_boutons))
    liste_boutons.append(Bouton(screen, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 100, SCREEN_WIDTH / 8, SCREEN_HEIGHT / 15,
                            'Quitter', quitter, police_boutons))

def toggle_grid() -> None:
    """
    Ajoute ou enlève la bordure des tuiles de la carte
    Args:
        None
    Returns:
        None
    """
    carte_jeu.grid_mode = not carte_jeu.grid_mode
    for bout in carte_jeu.liste_boutons:
        if isinstance(bout, Bouton) and 'Grids' in bout.texte:
            grid_mode_str = "ON" if carte_jeu.grid_mode else "OFF"
            bout.texte = f'Grids: {grid_mode_str}'
    menu_options()

def retour() -> None:
    """
    Ferme le menu secondaire
    Args:
        None
    Returns:
        None
    """
    global liste_boutons
    global in_menu_secondaire

    liste_boutons.clear()
    in_menu_secondaire = False

def quitter() -> None:
    """
    Retourne au menu principal
    Args:
        None
    Returns:
        None
    """
    global in_menu_principal
    global in_carte
    global in_nid
    global nids

    retour()
    nids.clear()
    in_menu_principal = True
    in_carte = False
    in_nid = False

def gestion_evenement(event: pygame.event) -> None:
    """
    Gère un événement du jeu et du menu principal
    Args:
        event (pygame.event): L'événement à gérer
    Returns:
        None
    """
    def gestion_menu_principal(event: pygame.event) -> None:
        """
        Gère un événement du menu principal
        Args:
            event (pygame.event): L'événement à gérer
        Returns:
            None
        """
        global selected_option
        global running

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                selected_option = (selected_option - 1) % len(liste_options)
            elif event.key == pygame.K_DOWN:
                selected_option = (selected_option + 1) % len(liste_options)
            elif event.key == pygame.K_RETURN:
                if selected_option == 0:
                    demarrer_jeu()
                elif selected_option == 1:
                    print("Options selected")
                elif selected_option == 2:
                    running = False

    def gestion_shortcuts_jeu(event: pygame.event) -> None:
        """
        Gère les shortcuts du jeu
        Args:
            event (pygame.event): L'événement à gérer
        Returns:
            None
        """
        global in_menu_secondaire

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                menu_options() if not in_menu_secondaire else retour()

    global running
    global in_carte
    global in_nid
    global current_nid

    if event.type == pygame.QUIT:
        running = False

    if in_menu_principal:
        gestion_menu_principal(event)
    else:
        gestion_shortcuts_jeu(event)

    if in_carte and not in_menu_secondaire:
        index_nid: int = carte_jeu.handle_event(event, screen)
        if index_nid != None:
            current_nid = nids[index_nid]
            in_carte = False
            in_nid = True
        
    elif in_nid and not in_menu_secondaire:
        return_to_map: bool = current_nid.handle_event(event)
        if return_to_map:
            in_nid = False
            in_carte = True
            current_nid = None

def demarrer_jeu() -> None:
    """
    Démarre le jeu en initialisant la carte et les nids
    Args:
        None
    Returns:
        None
    """
    global in_menu_principal
    global in_carte
    global carte_jeu
    global nids

    in_menu_principal = False
    in_carte = True

    carte_jeu = carte.Carte()
    graphes = nid.chargement(screen)
    for graphe in graphes:
        new_nid = nid.Nid(graphe)
        nids.append(new_nid)

def run() -> None:
    """
    Initialise le jeu et gère la boucle principale
    Args:
        None
    Returns:
        None
    """
    initialiser()

    while running:
        for event in pygame.event.get():
            gestion_evenement(event)
        
        dt = clock.tick(60)

        if carte_jeu != None:
            carte_jeu.colonie_joeur.process(clock.get_time())

        if in_menu_principal:
            fourmi.random_mouvement(dt)
            sprites.update(dt)

        draw()

if __name__ == "__main__":
    run()   
    pygame.quit()