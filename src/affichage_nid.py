import pygame
from pygame import Vector2

from camera import Camera
from generation_graphe import generer_graphe
from config import trouver_font, trouver_img, AQUA
from fourmi_types import Ouvriere, Soldat
from classes_graphe import TypeSalle
from colonies import Colonie

#Variables globales
MAP_LIMIT_X: int = 4000
MAP_LIMIT_Y: int = 2250
HAUTEUR_SOL: int = 128

class Nid:
    """
    Représente un des nids
    Attributs :
        graphe (Graphe): Graphe contenant les salles et tunnels du nid
        camera (Camera): Caméra pour le zoom et le déplacement
    """

    def __init__(self, graphe,screen,colonie_owner: Colonie):
        self.colonie_owner = colonie_owner
        self.tuile_debut = colonie_owner.tuile_debut
        self.graphe = graphe
        self.camera = Camera(screen.get_width(), screen.get_height(), MAP_LIMIT_X, MAP_LIMIT_Y)

        self.image_terre = pygame.image.load(trouver_img("Monde/terre.png"))
        self.image_terre_sombre = pygame.image.load(trouver_img("Monde/terre_sombre.png"))
        self.image_ciel = pygame.image.load(trouver_img("Monde/ciel32x32.png"))
        self.scale=4*screen.get_height()/720

        self.scale_images(self.scale)

        self.TILE_SIZE = self.image_terre.get_width()
        self.SKY_TILE_SIZE = self.image_ciel.get_width()

        self.salles_sorties=[]
        for salle in self.graphe.salles:
            if salle.type == TypeSalle.SORTIE:
                self.salles_sorties.append(salle)
                               
    def scale_images(self, scale, initial_sky_scaling = False) -> None:
        if initial_sky_scaling:
            facteur_ciel = HAUTEUR_SOL / self.image_ciel.get_height()
            self.image_ciel = pygame.transform.scale(self.image_ciel, (int(self.image_ciel.get_width() * facteur_ciel), int(self.image_ciel.get_height() * facteur_ciel)))
        else:
            self.image_ciel = pygame.transform.scale(self.image_ciel, (int(self.image_ciel.get_width() * scale), int(self.image_ciel.get_height() * scale)))

        self.image_terre = pygame.transform.scale(self.image_terre, (int(self.image_terre.get_width() * scale), int(self.image_terre.get_height() * scale)))
        self.image_terre_sombre = pygame.transform.scale(self.image_terre_sombre, (int(self.image_terre_sombre.get_width() * scale), int(self.image_terre_sombre.get_height() * scale)))

    def draw(self, dt, screen, liste_fourmis_jeu_complet, colonie_joueur) -> None:
        """
        Dessine tous les éléments du nid sur l'écran incluant l'arrière-plan
        Args:
            screen (pygame.Surface): La surface sur laquelle dessiner
        Returns:
            None
        """

        def draw_terre() -> None:
            for x in range(0, MAP_LIMIT_X, self.TILE_SIZE):
                for y in range(HAUTEUR_SOL, MAP_LIMIT_Y, self.TILE_SIZE):
                    screen_pos = self.camera.apply((x, y))
                    screen.blit(self.image_terre , screen_pos)

        def draw_ciel() -> None:
            for x in range(0, MAP_LIMIT_X, self.SKY_TILE_SIZE):
                screen_pos = self.camera.apply((x, 0))
                #screen_pos = (int(screen_pos[0]/2), int(screen_pos[1]/2))
                #screen_pos = (int(screen_pos[0]*720/screen.get_height()),int(screen_pos[1]*720/screen.get_height()))
                screen.blit(self.image_ciel, screen_pos)

        def draw_nid() -> None: 
            mask_surface = pygame.Surface((MAP_LIMIT_X, MAP_LIMIT_Y), pygame.SRCALPHA)
            mask_surface.fill((0, 0, 0, 0))

            buffer_images_top_layer=[]

            for salle in self.graphe.salles:
                pos = self.camera.apply(salle.noeud.coord)
                radius = salle.type.value[0] * self.camera.zoom
                pygame.draw.circle(mask_surface, (255, 255, 255, 255), pos, radius)

                #ajout de la texture spécifique au type au buffer
                if len(salle.type.value) > 2 and salle.type.value[2] is not None:
                    image_salle = pygame.image.load(salle.type.value[2])
                    image_salle = pygame.transform.scale(image_salle,(int(image_salle.get_width()*self.scale*self.camera.zoom),int(image_salle.get_height()*self.scale*self.camera.zoom)))
                    buffer_images_top_layer.append((image_salle, (pos[0]-image_salle.get_width()/2,pos[1]-image_salle.get_height()/2)))

            for tunnel in self.graphe.tunnels:
                start = self.camera.apply(tunnel.depart.noeud.coord)
                end = self.camera.apply(tunnel.arrivee.noeud.coord)
                width = int(tunnel.largeur * self.camera.zoom)
                pygame.draw.line(mask_surface, (255, 255, 255, 255), start, end, width)

            dug_surface = pygame.Surface((MAP_LIMIT_X, MAP_LIMIT_Y), pygame.SRCALPHA)
            for x in range(0, MAP_LIMIT_X, int(self.TILE_SIZE)):
                for y in range(0, MAP_LIMIT_Y, int(self.TILE_SIZE)):
                    screen_pos = self.camera.apply((x, y))
                    dug_surface.blit(self.image_terre_sombre , screen_pos)

            dug_surface.blit(mask_surface, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

            screen.blit(dug_surface, (0, 0))

            #draw buffer
            for image_et_pos in buffer_images_top_layer:
                screen.blit(image_et_pos[0],image_et_pos[1])

        def draw_fourmis() -> None:
            for fourmi in liste_fourmis_jeu_complet:
                if fourmi.current_colonie is not None and fourmi.current_colonie.tuile_debut == self.tuile_debut:
                    fourmi.draw_in_nid(dt,screen,self.camera)

        def draw_menu_salles():
            for salle in self.graphe.salles:
                if salle.menu_is_ouvert:
                    salle.draw_menu(screen, self.camera)

        draw_terre()
        draw_nid()
        draw_ciel()
        draw_fourmis()
        draw_menu_salles()
        colonie_joueur.update_menu()
        colonie_joueur.update_menu_fourmis()

        if colonie_joueur.menu_colonie_ouvert:
            colonie_joueur.menu_colonie()
        if colonie_joueur.menu_fourmis_ouvert:
            colonie_joueur.menu_fourmis()

    def handle_event(self, event, screen, colonie_joueur,liste_fourmis_jeu_complet,map_data,liste_toutes_colonies) -> bool:
        """
        Gère tous les événements liés au nid
        Args:
            event (pygame.event.Event): L'événement à gérer
        Returns:
            bool: True si le ciel a été cliqué pour sortir du nid, False sinon
        """

        def handle_left_click(pos):
            #menu colonie
            for key, rect in colonie_joueur.texte_rects.items():
                if rect.collidepoint(pos):
                    colonie_joueur.last_tab = colonie_joueur.curr_tab
                    if key == "Ouvrières":
                        colonie_joueur.curr_tab = "Ouvrières"
                    elif key == "Soldats":
                        colonie_joueur.curr_tab = "Soldats"
                    colonie_joueur.scroll_offset = 0
                    colonie_joueur.couleur_texte = AQUA
                    # On ferme le menu si on re clique sur le meme tab
                    colonie_joueur.menu_fourmis_ouvert = not colonie_joueur.menu_fourmis_ouvert if key == colonie_joueur.last_tab else True

                    colonie_joueur.menu_a_updater = True
                    colonie_joueur.menu_f_a_updater = True
                    return

            #menu fourmis
            if colonie_joueur.menu_fourmis_ouvert and colonie_joueur.menu_fourmis_rect.collidepoint(pos):
                rel_x = pos[0] - colonie_joueur.menu_fourmis_rect.x
                rel_y = pos[1] - colonie_joueur.menu_fourmis_rect.y + colonie_joueur.scroll_offset

                y_offset = 40
                if colonie_joueur.curr_tab == "Ouvrières":
                    fourmis_temp = [f for f in colonie_joueur.fourmis if isinstance(f, Ouvriere)]
                elif colonie_joueur.curr_tab == "Soldats":
                    fourmis_temp = [f for f in colonie_joueur.fourmis if isinstance(f, Soldat)]

                for fourmi in fourmis_temp:
                    rect = pygame.Rect(0, y_offset - 5, 250, 50)

                    if rect.collidepoint((rel_x, rel_y)):
                        if colonie_joueur.fourmis_selection == fourmi:
                            colonie_joueur.fourmis_selection = None

                        else:
                            colonie_joueur.fourmis_selection = fourmi

                        colonie_joueur.menu_f_a_updater = True
                        return

                    y_offset += 50
                return

            #ouvrir/fermer menu fourmi
            for fourmi in liste_fourmis_jeu_complet:
                if fourmi.current_colonie is None or fourmi.current_colonie.tuile_debut != self.tuile_debut:
                    continue
                if (Vector2(pos)-Vector2(self.camera.apply(fourmi.centre_in_nid))).magnitude() > 32*self.camera.zoom:
                    continue

                fourmi.menu_is_ouvert = not fourmi.menu_is_ouvert
                if fourmi == colonie_joueur.fourmis_selection:
                    colonie_joueur.fourmis_selection = None
                else:
                    colonie_joueur.fourmis_selection = fourmi

                keys = pygame.key.get_pressed()
                if keys[pygame.K_d]:
                    fourmi.digging = not fourmi.digging

                return

            for salle in self.graphe.salles:
                if (event.pos-Vector2(self.camera.apply(salle.noeud.coord))).magnitude() < salle.type.value[0]*self.camera.zoom:
                    salle.menu_is_ouvert = not salle.menu_is_ouvert

                if salle.type == TypeSalle.INDEFINI and salle.menu_is_ouvert and salle.menu_centre is not None:
                    pos_noeud = self.camera.apply(salle.noeud.coord)
                    largeur_menu = salle.menu_centre.get_width() * self.camera.zoom
                    hauteur_menu = salle.menu_centre.get_width() * self.camera.zoom
                    if ((pos_noeud[0] - largeur_menu < event.pos[0] and pos_noeud[0] + largeur_menu > event.pos[0])
                        and (pos_noeud[1] - hauteur_menu < event.pos[1] and pos_noeud[1] + hauteur_menu > event.pos[1])):
                        hauteur_case = hauteur_menu / len(salle.liste_types_salles)
                        index = 0
                        while pos_noeud[1] - hauteur_menu / 2 + index * hauteur_case < event.pos[1]:
                            index += 1

                        salle.type = salle.liste_types_salles[index - 1]
                        salle.type_specific_stats_update()
                        salle.menu_centre = None


        def handle_right_click(pos,map_data,liste_toutes_colonies):
            # set target of fourmi
            if colonie_joueur.fourmis_selection is not None:
                colonie_joueur.fourmis_selection.set_target_in_nid(self.camera.apply_inverse(pos),self,map_data,liste_toutes_colonies)
                return

        def handle_hover(pos):
            if colonie_joueur.menu_colonie_rect.collidepoint(pos):
                for key, rect in colonie_joueur.texte_rects.items():
                    if rect.collidepoint(pos):
                        colonie_joueur.hover_texte = key
                        colonie_joueur.menu_a_updater = True
                        colonie_joueur.update_menu()
                        return
                    else:
                        colonie_joueur.hover_texte = None
                        colonie_joueur.menu_a_updater = True
                        colonie_joueur.update_menu()

        def handle_scroll(dir, pos):
            if colonie_joueur.curr_tab == "Ouvrières":
                max_offset = max(0, colonie_joueur.nombre_ouvrieres() * 50 - 335)
            elif colonie_joueur.curr_tab == "Soldats":
                max_offset = max(0, colonie_joueur.nombre_soldats() * 50 - 335)

            if colonie_joueur.menu_fourmis_rect.collidepoint(pos):  # On scroll seulement si la souris est dans le rect du menu
                if dir == "up":
                    colonie_joueur.scroll_offset = max(0, colonie_joueur.scroll_offset - colonie_joueur.scroll_speed)
                elif dir == "down":
                    colonie_joueur.scroll_offset = min(max_offset, colonie_joueur.scroll_offset + colonie_joueur.scroll_speed)
                colonie_joueur.scrolling = True
                colonie_joueur.menu_f_a_updater = True
                colonie_joueur.update_menu_fourmis()
            else:
                colonie_joueur.scrolling = False

        if event.type == pygame.MOUSEBUTTONDOWN:
            x, y = event.pos
            if event.button == 1:  # Clic gauche
                handle_left_click(event.pos)
                self.camera.start_drag(*event.pos)
            elif event.button == 3:  # Clic droit
                handle_right_click(event.pos,map_data,liste_toutes_colonies)
                if y < HAUTEUR_SOL:
                    return True
            elif event.button == 4:  # Molette haut
                handle_scroll("up", event.pos)
                old_zoom = self.camera.zoom
                self.camera.zoom_camera(*event.pos, "in")
                self.scale_images(self.camera.zoom / old_zoom)
            elif event.button == 5:  # Molette bas
                handle_scroll("down", event.pos)
                old_zoom = self.camera.zoom
                self.camera.zoom_camera(*event.pos, "out")
                self.scale_images(self.camera.zoom / old_zoom)

        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                self.camera.stop_drag()

        elif event.type == pygame.MOUSEMOTION:
            handle_hover(event.pos)
            self.camera.drag(*event.pos)

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_q:
                colonie_joueur.menu_colonie_ouvert = not colonie_joueur.menu_colonie_ouvert


def chargement(screen: pygame.Surface, nb_nids: int) -> list:
    """Créer tous les graphes du jeu et affiche un écran de chargement"""

    def afficher_chargement(nb_genere, total):
        """Affiche l'écran de chargement"""
        screen.fill((30, 30, 30))

        titre = font.render("Création des nids", False, (255, 255, 255))
        progression = small_font.render(f"{nb_genere} sur {total}", False, (200, 200, 200))

        screen.blit(titre, (screen.get_width()//2 - titre.get_width()//2, screen.get_height()//2 - 100))
        screen.blit(progression, (screen.get_width()//2 - progression.get_width()//2, screen.get_height()//2))

        pygame.display.update()

    graphes = []

    font = pygame.font.Font(trouver_font("LowresPixel-Regular.otf"), 48)
    small_font = pygame.font.Font(trouver_font("LowresPixel-Regular.otf"), 32)

    for i in range(nb_nids):
        afficher_chargement(i+1, nb_nids)
        graphe = generer_graphe(HAUTEUR_SOL, MAP_LIMIT_X)
        graphes.append(graphe)

    return graphes