# main.py
from game import Game
from gui import GameWindow

def main():
    # Player names
    player_names = ["Alice", "Bob"]

    # Create the game
    game = Game(player_names)

    # Start the game (deal cards, first discard)
    game.start_game()

    # Create the GUI window and link it to the game
    window = GameWindow(game)

    # Start Tkinter event loop
    window.mainloop()

if __name__ == "__main__":
    main()
