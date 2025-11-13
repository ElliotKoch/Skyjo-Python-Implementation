# main.py
from game import Game
from gui import GameWindow

def main():
    player_names = ["Alice", "Bob"]
    game = Game(player_names)
    game.start_game()
    window = GameWindow(game)
    window.mainloop()

if __name__ == "__main__":
    main()
