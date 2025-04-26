from tuile import Tuile

class GenerationMap:
    def __init__(self, width, height, tile_size):
        self.width = width # En nombre de tuiles
        self.height = height
        self.tile_size = tile_size


    def liste_tuiles(self) -> list:
        tuiles = [[Tuile(x, y, self.tile_size, self.tile_size) for x in range(self.width)] for y in range(self.height)]
        return tuiles
