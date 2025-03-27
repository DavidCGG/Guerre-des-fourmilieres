import arcade


def spritesheet_to_texture_list(spritesheet: arcade.SpriteSheet,
                                size: tuple[int, int], columns: int, count: int,
                                margin: tuple[int, int, int, int] | None) -> list:
    """
    Convertit une spritesheet en liste de textures
    :param spritesheet: La spritesheet à convertir
    :param size: La taille de chaque texture
    :param columns: Le nombre de colonnes dans la spritesheet
    :param count: Le nombre de textures à extraire
    :param margin: La marge entre chaque texture
    :return: La liste de textures

    """
    if margin is None:
        margin = (0, 0, 0, 0)

    return spritesheet.get_texture_grid(size, columns, count, margin)

def spritesheet_flip(spritesheet: arcade.SpriteSheet):
    return spritesheet.flip_left_right()

