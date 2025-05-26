import math
from enum import Enum

import pygame
from pygame import Vector2

from config import trouver_img, trouver_font, WHITE, BLACK, TypeItem, CouleurFourmi
from fourmi_types import Ouvriere, Soldat

class NoeudGeneration:
    """Représente le noeud d'un graphe"""
    
    def __init__(self, nb = -1, voisins = None):
        self.nb: int = nb
        self.voisins: set[NoeudGeneration] = voisins if voisins is not None else set()

    def add_voisin(self, voisin) -> None:
        """Ajoute un voisin au noeud"""
        self.voisins.add(voisin)       

class NoeudPondere:
    """Représente un noeud dans un graphe pondéré 2D."""

    def __init__(self, coord = [-1,-1], voisins = None):
        self.coord: list[float, float] = coord
        self.voisins: dict[NoeudPondere: float] = voisins if voisins is not None else dict()

    def connecter_noeud(self, voisin) -> None:
        """Connecte le noeud à un voisin et l'inverse en initialisant la distance entre les deux noeuds"""
        
        distance = ((self.coord[0] - voisin.coord[0]) ** 2 + (self.coord[1] - voisin.coord[1]) ** 2) ** 0.5
        self.voisins[voisin] = distance
        voisin.voisins[self] = distance

    def add_voisin(self, voisin, poid = -1) -> None:
        """Ajoute un voisin au noeud"""

        self.voisins[voisin] = poid   
    
    def remove_voisin(self, voisin) -> None:
        """Supprime un voisin du noeud"""

        self.voisins.pop(voisin)

class TypeSalle(Enum):
    #Nom = (taille, nom, image)
    CONSTRUCTION = (40, "Construction", None) #Sert de type intermédiaire durant le digging
    INDEFINI = (40, "Indéfini", None)
    INTERSECTION = (40, "Intersection", None)
    SORTIE = (40, "Sortie", None)
    BANQUE = (128, "Banque", trouver_img("Salles/banque.png"))
    THRONE = (128, "Throne", trouver_img("Salles/throne.png"))
    ENCLUME = (128, "Enclume", trouver_img("Salles/enclume.png"))
    MEULE = (128, "Meule", trouver_img("Salles/meule.png"))
    TRAINING_OUVRIERE = (128, "Nurserie d'ouvrières", trouver_img("Salles/training_ouvriere.png"))
    TRAINING_SOLDAT = (128, "Nurserie de soldats", trouver_img("Salles/training_soldat.png"))

class Salle:
    """Représente une salle dans un graphe."""

    def __init__(self, noeud, tunnels = None, type = None):
        self.noeud: NoeudPondere = noeud
        self.tunnels: set[Tunnel] = set(tunnels) if tunnels is not None else set()
        self.type: TypeSalle = type

        self.menu_is_ouvert: bool = False
        self.menu_top = None
        self.menu_bottom = None
        self.menu_centre = None
        self.font_menu = pygame.font.Font(trouver_font("LowresPixel-Regular.otf"), 30)
        self.liste_images_cases_vides = []
        self.liste_images_items = []

        self.fourmi_qui_fait_action = None
        self.temps_pour_action = None
        self.temps_ecoule_depuis_debut_action = 0

        self.inventaire_taille_max = None
        self.inventaire = []
        self.inventaire_necessaire = None

        self.liste_types_salles = [
                    TypeSalle.INTERSECTION,
                    TypeSalle.BANQUE,
                    TypeSalle.ENCLUME,
                    TypeSalle.MEULE,
                    TypeSalle.TRAINING_OUVRIERE,
                    TypeSalle.TRAINING_SOLDAT
                ]

    def intersecte_salle(self, autre) -> bool:
        """
        Vérifie si deux salles se superposent.
        Args:
            autre (Salle): Autre salle à vérifier.
        Returns:
            bool: True si les salles se superposent, False sinon.
        """
        coord1 = self.noeud.coord
        coord2 = autre.noeud.coord

        distance = ((coord1[0] - coord2[0]) ** 2 + (coord1[1] - coord2[1]) ** 2) ** 0.5
        distance_min = self.type.value[0] + autre.type.value[0]

        return distance < distance_min

    def intersecte_tunnel(self, tunnel) -> bool:
        """
        Vérifie si une salle se superpose à un tunnel.
        Args:
            tunnel (Tunnel): Tunnel à vérifier.
        Returns:
            bool: True si la salle se superpose au tunnel, False sinon.
        """
        x1, y1 = tunnel.depart.noeud.coord
        x2, y2 = tunnel.arrivee.noeud.coord
        cx, cy = self.noeud.coord

        #Vecteur directeur de la droite
        droite = Vector2(x2 - x1, y2 - y1)

        #Vecteur entre le centre de la salle et le point de départ du tunnel
        droite_cercle = Vector2(cx - x1, cy - y1)

        #Rapport entre le vecteur directeur et
        #la projection du vecteur entre le centre de la salle et le point de départ du tunnel sur celui-ci
        t = max(0, min(1, (droite.x * droite_cercle.x + droite.y * droite_cercle.y) / (droite.x ** 2 + droite.y ** 2)))

        #Point le plus proche de la salle sur la droite
        closest_x = x1 + t * droite.x
        closest_y = y1 + t * droite.y

        #Distance au centre
        distance = ((closest_x - cx) ** 2 + (closest_y - cy) ** 2) ** 0.5
        rayon = self.type.value[0] + tunnel.largeur / 2

        return distance <= rayon

    def process(self, listes_fourmis_jeu_complet, colonie_owner_of_self, dt, map_data, liste_toutes_colonies):        
        if self.type == TypeSalle.INTERSECTION:
            return
        
        self.update_menu(colonie_owner_of_self)

        if self.fourmi_qui_fait_action is not None:
            self.verifier_action_timer(colonie_owner_of_self, listes_fourmis_jeu_complet, dt)
        
        if self.type == TypeSalle.THRONE:
            self.defense_automatique(colonie_owner_of_self, listes_fourmis_jeu_complet, map_data, liste_toutes_colonies)
            self.attaque_throne(listes_fourmis_jeu_complet, colonie_owner_of_self, dt)

    def attaque_throne(self, listes_fourmis_jeu_complet, colonie_owner_of_self, dt):
        for fourmi in listes_fourmis_jeu_complet:
            if fourmi.is_busy:
                continue
            if fourmi.current_salle != self:
                continue
            if fourmi.colonie_origine == colonie_owner_of_self:
                continue

            colonie_owner_of_self.hp -= (fourmi.atk_result * dt) / 1000
    
    def salle_fourmi_collision(self, fourmi, colonie_of_salle, dt):
        def collecte_item_selon_inventaire_necessaire(fourmi):
            item_collecte_index_in_inventaire_fourmi = None
            item_collecte_index_in_inventaire_salle = None

            for i in range(len(self.inventaire_necessaire)):
                if self.inventaire[i] is None:
                    for j in range(len(fourmi.inventaire)):
                        if fourmi.inventaire[j].name == self.inventaire_necessaire[i].name:
                            item_collecte_index_in_inventaire_fourmi = j
                            item_collecte_index_in_inventaire_salle = i

            if item_collecte_index_in_inventaire_fourmi is not None and item_collecte_index_in_inventaire_salle is not None:
                self.inventaire[item_collecte_index_in_inventaire_salle] = fourmi.inventaire.pop(item_collecte_index_in_inventaire_fourmi)
        
        def commencer_action(fourmi):
            if fourmi.is_busy and self.fourmi_qui_fait_action is None and self.inventaire == self.inventaire_necessaire:
                for f in colonie_of_salle.fourmis:
                    if f.current_salle == self and not f.is_busy:
                        self.fourmi_qui_fait_action = f
                        f.is_busy = True
                if colonie_of_salle.couleur_fourmi == CouleurFourmi.ROUGE and isinstance(fourmi,Ouvriere) and self.type in [TypeSalle.TRAINING_OUVRIERE, TypeSalle.TRAINING_SOLDAT]:
                    if self.inventaire == self.inventaire_necessaire and self.fourmi_qui_fait_action is None:
                        fourmi.target_in_map = None
                        fourmi.target_in_nid = None
                        self.fourmi_qui_fait_action = fourmi
                        fourmi.is_busy = True
            elif self.inventaire == self.inventaire_necessaire and self.fourmi_qui_fait_action is None:
                self.fourmi_qui_fait_action = fourmi
                fourmi.is_busy = True



                    
        if fourmi.colonie_origine == colonie_of_salle: # action if fourmi is in its own colonie
            if self.type == TypeSalle.BANQUE:
                if len(self.inventaire) < self.inventaire_taille_max and len(fourmi.inventaire) > 0:
                    self.inventaire.append(fourmi.inventaire.pop(0))

            elif self.type == TypeSalle.THRONE:
                collecte_item_selon_inventaire_necessaire(fourmi)
                commencer_action(fourmi)

            elif self.type == TypeSalle.ENCLUME:
                collecte_item_selon_inventaire_necessaire(fourmi)
                commencer_action(fourmi)

            elif self.type == TypeSalle.MEULE:
                collecte_item_selon_inventaire_necessaire(fourmi)
                commencer_action(fourmi)

            elif self.type == TypeSalle.TRAINING_OUVRIERE:
                collecte_item_selon_inventaire_necessaire(fourmi)
                commencer_action(fourmi)

            elif self.type == TypeSalle.TRAINING_SOLDAT:
                collecte_item_selon_inventaire_necessaire(fourmi)
                commencer_action(fourmi)
        
        if self.type == TypeSalle.SORTIE and fourmi.bouge_depuis_transition == True: #action if fourmi in either               
            fourmi.current_colonie = None
            fourmi.centre_in_map = colonie_of_salle.tuile_debut

            fourmi.centre_in_nid = None
            fourmi.target_in_nid = None
            fourmi.path = []

            fourmi.bouge_depuis_transition = False

            if fourmi.target_in_map is not None:
                fourmi.bouge_depuis_transition = True

        elif fourmi.bouge_depuis_transition == False:
            fourmi.bouge_depuis_transition = True

    def type_specific_stats_update(self):
        if self.type == TypeSalle.BANQUE:
            self.inventaire_taille_max = 10

        elif self.type == TypeSalle.THRONE:
            self.inventaire_necessaire = [TypeItem.POMME, TypeItem.POMME]
            self.inventaire = [None,None]
            self.temps_pour_action = 5000

        elif self.type == TypeSalle.ENCLUME:
            self.inventaire_necessaire = [TypeItem.METAL, TypeItem.METAL]
            self.inventaire = [None, None]
            self.temps_pour_action = 5000

        elif self.type == TypeSalle.MEULE:
            self.inventaire_necessaire = [TypeItem.METAL, TypeItem.METAL]
            self.inventaire = [None, None]
            self.temps_pour_action = 5000

        elif self.type == TypeSalle.TRAINING_OUVRIERE:
            self.inventaire_necessaire = [TypeItem.POMME, TypeItem.BOIS, TypeItem.OEUF]
            self.inventaire = [None, None, None]
            self.temps_pour_action = 5000

        elif self.type == TypeSalle.TRAINING_SOLDAT:
            self.inventaire_necessaire = [TypeItem.POMME, TypeItem.METAL, TypeItem.OEUF]
            self.inventaire = [None, None, None]
            self.temps_pour_action = 5000

        elif self.type == TypeSalle.CONSTRUCTION:
            self.temps_pour_action = 10_000

    def verifier_action_timer(self, colonie_owner_of_self, listes_fourmis_jeu_complet, dt):
        self.temps_ecoule_depuis_debut_action += dt
        if self.temps_ecoule_depuis_debut_action >= self.temps_pour_action:
            if self.type == TypeSalle.THRONE:
                self.inventaire = [None,None]
                self.fourmi_qui_fait_action.inventaire.append(TypeItem.OEUF)

            elif self.type == TypeSalle.ENCLUME:
                self.inventaire = [None,None]
                self.fourmi_qui_fait_action.inventaire.append(TypeItem.ARMURE)

            elif self.type == TypeSalle.MEULE:
                self.inventaire = [None,None]
                self.fourmi_qui_fait_action.inventaire.append(TypeItem.EPEE)

            elif self.type == TypeSalle.TRAINING_OUVRIERE:
                self.inventaire = [None, None, None]
                nouvelle_fourmi = Ouvriere(self.noeud.coord[0], self.noeud.coord[1], colonie_owner_of_self.couleur_fourmi, colonie_owner_of_self, self)
                colonie_owner_of_self.fourmis.append(nouvelle_fourmi)
                listes_fourmis_jeu_complet.append(nouvelle_fourmi)

            elif self.type == TypeSalle.TRAINING_SOLDAT:
                self.inventaire = [None, None, None]
                nouvelle_fourmi = Soldat(self.noeud.coord[0], self.noeud.coord[1], colonie_owner_of_self.couleur_fourmi,colonie_owner_of_self, self)
                colonie_owner_of_self.fourmis.append(nouvelle_fourmi)
                listes_fourmis_jeu_complet.append(nouvelle_fourmi)

            elif self.type == TypeSalle.CONSTRUCTION:
                self.type = TypeSalle.INDEFINI
                self.type_specific_stats_update()

            self.fourmi_qui_fait_action.is_busy = False
            self.fourmi_qui_fait_action = None
            self.temps_ecoule_depuis_debut_action = 0

    def defense_automatique(self, colonie_owner_of_self, listes_fourmis_jeu_complet, map_data, liste_toutes_colonies):
        fourmis_a_target = []
        fourmis_defenders = []

        for fourmi in listes_fourmis_jeu_complet:
            if fourmi.current_colonie is not None and fourmi.current_colonie == colonie_owner_of_self and fourmi.colonie_origine != colonie_owner_of_self: #find all enemys in nid
                fourmis_a_target.append(fourmi)

        for fourmi_defender in colonie_owner_of_self.fourmis:
            if (not fourmi_defender.is_busy or fourmi_defender.is_attacking_for_defense_automatique) and fourmi_defender.current_colonie is not None and fourmi_defender.current_colonie == colonie_owner_of_self:
                fourmis_defenders.append(fourmi_defender)

        if len(fourmis_a_target) > 0 and len(fourmis_defenders) > 0:
            for i in range(len(fourmis_defenders)):
                fourmis_defenders[i].set_attack(fourmis_a_target[i % len(fourmis_a_target)],map_data,liste_toutes_colonies)
                fourmis_defenders[i].is_attacking_for_defense_automatique = True
        
        elif len(fourmis_a_target) == 0:
            for fourmi_defender in fourmis_defenders:
                if fourmi_defender.is_attacking_for_defense_automatique:
                    fourmi_defender.fourmi_attacking = None
                    fourmi_defender.is_attacking_for_defense_automatique = False
                    fourmi_defender.is_busy = False

                    fourmi_defender.target_in_nid = None
                    fourmi_defender.target_in_nid_queued = None
                    fourmi_defender.target_in_map = None

    def on_click_action(self):
        self.menu_is_ouvert = not self.menu_is_ouvert

    def update_menu(self, colonie_owner_of_self):
        def update_menu_centre():
            # Menu settings
            button_width = 150
            button_height = 40
            padding = 5

            menu_height = len(self.liste_types_salles) * (button_height + padding) + padding
            menu_width = button_width + 2 * padding

            # Create the menu surface
            self.menu_centre = pygame.Surface((menu_width, menu_height), pygame.SRCALPHA)
            self.menu_centre.fill(WHITE)

            font = pygame.font.Font(trouver_font("LowresPixel-Regular.otf"), 16)

            for i, salle_type in enumerate(self.liste_types_salles):
                btn_x = padding
                btn_y = padding + i * (button_height + padding)
                btn_rect = pygame.Rect(btn_x, btn_y, button_width, button_height)

                # Render label
                label = font.render(salle_type.value[1], True, (0, 0, 0))
                label_rect = label.get_rect(center=btn_rect.center)
                self.menu_centre.blit(label, label_rect)

        def update_menu_top():
            if self.inventaire_taille_max is not None:
                case_inventaire = pygame.Surface((100, 100))
                case_inventaire.fill(WHITE)
                if self.inventaire_taille_max <= 5:
                    self.menu_top = pygame.Surface((5 + self.inventaire_taille_max * (100 + 5), 5 + 100 + 5))
                    self.menu_top.fill(BLACK)
                    for i in range(self.inventaire_taille_max):
                        self.menu_top.blit(case_inventaire, (5 + i * (100 + 5), 5))
                    for i in range(len(self.inventaire)):
                        image_item = pygame.transform.scale(pygame.image.load(self.inventaire[i].value[1]), (100, 100))
                        self.menu_top.blit(image_item, (5 + i * (100 + 5), 5))
                elif self.inventaire_taille_max <= 10:
                    self.menu_top = pygame.Surface((5 + 5 * (100 + 5), 5 + 2 * (100 + 5)))
                    self.menu_top.fill(BLACK)
                    for i in range(self.inventaire_taille_max):
                        self.menu_top.blit(case_inventaire,
                                            (5 + (i % 5) * (100 + 5), 5 + math.floor(i / 5) * (100 + 5)))
                    for i in range(len(self.inventaire)):
                        image_item = pygame.transform.scale(pygame.image.load(self.inventaire[i].value[1]), (100, 100))
                        self.menu_top.blit(image_item, (5 + (i % 5) * (100 + 5), 5 + math.floor(i / 5) * (100 + 5)))
                elif self.inventaire_taille_max <= 15:
                    self.menu_top = pygame.Surface((5 + 5 * (100 + 5), 5 + 3 * (100 + 5)))
                    self.menu_top.fill(BLACK)
                    for i in range(self.inventaire_taille_max):
                        self.menu_top.blit(case_inventaire,
                                            (5 + (i % 5) * (100 + 5), 5 + math.floor(i / 5) * (100 + 5)))
                    for i in range(len(self.inventaire)):
                        image_item = pygame.transform.scale(pygame.image.load(self.inventaire[i].value[1]), (100, 100))
                        self.menu_top.blit(image_item, (5 + (i % 5) * (100 + 5), 5 + math.floor(i / 5) * (100 + 5)))
                elif self.inventaire_taille_max <= 20:
                    self.menu_top = pygame.Surface((5 + 5 * (100 + 5), 5 + 4 * (100 + 5)))
                    self.menu_top.fill(BLACK)
                    for i in range(self.inventaire_taille_max):
                        self.menu_top.blit(case_inventaire,
                                            (5 + (i % 5) * (100 + 5), 5 + math.floor(i / 5) * (100 + 5)))
                    for i in range(len(self.inventaire)):
                        image_item = pygame.transform.scale(pygame.image.load(self.inventaire[i].value[1]), (100, 100))
                        self.menu_top.blit(image_item, (5 + (i % 5) * (100 + 5), 5 + math.floor(i / 5) * (100 + 5)))
            elif self.inventaire_necessaire is not None:
                self.menu_top = pygame.Surface((5 + len(self.inventaire_necessaire) * (100 + 5), 5 + 100 + 5))
                self.menu_top.fill(BLACK)
                for i in range(len(self.inventaire_necessaire)):
                    self.menu_top.blit(pygame.transform.scale(pygame.image.load(self.inventaire_necessaire[i].value[2]),(100,100)), (5 + i * (100 + 5), 5))
                    if self.inventaire[i] is not None:
                        if self.inventaire[i]==self.inventaire_necessaire[i]:
                            self.menu_top.blit(pygame.transform.scale(pygame.image.load(self.inventaire_necessaire[i].value[1]),(100, 100)), (5 + i * (100 + 5), 5))
        
        def update_menu_bottom():#only colonie hp for throne
            self.menu_bottom = pygame.Surface((125, 50))
            text_surface = self.font_menu.render("HP: " + str(colonie_owner_of_self.hp), False, WHITE)
            self.menu_bottom.blit(text_surface, (self.menu_bottom.get_height() / 2 - text_surface.get_height() / 2,self.menu_bottom.get_height() / 2 - text_surface.get_height() / 2))

        if self.menu_is_ouvert:
            if self.type == TypeSalle.THRONE:
                update_menu_bottom()
            if self.type == TypeSalle.INDEFINI:
                update_menu_centre()
            if self.type != TypeSalle.INDEFINI:
                update_menu_top()

    def draw_menu(self,screen,camera):
        def draw_menu_top():
            menu_transformed=pygame.transform.scale(self.menu_top, (self.menu_top.get_width() * camera.zoom, self.menu_top.get_height() * camera.zoom))
            screen.blit(menu_transformed, camera.apply((self.noeud.coord[0] - self.menu_top.get_width() / 2, self.noeud.coord[1] - self.type.value[0] - self.menu_top.get_height())))
        def draw_menu_bottom():
            menu_transformed = pygame.transform.scale(self.menu_bottom, (self.menu_bottom.get_width() * camera.zoom, self.menu_bottom.get_height() * camera.zoom))
            screen.blit(menu_transformed, camera.apply((self.noeud.coord[0] - self.menu_bottom.get_width() / 2,self.noeud.coord[1] + self.type.value[0])))
        def draw_menu_centre():
            menu_transformed = pygame.transform.scale(self.menu_centre, (self.menu_centre.get_width() * camera.zoom, self.menu_centre.get_height() * camera.zoom))
            screen.blit(menu_transformed, camera.apply((self.noeud.coord[0] - self.menu_centre.get_width() / 2,self.noeud.coord[1] - self.menu_centre.get_height()/2)))
        
        if self.menu_top is not None:
            draw_menu_top()
        if self.menu_bottom is not None:
            draw_menu_bottom()
        if self.menu_centre is not None:
            draw_menu_centre()
   
class Tunnel:
    """
    Représente un tunnel entre deux salles dans un graphe.
    Attributs :
        depart (Salle) : Une première salle reliée au tunnel.
        arrivee (Salle) : Une seconde salle reliée au tunnel.
        largeur (int) : Largeur du tunnel.
    """
    def __init__(self, depart = None, arrivee = None, largeur = 80):
        """
        Constructeur de la classe Tunnel. Ajoute le tunnel aux salles et connecte leurs noeuds.
        Args:
            depart (Salle): Salle de départ.
            arrivee (Salle): Salle d'arrivée.
            largeur (int): Largeur du tunnel.
        """
        self.depart: Salle = depart
        self.arrivee: Salle = arrivee
        self.largeur: int = largeur

        depart.tunnels.add(self)
        arrivee.tunnels.add(self)
        depart.noeud.connecter_noeud(arrivee.noeud)
    
    def intersecte(self, autre) -> bool:
        """
        Vérifie si deux tunnels se superposent.
        Args:
            autre (Tunnel): Autre tunnel à vérifier.
        Returns:
            bool: True si les tunnels se superposent, False sinon.
        """
        def get_rectangle(tunnel) -> tuple[int, int, int, int]:
            """
            Crée un rectangle représentant le tunnel.
            Args:
                tunnel (Tunnel): Tunnel à représenter.
            Returns:
                list[Vector2]: Liste de points représentant les coins du rectangle.
            """
            scale_largeur: float = 2 #Sert à bien espacer les tunnels

            direction: Vector2 = Vector2(tunnel.arrivee.noeud.coord[0] - tunnel.depart.noeud.coord[0],
                                         tunnel.arrivee.noeud.coord[1] - tunnel.depart.noeud.coord[1]).normalize()
            normal: Vector2 = Vector2(-direction.y, direction.x)
            offset: Vector2 = normal * (scale_largeur * self.largeur / 2)

            p1 = Vector2(tunnel.depart.noeud.coord) + offset
            p2 = Vector2(tunnel.arrivee.noeud.coord) + offset
            p3 = Vector2(tunnel.arrivee.noeud.coord) - offset
            p4 = Vector2(tunnel.depart.noeud.coord) - offset

            return [p1, p2, p3, p4]
        
        def intersection_segments(a1, a2, b1, b2):
            """
            Vérifie si deux segments de droite se croisent. Utilise la fonction ccw pour déterminer l'orientation des points.
            Args:
                a1 (Vector2): Premier point du premier segment.
                a2 (Vector2): Deuxième point du premier segment.
                b1 (Vector2): Premier point du deuxième segment.
                b2 (Vector2): Deuxième point du deuxième segment.
            Returns:
                bool: True si les segments se croisent, False sinon.
            """
            def ccw(p1, p2, p3):
                return (p3.y - p1.y) * (p2.x - p1.x) > (p2.y - p1.y) * (p3.x - p1.x)
            
            return ccw(a1, b1, b2) != ccw(a2, b1, b2) and ccw(b1, a1, a2) != ccw(b2, a1, a2)
        
        rect1 = get_rectangle(self)
        rect2 = get_rectangle(autre)

        for i in range(len(rect1)):
            a1 = rect1[i]
            a2 = rect1[(i + 1) % len(rect1)]
            for j in range(len(rect2)):
                b1 = rect2[j]
                b2 = rect2[(j + 1) % len(rect2)]
                if intersection_segments(a1, a2, b1, b2):
                    return True
                
        return False
        
class Graphe:
    """
    Représente un graphe de salles et de tunnels.
    Attributs :
        salles (set[Salle]) : Ensemble des salles du graphe.
        tunnels (set[Tunnel]) : Ensemble des tunnels du graphe.
    """
    def __init__(self, salles = None, tunnels = None):
        self.salles: set[Salle] = salles if salles is not None else set()
        self.tunnels: set[Tunnel] = tunnels if tunnels is not None else set()

    def get_noeud_at_coord(self, coord: list[float, float]) -> NoeudPondere:
        """
        Retourne le noeud correspondant aux coordonnées données.
        Args:
            coord (list[float, float]): Coordonnées d'un point sur le graphe.
        Returns:
            NoeudPondere: Noeud correspondant aux coordonnées ou None si non trouvé.
        """
        for salle in self.salles:
            coord_salle = salle.noeud.coord

            distance = ((coord[0] - coord_salle[0])**2 + (coord[1] - coord_salle[1])**2) ** 0.5
            distance_min = salle.type.value[0]

            if distance < distance_min:
                return salle.noeud

        return None
    
    def get_coord_in_tunnel_at_coord(self, coord: list[float, float]) -> tuple[Tunnel, list[float, float]]:
        cx, cy = coord

        for tunnel in self.tunnels:
            x1, y1 = tunnel.depart.noeud.coord
            x2, y2 = tunnel.arrivee.noeud.coord

            #Vecteur directeur de la droite
            droite = Vector2(x2 - x1, y2 - y1)

            #Vecteur entre le centre de la salle et le point de départ du tunnel
            droite_cercle = Vector2(cx - x1, cy - y1)

            #Rapport entre le vecteur directeur et
            #la projection du vecteur entre le centre de la salle et le point de départ du tunnel sur celui-ci
            t = max(0, min(1, (droite.x * droite_cercle.x + droite.y * droite_cercle.y) / (droite.x ** 2 + droite.y ** 2)))

            #Point le plus proche de la salle sur la droite
            closest_x = x1 + t * droite.x
            closest_y = y1 + t * droite.y

            #Distance au centre
            distance = ((closest_x - cx) ** 2 + (closest_y - cy) ** 2) ** 0.5

            if distance <= tunnel.largeur / 2:
                return tunnel, (closest_x, closest_y)
            
        return None

    def initialiser_graphe(self, noeuds: list[NoeudPondere]) -> None:
        """
        Initialise le graphe en connectant les noeuds et en créant les salles et tunnels.
        Args:
            noeuds (list[NoeudPondere]): Liste de noeuds à initialiser.
        Returns:
            None
        """
        def connecter_noeuds(noeuds) -> None:
            """
            Connecte les noeuds entre eux en ajoutant des voisins.
            Args:
                noeuds (list[NoeudPondere]): Liste de noeuds à connecter.
            Returns:
                None
            """
            for noeud in noeuds:
                for voisin in noeud.voisins:
                    noeud.connecter_noeud(voisin)

        def initialiser_salles(self, noeuds, lien_noeud_salle) -> None:
            """
            Initialise les salles en fonction des noeuds.
            Args:
                noeuds (list[NoeudPondere]): Liste de noeuds à initialiser.
                lien_noeud_salle (dict[NoeudPondere, Salle]): Dictionnaire liant les noeuds aux salles.
            Returns:
                None
            """
            for noeud in noeuds:
                salle = Salle(noeud)

                if len(salle.noeud.voisins) == 1: #Salle
                    salle.type = TypeSalle.INDEFINI
                else: #Intersection
                    salle.type = TypeSalle.INTERSECTION

                self.salles.add(salle)
                lien_noeud_salle[noeud] = salle
        
        def initialiser_tunnels(self, noeuds, lien_noeud_salle) -> None:
            """
            Initialise les tunnels en fonction des noeuds.
            Args:
                noeuds (list[NoeudPondere]): Liste de noeuds à initialiser.
                lien_noeud_salle (dict[NoeudPondere, Salle]): Dictionnaire liant les noeuds aux salles.
            Returns:
                None
            """
            visited = set()

            for noeud in noeuds:
                for voisin in noeud.voisins:
                    if voisin in visited:
                        continue

                    self.tunnels.add(Tunnel(lien_noeud_salle[noeud], lien_noeud_salle[voisin]))
                visited.add(noeud)

        lien_noeud_salle = dict()
        connecter_noeuds(noeuds)
        initialiser_salles(self, noeuds, lien_noeud_salle)
        initialiser_tunnels(self, noeuds, lien_noeud_salle)

    def verifier_graphe(self, scale, HAUTEUR_SOL) -> bool:
        """
        Vérifie si le graphe respecte les contraintes de superposition et de nombre de salles.
        Args:
            None
        Returns:
            bool: True si le graphe est valide, False sinon.
        """
        def verifier_nombre_salles() -> bool:
            """
            Vérifie si le nombre de salles autre que des intersections ou des sorties est compris entre 2 et 5.
            Args:
                None
            Returns:
                bool: True si le nombre de salles est valide, False sinon.
            """
            nb_salles: int = 0

            for salle in self.salles:
                if salle.type == TypeSalle.INTERSECTION or salle.type == TypeSalle.SORTIE:
                    continue
                nb_salles += 1

            return 2 <= nb_salles <= 4
        
        def verifier_longueur_tunnels(scale) -> bool:
            """
            Vérifie si les tunnels sont suffisamment longs.
            Args:
                None
            Returns:
                bool: True si les tunnels sont suffisament long, False sinon.
            """
            for tunnel in self.tunnels:
                longueur = ((tunnel.depart.noeud.coord[0] - tunnel.arrivee.noeud.coord[0]) ** 2 +
                            (tunnel.depart.noeud.coord[1] - tunnel.arrivee.noeud.coord[1]) ** 2) ** 0.5
                if longueur / scale < 1.5:
                    return False
            return True
        
        def verifier_angle_tunnels() -> bool:
            """
            Vérifie si les tunnels adjacents sont trop proches.
            Args:
                None
            Returns:
                bool: True si les tunnels adjacents ne sont pas trop proches, False sinon."""
            for tunnel1 in self.tunnels:
                for tunnel2 in self.tunnels:
                    if tunnel1 == tunnel2:
                        continue

                    if not (tunnel1.depart in (tunnel2.depart, tunnel2.arrivee) or 
                        tunnel1.arrivee in (tunnel2.depart, tunnel2.arrivee)):
                        continue

                    direction1: Vector2 = Vector2(tunnel1.arrivee.noeud.coord[0] - tunnel1.depart.noeud.coord[0],
                                            tunnel1.arrivee.noeud.coord[1] - tunnel1.depart.noeud.coord[1]).normalize()
                    direction2: Vector2 = Vector2(tunnel2.arrivee.noeud.coord[0] - tunnel2.depart.noeud.coord[0],
                                            tunnel2.arrivee.noeud.coord[1] - tunnel2.depart.noeud.coord[1]).normalize()
                    angle = direction1.angle_to(direction2)

                    if abs(angle) < 25:
                        return False
                    
            return True
        
        def verifier_sous_terre(HAUTEUR_SOL) -> bool:
            """
            Vérifie si les salles sont sous terre.
            Args:
                HAUTEUR_SOL (float): Hauteur du sol.
            Returns:
                bool: True si les salles sont sous terre, False sinon.
            """
            for salle in self.salles:
                if salle.type == TypeSalle.SORTIE:
                    continue

                if salle.noeud.coord[1] - salle.type.value[0] < HAUTEUR_SOL + HAUTEUR_SOL / 10:
                    return False
                
            return True
        
        def verifier_superpositions() -> bool:
            """
            Vérifie si les salles et tunnels se superposent.
            Args:
                None
            Returns:
                bool: True si les salles et les tunnels ne se supperposent pas, False sinon.
            """
            for salle1 in self.salles:
                for salle2 in self.salles:
                    if salle1 == salle2:
                        continue

                    if salle1.intersecte_salle(salle2):
                        return False    

            for tunnel1 in self.tunnels:
                for tunnel2 in self.tunnels:
                    if (tunnel1.depart in (tunnel2.depart, tunnel2.arrivee) or 
                        tunnel1.arrivee in (tunnel2.depart, tunnel2.arrivee)):
                        continue

                    if tunnel1.intersecte(tunnel2):
                        return False
                    
            for salle in self.salles:
                for tunnel in self.tunnels:
                    if tunnel in salle.tunnels:
                        continue

                    if salle.intersecte_tunnel(tunnel):
                        return False
                    
            return True
        
        valide: bool = True
        valide = valide and verifier_nombre_salles()
        valide = valide and verifier_longueur_tunnels(scale)
        valide = valide and verifier_angle_tunnels()
        valide = valide and verifier_sous_terre(HAUTEUR_SOL)
        valide = valide and verifier_superpositions()
        return valide
    
    def add_salle(self, salle: Salle, voisins:list[Salle]) -> None:
        """
        Ajoute une salle au graphe et creer les tunnels entre la salle et ses voisins.
        Args:
            salle (Salle): Salle à ajouter.
            voisins (list[Salle]): Liste de salles voisines.
        Returns:
            None
        """
        self.salles.add(salle)
        for voisin in voisins:
            tunnel = Tunnel(salle, voisin)
            self.tunnels.add(tunnel)

    def creer_salle_depuis_intersection(self, salle: Salle, coord_arrivee: list[float, float], fourmi) -> bool:
        """Crée une nouvelle salle à partir d'une intersection et d'une coordonnée d'arrivée."""
        
        if salle.type != TypeSalle.INTERSECTION:
            return False

        #Initialisation de la nouvelle salle
        noeud_salle = NoeudPondere(coord_arrivee)
        salle_indefinie = Salle(noeud_salle, type = TypeSalle.CONSTRUCTION)
        nouveau_tunnel = Tunnel(salle, salle_indefinie)

        #Vérifier si la nouvelle salle est valide
        for salle_graphe in self.salles:
            if salle_graphe == fourmi.current_salle:
                continue

            if salle_indefinie.intersecte_salle(salle_graphe):
                return False
            
        for tunnel_graphe in self.tunnels:
            if tunnel_graphe in fourmi.current_salle.tunnels:
                continue

            if salle_indefinie.intersecte_tunnel(tunnel_graphe):
                return False
            if nouveau_tunnel.intersecte(tunnel_graphe):
                return False

        salle_indefinie.type_specific_stats_update()
        salle_indefinie.fourmi_qui_fait_action = fourmi
        self.salles.add(salle_indefinie)
        self.tunnels.add(nouveau_tunnel)

        return True

    def creer_salle_depuis_tunnel(self, tunnel: Tunnel, coord_depart: list[float, float], coord_arrivee, fourmi) -> bool:     
        """Crée une nouvelle salle à partir d'un tunnel, du point de départ dans le tunnel et des coordonnées de la nouvelle salle."""

        #Initialisation des nouvelles salles
        noeud_intersection = NoeudPondere(coord_depart)
        salle_intersection = Salle(noeud_intersection, type = TypeSalle.INTERSECTION)

        noeud_salle = NoeudPondere(coord_arrivee)
        salle_indefinie = Salle(noeud_salle, type = TypeSalle.CONSTRUCTION)
        nouveau_tunnel = Tunnel(salle_intersection, salle_indefinie)

        #Vérifier si la nouvelle salle est valide
        for salle_graphe in self.salles:
            if salle_graphe == fourmi.current_salle:
                continue

            if salle_indefinie.intersecte_salle(salle_graphe):
                return False
            
        for tunnel_graphe in self.tunnels:
            if tunnel_graphe in fourmi.current_salle.tunnels:
                continue

            if salle_indefinie.intersecte_tunnel(tunnel_graphe):
                return False
            if nouveau_tunnel.intersecte(tunnel_graphe):
                return False

        salle_indefinie.type_specific_stats_update()
        salle_indefinie.fourmi_qui_fait_action = fourmi

        self.salles.add(salle_intersection)
        self.salles.add(salle_indefinie)

        #Déconnexion des noeuds
        tunnel.depart.noeud.remove_voisin(tunnel.arrivee.noeud)
        tunnel.arrivee.noeud.remove_voisin(tunnel.depart.noeud)

        #Suppression des tunnels
        self.tunnels.remove(tunnel)
        for s in self.salles:
            for t in s.tunnels:
                if t == tunnel:
                    s.tunnels.remove(t)
                    break
        
        #Création des nouveaux tunnels
        self.tunnels.add(Tunnel(tunnel.depart, salle_intersection))
        self.tunnels.add(Tunnel(tunnel.arrivee, salle_intersection))
        self.tunnels.add(nouveau_tunnel)

        return True

    def dijkstra(self, depart, arrivee) -> list[NoeudPondere]:
        """
        Implémente l'algorithme de Dijkstra pour trouver le chemin le plus court entre deux noeuds dans un graphe pondéré.
        Args:
            depart (NoeudPondere): Noeud de départ.
            arrivee (NoeudPondere): Noeud d'arrivée.
        Returns:
            list[NoeudPondere]: Liste des noeuds représentant le chemin le plus court.
        """
        def sort_queue(arr) -> list[NoeudPondere]:
            """
            Trie la liste de noeuds en fonction de leur distance avec un algorithme de merge sort.
            Args:
                arr (list[NoeudPondere]): Liste de noeuds à trier.
                distance (dict[NoeudPondere, int]): Dictionnaire des distances.
            Returns:
                list[NoeudPondere]: Liste triée de noeuds.
            """
            if len(arr) <= 1:
                return arr

            mid = len(arr) // 2
            left_half = sort_queue(arr[:mid])
            right_half = sort_queue(arr[mid:])

            return merge(left_half, right_half)

        def merge(left, right) -> list[NoeudPondere]:
            """
            Fusionne deux listes triées en une seule liste triée.
            Args:
                left (list[NoeudPondere]): Première liste triée.
                right (list[NoeudPondere]): Deuxième liste triée.
                distance (dict[NoeudPondere, int]): Dictionnaire des distances.
            Returns:
                list[NoeudPondere]: Liste fusionnée et triée.
            """
            sorted_arr = []
            i, j = 0, 0

            while i < len(left) and j < len(right):
                if distance[left[i]] < distance[right[j]]:
                    sorted_arr.append(left[i])
                    i += 1
                else:
                    sorted_arr.append(right[j])
                    j += 1

            sorted_arr.extend(left[i:])
            sorted_arr.extend(right[j:])
            
            return sorted_arr
        
        #Initialisation
        queue: list[NoeudPondere] = [] #queue qui permet de savoir quel noeud visiter
        distance: dict[NoeudPondere, int] = dict() #distance du départ à une node
        previous: dict[NoeudPondere, NoeudPondere] = dict() #noeud par lequel on est arrivé à ce noeud
        visited: set[NoeudPondere] = set() #noeuds dont tous les voisins ont été visités

        queue.append(depart)
        distance[depart] = 0
        previous[depart] = None
        
        #Naviguation
        while queue[0] != arrivee:
            sort_queue(queue)
            current: NoeudPondere = queue[0]

            for v, p in current.voisins.items():
                if v in visited:
                    continue

                if v not in queue:
                    queue.append(v)
                    distance[v] = distance[current] + p
                    previous[v] = current
                    continue

                if distance[current] + p < distance[v]:
                    distance[v] = distance[current] + p
                    previous[v] = current
            
            visited.add(current)
            queue.pop(0)

        #Reconstruction du chemin
        chemin: list[NoeudPondere] = [] #le chemin pris pour arriver à la fin
        current: NoeudPondere = arrivee

        while current != None:
            chemin.append(current)
            current = previous[current]

        chemin.reverse()
        return chemin