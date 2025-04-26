import pygame

class Camera:
    def __init__(self, width, height, map_limit_x, map_limit_y):
        self.width = width   # Screen width
        self.height = height  # Screen height
        self.map_limit_x = map_limit_x
        self.map_limit_y = map_limit_y

        self.x = map_limit_x // 2 - width // 2
        self.y = 0
        self.zoom = 1.0
        self.dragging = False
        self.offset_x = 0
        self.offset_y = 0
        self.old_x = self.x
        self.old_y = self.y

        self.zoom_levels = [0.5, 0.75, 1.0, 1.25, 1.5, 1.75, 2.0, 2.25, 2.5]

    def apply(self, point):
        """Applique la camera a un rectangle, pour le 'deplacer'"""
        new_x = point[0] * self.zoom - self.x
        new_y = point[1] * self.zoom - self.y + 50  # + 50 pour la barre du haut
        return (new_x, new_y)
    
    def apply_rect(self, rect):
        return pygame.Rect(
            rect.x - self.x,
            rect.y - self.y + 50,  # + 50 pour la barre du haut
            rect.width,
            rect.height,
        )

    def move(self, dx, dy):
        """Deplace la camera tout en gardant la camera dans les limites de la map"""
        ### On prend le min entre le deplacement et le reste de la map pour ne pas sortir de la map du coté gauche
        ### On prend le max entre le deplacement et 0 pour ne pas sortir de la map du coté droit
        dx = dx * self.zoom
        dy = dy * self.zoom

        self.x = max(0, min(self.x - dx, self.map_limit_x * self.zoom - self.width))
        self.y = max(0, min(self.y - dy, self.map_limit_y * self.zoom - self.height + 50))

    def start_drag(self, mouse_x, mouse_y):
        """Debut du drag de la camera"""
        self.dragging = True
        self.offset_x = mouse_x
        self.offset_y = mouse_y
        self.old_x = self.x
        self.old_y = self.y

    def drag(self, mouse_x, mouse_y):
        """Mise a jour de la position de la camera pendant le drag"""
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
        """Arret du drag de la camera"""
        self.dragging = False

    def zoom_camera(self, mouse_x, mouse_y, direction):
        """Zoom in/out en gardant la position de la souris fixe"""
        current_zoom_index = self.zoom_levels.index(self.zoom)
        if direction == "in" and current_zoom_index < len(self.zoom_levels) - 1:
            new_zoom = self.zoom_levels[current_zoom_index + 1]
        elif direction == "out" and current_zoom_index > 0:
            new_zoom = self.zoom_levels[current_zoom_index - 1]
        else:
            return

        ## On garde la position de la souris dans le jeu en prenant en compte le zoom et la position de la camera
        world_x = (mouse_x + self.x) / self.zoom
        world_y = (mouse_y + self.y - 50) / self.zoom

        # On met a jour le zoom
        self.zoom = new_zoom

        # On garde la position de la souris fixe
        self.x = world_x * self.zoom - mouse_x
        self.y = world_y * self.zoom - mouse_y + 50

        # On s'assure que la camera reste dans les limites de la map
        self.x = max(0, min(self.x, self.map_limit_x * self.zoom - self.width))
        self.y = max(0, min(self.y , self.map_limit_y * self.zoom - self.height))