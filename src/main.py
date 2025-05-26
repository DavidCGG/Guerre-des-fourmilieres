import ast
import os
import random
#import venv_setup

import pygame
import carte as carte
import affichage_nid as nid
from config import trouver_font, trouver_img
from config import WHITE, BLACK, YELLOW
from config import Bouton
from fourmi import FourmiTitleScreen, FourmiTitleScreenSprite, Fourmis

#Variables globales
screen: pygame.Surface = None
clock: pygame.time.Clock = pygame.time.Clock()

font = pygame.font.Font(trouver_font("LowresPixel-Regular.otf"), 74)
small_font = pygame.font.Font(trouver_font("LowresPixel-Regular.otf"), 36)
tiny_font = pygame.font.Font(trouver_font("LowresPixel-Regular.otf"), 18)
liste_boutons: list[Bouton] = []

running: bool = True
in_menu_principal: bool = True
in_menu_options: bool = False
in_menu_secondaire: bool = False
in_carte: bool = False
in_nid: bool = False
partie_en_cours: bool = False

#Variables de menu principal
selected_option: int = 0
liste_options_menu_principal = ["Nouvelle partie", "Options", "Quitter"]
liste_options_menu_options = ["Maximum framerate: ", "Fullscreen: ", "Retour"]

spritesheet: pygame.image = None
fourmi: FourmiTitleScreen = None
fourmi_sprite: FourmiTitleScreenSprite = None
sprites = pygame.sprite.Group()

#Variables du jeu
nb_colonies_nids: int = 2
carte_jeu: carte.Carte = None
nids: list[nid.Nid] = []
current_nid: nid.Nid = None
liste_fourmis: list[Fourmis] = []

#Fichier options.txt
max_framerate: int
fullscreen: bool
SCREEN_WIDTH: int
SCREEN_HEIGHT: int

gestion_en_pause_pour_text_input: bool = False
text_input: str = ""

def initialiser() -> None:
    global screen

    global spritesheet
    global fourmi
    global fourmi_sprite
    global sprites

    global liste_options_menu_options
    global max_framerate
    global fullscreen
    global SCREEN_WIDTH
    global SCREEN_HEIGHT

    #Création du fichier options.txt et lecture
    if not os.path.isfile(os.path.join(os.path.dirname(__file__), "..", "options.txt")):
        with open(os.path.join(os.path.dirname(__file__), "..", "options.txt"),"x") as fichier_options:
            fichier_options.write("max_framerate=60\nfullscreen=False\nSCREEN_WIDTH=1280\nSCREEN_HEIGHT=720")
        fichier_options.close()

    with open(os.path.join(os.path.dirname(__file__), "..", "options.txt"),"r") as fichier_options:
        max_framerate = int(fichier_options.readline().removeprefix("max_framerate="))
        fullscreen = ast.literal_eval(fichier_options.readline().removeprefix("fullscreen="))
        SCREEN_WIDTH = int(fichier_options.readline().removeprefix("SCREEN_WIDTH="))
        SCREEN_HEIGHT = int(fichier_options.readline().removeprefix("SCREEN_HEIGHT="))

    fichier_options.close()
    liste_options_menu_options[0] += str(max_framerate)
    liste_options_menu_options[1] += str(fullscreen)

    #Initialisation de pygame
    pygame.init()
    pygame.font.init()
    pygame.display.set_caption("Guerre des fourmillières")
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT),pygame.SCALED)
    if fullscreen:
        pygame.display.toggle_fullscreen()

    #Initialisation du menu principal
    spritesheet = pygame.image.load(trouver_img("Fourmis/sprite_sheet_fourmi_noire.png")).convert_alpha()
    if random.random() > 0.5:
        spritesheet.blit(pygame.image.load(trouver_img("Fourmis/habit_ouvriere.png")).convert_alpha(),(0,0))
    else:
        spritesheet.blit(pygame.image.load(trouver_img("Fourmis/habit_soldat.png")).convert_alpha(), (0, 0))
    icon = spritesheet.subsurface(pygame.Rect(0, 0, 32, 32))
    pygame.display.set_icon(icon)

    fourmi = FourmiTitleScreen(3 * screen.get_width() // 5, 3 * screen.get_height() // 5, screen,8)
    fourmi_sprite = FourmiTitleScreenSprite(fourmi, spritesheet, 32, 32, 8, 300)
    sprites.add(fourmi_sprite)

def draw(dt) -> None:
    def draw_carte() -> None:
        carte_jeu.draw(screen, dt)

        for colonie in carte_jeu.colonies:
            for fourmi in colonie.fourmis:
                if fourmi.current_colonie is None:
                    fourmi.draw_in_map(dt,screen,carte_jeu.camera)

    def draw_menu(liste_options) -> None:
        #Dessine le menu principal ou d'options
        screen.fill(BLACK)

        for i in range(len(liste_options)):
            y = screen.get_height() // 2 - (150 * (len(liste_options) - 1)) // 2 - small_font.get_height() // 2 + i * 150

            if i == selected_option:
                draw_text_menu(liste_options[i], font, 100, y)
            else:
                draw_text_menu(liste_options[i], small_font, 100, y)

        sprites.draw(screen)
        
    def draw_text_menu(text, font, x, y) -> None:
        textobj = font.render(text, False, WHITE)
        textrect = textobj.get_rect()
        textrect.topleft = (x, y)
        screen.blit(textobj, textrect)

    def draw_top_bar() -> None:
        global liste_boutons
        global current_zoom

        camera = carte_jeu.camera if in_carte else current_nid.camera

        if  not any(isinstance(bouton, Bouton) and bouton.texte == "Options" for bouton in liste_boutons):
            bouton = Bouton(screen, screen.get_width() - 100, 25, 100, 30, "Options", menu_options_overlay, pygame.font.Font(trouver_font("LowresPixel-Regular.otf"), 22))
            liste_boutons.append(bouton)

        pygame.draw.rect(screen, BLACK, (0, 0, screen.get_width(), 50))

        fps_info = tiny_font.render(f'FPS: {clock.get_fps():.0f}', False, YELLOW)
        zoom_info = tiny_font.render(f'Zoom: {camera.zoom * 100:.2f}%', False, YELLOW)
        current_zoom = camera.zoom
        screen.blit(fps_info, (10, 5))
        screen.blit(zoom_info, (10, 25))

        titre_message: str = None
        if in_carte:
            titre_message = f"Carte"
        elif in_nid and nids.index(current_nid) == 0:
            titre_message = f"Nid joueur"
        else:
            titre_message = f"Nid ennemi {nids.index(current_nid)}"

        titre = small_font.render(titre_message, False, WHITE)
        screen.blit(titre, (screen.get_width() / 2 - titre.get_width() / 2, 10))

    global liste_options_menu_options
    global liste_options_menu_principal

    if in_menu_principal:
        draw_menu(liste_options_menu_principal)
    elif in_menu_options:
        draw_menu(liste_options_menu_options)
    elif in_carte and not in_menu_secondaire:
        draw_carte()
    elif in_nid and not in_menu_secondaire:
        current_nid.draw(dt,screen, liste_fourmis, carte_jeu.colonies[0])

    if partie_en_cours:
        draw_top_bar()
        for bouton in liste_boutons:
            bouton.draw()

    pygame.display.update()

def menu_options_overlay() -> None:
    global liste_boutons
    global in_menu_secondaire

    in_menu_secondaire = True
    if in_carte:
        carte_jeu.camera.stop_drag()
    elif in_nid:
        current_nid.camera.stop_drag()

    surface = pygame.Surface((300, 400))
    surface.fill(BLACK)

    texte_render = pygame.font.Font(trouver_font("LowresPixel-Regular.otf"), 36).render("Options", False, WHITE)
    police_boutons = pygame.font.Font(trouver_font("LowresPixel-Regular.otf"), 30)

    surface.blit(texte_render, [surface.get_width() / 2 - texte_render.get_rect().width / 2, 10])
    screen.blit(surface, (screen.get_width() / 2 - 150, screen.get_height() / 2 - 250))

    grid_mode_str = "ON" if carte_jeu.grid_mode else "OFF"

    liste_boutons.append(Bouton(screen, screen.get_width() / 2, screen.get_height() / 2 - 100, screen.get_width() / 8, screen.get_height() / 15,'Retour', retour, police_boutons))
    liste_boutons.append(Bouton(screen,screen.get_width() / 2, screen.get_height() / 2, screen.get_width() / 8, screen.get_height() / 15,f'Grids: {grid_mode_str}', toggle_grid, police_boutons))
    liste_boutons.append(Bouton(screen, screen.get_width() / 2, screen.get_height() / 2 + 100, screen.get_width() / 8, screen.get_height() / 15,'Quitter', quitter, police_boutons))

def toggle_grid() -> None:
    carte_jeu.grid_mode = not carte_jeu.grid_mode
    for bout in carte_jeu.liste_boutons:
        if isinstance(bout, Bouton) and 'Grids' in bout.texte:
            grid_mode_str = "ON" if carte_jeu.grid_mode else "OFF"
            bout.texte = f'Grids: {grid_mode_str}'
    menu_options_overlay()

#Sort du menu secondaire
def retour() -> None:
    global liste_boutons
    global in_menu_secondaire

    liste_boutons.clear()
    in_menu_secondaire = False

#Retourne au menu principal
def quitter() -> None:
    global in_menu_principal
    global in_carte
    global in_nid
    global nids
    global in_menu_options
    global partie_en_cours

    retour()
    nids.clear()
    in_menu_principal = True
    in_carte = False
    in_nid = False
    in_menu_options = False
    partie_en_cours = False

def entrer_menu_option() -> None:
    #ouvre le menu option
    global in_menu_principal
    global in_carte
    global in_nid
    global in_menu_options
    global sprites

    in_menu_principal = False
    in_carte = False
    in_nid = False
    in_menu_options = True

def gestion_evenement(event: pygame.event) -> None:
    def gestion_menu_principal(event: pygame.event) -> None:
        global selected_option
        global running
        global liste_options_menu_principal
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                selected_option = (selected_option - 1) % len(liste_options_menu_principal)
            elif event.key == pygame.K_DOWN:
                selected_option = (selected_option + 1) % len(liste_options_menu_principal)
            elif event.key == pygame.K_RETURN:
                if selected_option == 0:
                    demarrer_jeu()
                elif selected_option == 1:
                    entrer_menu_option()
                elif selected_option == 2:
                    running = False

    def gestion_menu_options(event: pygame.event) -> None:
        global selected_option
        global running
        global max_framerate
        global fullscreen
        global liste_options_menu_options

        def write_option(option,value):
            string_nouveau_fichier=""
            with open(os.path.join(os.path.dirname(__file__), "..", "options.txt"), "r") as fichier_options_temp:
                ligne_temp=fichier_options_temp.readline()
                lignes=[]
                while ligne_temp:
                    lignes.append(ligne_temp)
                    ligne_temp = fichier_options_temp.readline()

                for ligne in lignes:
                    if ligne.startswith(option):
                        string_nouveau_fichier+=(option+"="+str(value))
                    else:
                        string_nouveau_fichier+=ligne
                    ligne=fichier_options_temp.readline()
                    string_nouveau_fichier = string_nouveau_fichier.rstrip()+"\n"

            string_nouveau_fichier=string_nouveau_fichier.rstrip()
            fichier_options_temp.close()

            with open(os.path.join(os.path.dirname(__file__), "..", "options.txt"), "w") as fichier_options_temp:
                fichier_options_temp.write(string_nouveau_fichier)
            fichier_options_temp.close()

        global gestion_en_pause_pour_text_input
        global text_input
        if not gestion_en_pause_pour_text_input:

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    selected_option = (selected_option - 1) % len(liste_options_menu_options)
                elif event.key == pygame.K_DOWN:
                    selected_option = (selected_option + 1) % len(liste_options_menu_options)
                elif event.key == pygame.K_RETURN:
                    if selected_option == 0:
                        text_input = ""
                        liste_options_menu_options[0] = "Maximum framerate: "
                        gestion_en_pause_pour_text_input = True
                    elif selected_option == 1:
                        fullscreen = not fullscreen
                        write_option("fullscreen",fullscreen)
                        liste_options_menu_options[1]="Fullscreen: "+str(fullscreen)
                        if fullscreen:
                            #pygame.display.set_mode((SCREEN_WIDTH,SCREEN_HEIGHT),pygame.FULLSCREEN,pygame.SCALED)
                            pygame.display.toggle_fullscreen()
                        else:
                            pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT),pygame.SCALED)

                    elif selected_option == 2:
                        quitter()
        else:
            if event.type == pygame.TEXTINPUT:
                if event.text.isdigit():
                    text_input += event.text
                    liste_options_menu_options[0] = "Maximum framerate: " + text_input
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_BACKSPACE:
                text_input = text_input[:-1]
                liste_options_menu_options[0] = "Maximum framerate: " + text_input
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                gestion_en_pause_pour_text_input=False
                write_option("max_framerate",text_input)
                max_framerate = int(text_input)

    def gestion_shortcuts_jeu(event: pygame.event) -> None:
        global in_menu_secondaire

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                menu_options_overlay() if not in_menu_secondaire else retour()

    global running
    global in_carte
    global in_nid
    global current_nid

    if event.type == pygame.QUIT:
        running = False

    if in_menu_principal:
        gestion_menu_principal(event)
    elif in_menu_options:
        gestion_menu_options(event)
    else:
        gestion_shortcuts_jeu(event)

    if in_carte and not in_menu_secondaire:
        index_nid: int = carte_jeu.handle_event(event, screen)
        if index_nid != None:
            current_nid = nids[index_nid]
            in_carte = False
            in_nid = True
        
    elif in_nid and not in_menu_secondaire:
        return_to_map: bool = current_nid.handle_event(event,screen,carte_jeu.colonies[0],liste_fourmis,carte_jeu.map_data,carte_jeu.colonies)
        if return_to_map:
            in_nid = False
            in_carte = True
            current_nid = None

def check_victory():
    def victory():
        global in_menu_secondaire
        global liste_boutons
        global carte_jeu
        global current_nid

        in_menu_secondaire = True
        if in_carte:
            carte_jeu.camera.stop_drag()
        elif in_nid:
            current_nid.camera.stop_drag()

        texte_render = pygame.font.Font(trouver_font("LowresPixel-Regular.otf"), 48).render("Vous avez gagné!", False, WHITE)
        police_boutons = pygame.font.Font(trouver_font("LowresPixel-Regular.otf"), 30)

        surface = pygame.Surface((int(texte_render.get_width() * 1.5), int(texte_render.get_height() * 1.5)))
        surface.fill(BLACK)

        surface.blit(texte_render, [surface.get_width() / 2 - texte_render.get_rect().width / 2, 10])
        screen.blit(surface, (screen.get_width() / 2 - surface.get_width() / 2, screen.get_height() / 2 - 250))

        liste_boutons.append(Bouton(screen, screen.get_width() / 2, screen.get_height() * 2 / 3 - 100, screen.get_width() / 8,screen.get_height() / 15, 'Quitter', quitter, police_boutons))

    def loss():
        global in_menu_secondaire
        global liste_boutons
        global carte_jeu
        global current_nid

        in_menu_secondaire = True
        if in_carte:
            carte_jeu.camera.stop_drag()
        elif in_nid:
            current_nid.camera.stop_drag()

        texte_render = pygame.font.Font(trouver_font("LowresPixel-Regular.otf"), 48).render("Vous avez perdu!",False, WHITE)
        police_boutons = pygame.font.Font(trouver_font("LowresPixel-Regular.otf"), 30)

        surface = pygame.Surface((int(texte_render.get_width()*1.5), int(texte_render.get_height()*1.5)))
        surface.fill(BLACK)

        surface.blit(texte_render, [surface.get_width() / 2 - texte_render.get_rect().width / 2, 10])
        screen.blit(surface, (screen.get_width() / 2 - surface.get_width()/2, screen.get_height() / 2 - 250))

        liste_boutons.append(Bouton(screen, screen.get_width() / 2, screen.get_height() * 2 / 3 - 100, screen.get_width() / 8,screen.get_height() / 15, 'Quitter', quitter, police_boutons))

    def remove_colonie(colonie):
        global liste_fourmis
        nonlocal nb_colonies_ennemies_mortes

        nb_colonies_ennemies_mortes += 1

        for fourmi_in_dead_colonie in colonie.fourmis:
            for fourmi_in_jeu in liste_fourmis:
                if fourmi_in_dead_colonie == fourmi_in_jeu:
                    liste_fourmis.remove(fourmi_in_jeu)

        colonie.fourmis = []
        colonie.stop_processing_salles_other_than_sortie_when_dead = True


    nb_colonies_ennemies_mortes = 0
    for i in range(len(carte_jeu.colonies)):
        if carte_jeu.colonies[i].hp > 0:
            continue

        if i == 0:
            loss()
        else:
            remove_colonie(carte_jeu.colonies[i])

    if nb_colonies_ennemies_mortes == (nb_colonies_nids - 1):
        victory()

def process(dt) -> None:
    if partie_en_cours:
        check_victory()
        for colonie in carte_jeu.colonies:
            colonie.process(clock.get_time(),nids,liste_fourmis,carte_jeu.colonies,carte_jeu.map_data)

    if in_menu_principal:
        fourmi.random_mouvement(dt)
        sprites.update(dt)

def demarrer_jeu() -> None:
    global in_menu_principal
    global in_carte
    global carte_jeu
    global nids
    global partie_en_cours
    global liste_fourmis

    in_menu_principal = False
    in_carte = True
    partie_en_cours = True

    graphes = nid.chargement(screen, nb_colonies_nids)
    carte_jeu = carte.Carte(nb_colonies_nids, screen, graphes, liste_fourmis)
    
    for i in range(nb_colonies_nids):
        new_nid = nid.Nid(graphes[i], screen, carte_jeu.colonies[i])
        nids.append(new_nid)

def run() -> None:
    initialiser()
    while running:
        dt = clock.tick(max_framerate)
        for event in pygame.event.get():
            gestion_evenement(event)
        process(dt)
        draw(dt)

if __name__ == "__main__":
    run()   
    pygame.quit()