# main.py
from game import Game
from gui import GameWindow

def main():
    # Define the list of players taking part in the game
    player_names = ["Alice", "Bob"]

    # Create the Game instance with all players
    game = Game(player_names)

    # Initialize the first round (deal cards, set up discard pile)
    game.start_game()

    # Create and display the GUI window bound to the game
    window = GameWindow(game)
    window.mainloop()  # Start GUI event loop

if __name__ == "__main__":
    # Entry point of the app
    main()
