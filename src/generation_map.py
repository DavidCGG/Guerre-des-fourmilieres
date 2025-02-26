from tuile import Tuile
from config import RED

class GenerationMap:
    def __init__(self, width, height, tile_size):
        self.width = width # En nombre de tuiles
        self.height = height
        self.tile_size = tile_size


    def liste_tuiles(self) -> list:
        tuiles = [[Tuile(x, y, self.tile_size, self.tile_size) for x in range(self.width)] for y in range(self.height)]
        for y in range(self.height):
            for x in range(self.width):
                if x == 0 or y == 0 or x == self.width - 1 or y == self.height - 1:
                    tuiles[y][x].is_border = True
                    tuiles[y][x].color = RED

        return tuiles



if __name__ == "__main__":
    gen_map = GenerationMap(10, 10, 32)
    map_data = gen_map.liste_tuiles()
    for y in range(10):
        for x in range(10):
            print(map_data[y][x].color, end=" ")
        print()