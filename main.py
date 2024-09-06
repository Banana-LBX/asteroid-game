import pyray as pr
from game import Game

screen_width = 1200
screen_height = 720

current_game = Game(screen_width, screen_height)

if __name__ == "__main__":
    pr.init_window(screen_width, screen_height, "Asteroids")
    pr.set_target_fps(60)

    current_game.startup()
    pr.set_window_icon(pr.load_image("assets/player.png"))

    while not pr.window_should_close():

        current_game.update()

        pr.begin_drawing()
        pr.clear_background(pr.BLACK)

        current_game.render()

        pr.end_drawing()

    pr.close_window()
    current_game.shutdown()
