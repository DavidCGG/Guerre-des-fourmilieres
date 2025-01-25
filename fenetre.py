import arcade

fenetre_largeur=1000
fenetre_hauteur=500
fenetre_titre="Titre"

class VueJeu(arcade.Window):
    def __init__(self):
        super().__init__(fenetre_largeur,fenetre_hauteur,fenetre_titre)
        self.background_color=arcade.csscolor.CORNFLOWER_BLUE
        self.player_texture=arcade.load_texture("assets/Fourmi.png")
        self.player_sprite=arcade.Sprite(self.player_texture)
        self.player_sprite.center_x=16
        self.player_sprite.center_y=14

    def setup(selfself):
        #Set up le jeu ici. Call pour redemarrer le jeu.
        pass

    def on_draw(self):
        self.clear()
        #code pour draw ici
        arcade.draw_sprite(self.player_sprite)

def main():
    fenetre=VueJeu()
    fenetre.setup()
    arcade.run()

if __name__ == "__main__":
    main()