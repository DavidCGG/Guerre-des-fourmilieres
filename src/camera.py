import pygame

class Camera:
    """
    Permet de déplacer et zoomer la caméra sur la carte du monde et sur un nid
    Attributs :
        width (int): Largeur de la fenêtre en pixels
        height (int): Hauteur de la fenêtre en pixels
        map_limit_x (int): Limite de la carte en pixels sur l'axe x
        map_limit_y (int): Limite de la carte en pixels sur l'axe y
        x (float): Position actuelle de la caméra sur l'axe x
        y (float): Position actuelle de la caméra sur l'axe y
        offset_x (float): Décalage de la souris sur l'axe x
        offset_y (float): Décalage de la souris sur l'axe y
        old_x (float): Ancienne position de la caméra sur l'axe x
        old_y (float): Ancienne position de la caméra sur l'axe y
        dragging (bool): Indique si la caméra est en cours de déplacement
        zoom (float): Niveau de zoom actuel
        zoom_levels (list): Liste des niveaux de zoom disponibles
    """
    def __init__(self, width, height, map_limit_x, map_limit_y):
        self.width = width
        self.height = height
        self.map_limit_x = map_limit_x
        self.map_limit_y = map_limit_y

        self.x = map_limit_x // 2 - width // 2
        self.y = 0
        self.offset_x = 0
        self.offset_y = 0
        self.old_x = self.x
        self.old_y = self.y

        self.dragging = False

        self.zoom = 1.0 * height / 720
        self.zoom_levels = [0.5, 0.75, 1.0, 1.25, 1.5, 1.75, 2.0, 2.25, 2.5]
        for l in range(len(self.zoom_levels)):
            self.zoom_levels[l]*=height / 720

    def apply(self, point):
        """
        Applique la transformation de la caméra à un point donné
        Args:
            point (tuple): Coordonnées du point à transformer
        Returns:
            tuple: Coordonnées transformées du point
        """
        new_x = point[0] * self.zoom - self.x
        new_y = point[1] * self.zoom - self.y + 50  # + 50 pour la barre du haut
        return (new_x, new_y)
    
    def apply_rect(self, rect):
        """
        Applique la transformation de la caméra à un rectangle donné
        Args:
            rect (pygame.Rect): Rectangle à transformer
        Returns:
            pygame.Rect: Rectangle transformé
        """
        return pygame.Rect(
            rect.x - self.x,
            rect.y - self.y + 50,  # + 50 pour la barre du haut
            rect.width,
            rect.height,
        )

    def move(self, dx, dy):
        """
        Déplace la caméra en fonction des déplacements dx et dy
        Args:
            dx (float): Déplacement sur l'axe x
            dy (float): Déplacement sur l'axe y
        Returns:
            None
        """
        dx = dx * self.zoom
        dy = dy * self.zoom

        #On s'assure que la caméra reste dans les limites de la carte
        self.x = max(0, min(self.x - dx, self.map_limit_x * self.zoom - self.width))
        self.y = max(0, min(self.y - dy, self.map_limit_y * self.zoom - self.height + 50))

    def start_drag(self, mouse_x, mouse_y):
        """
        Démarre le drag de la caméra
        Args:
            mouse_x (int): Position x de la souris
            mouse_y (int): Position y de la souris
        Returns:
            None
        """
        self.dragging = True
        self.offset_x = mouse_x
        self.offset_y = mouse_y
        self.old_x = self.x
        self.old_y = self.y

    def drag(self, mouse_x, mouse_y):
        """
        Déplace la caméra en fonction du mouvement de la souris
        Args:
            mouse_x (int): Position x de la souris
            mouse_y (int): Position y de la souris
        Returns:
            None
        """
        if self.dragging:
            ### dx et dy sont les deplacements de la souris
            ### entre le premier clic et la position actuelle de drag
            ### On divise par le zoom pour que le deplacement soit plus lent
            dx = (mouse_x - self.offset_x) / self.zoom
            dy = (mouse_y - self.offset_y) / self.zoom
            ### On met a jour la position de la camera
            self.x = self.old_x - dx
            self.y = self.old_y - dy
            ### On deplace la camera
            self.move(dx, dy)

    def stop_drag(self):
        """
        Arrête le drag de la caméra
        Args:
            None
        Returns:
            None
        """
        self.dragging = False

    def zoom_camera(self, mouse_x, mouse_y, direction):
        """
        Zoom la caméra en fonction de la molette de la souris
        Args:
            mouse_x (int): Position x de la souris
            mouse_y (int): Position y de la souris
            direction (str): "in" pour zoomer, "out" pour dézoomer
        Returns:
            None
        """
        current_zoom_index = self.zoom_levels.index(self.zoom)
        if direction == "in" and current_zoom_index < len(self.zoom_levels) - 1:
            new_zoom = self.zoom_levels[current_zoom_index + 1]
        elif direction == "out" and current_zoom_index > 0:
            new_zoom = self.zoom_levels[current_zoom_index - 1]
        else:
            return

        # On garde la position de la souris dans le jeu en prenant en compte le zoom et la position de la camera
        world_x = (mouse_x + self.x) / self.zoom
        world_y = (mouse_y + self.y - 50) / self.zoom

        self.zoom = new_zoom

        # On garde la position de la souris fixe
        self.x = world_x * self.zoom - mouse_x
        self.y = world_y * self.zoom - mouse_y + 50

        # On s'assure que la camera reste dans les limites de la map
        self.x = max(0, min(self.x, self.map_limit_x * self.zoom - self.width))
        self.y = max(0, min(self.y , self.map_limit_y * self.zoom - self.height))