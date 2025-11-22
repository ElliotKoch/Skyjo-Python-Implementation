# game.py
from deck import Deck
from player import Player

class Game:
    def __init__(self, player_names: list[str]):
        # Create the deck, discard pile, and all players
        self.deck = Deck()
        self.discard_pile = self.deck.discard_pile
        self.players = [Player(name) for name in player_names]

        # Track turn order and round progression
        self.current_player_index = 0
        self.final_round_triggered_by = None
        self.final_round_triggered = False
        self.final_turns_remaining = 0
        self.phase = "setup"

    def start_game(self):
        # Deal grids and clear held cards for all players
        for player in self.players:
            player.setup_grid(self.deck)
            player.held_card = None

        # Draw the first revealed card for the discard pile
        first_card = self.deck.draw_card()
        if first_card:
            first_card.reveal()
            self.discard_pile.append(first_card)

    def get_current_player(self):
        # Return the player whose turn is active
        return self.players[self.current_player_index]

    def next_turn(self):
        # Advance to the next player's turn, handling final round logic
        if self.final_round_triggered:
            if self.current_player_index == self.final_round_triggered_by:
                # Skip the player who triggered the final round
                self.current_player_index = (self.current_player_index + 1) % len(self.players)
            self.final_turns_remaining -= 1

        # Move to the next player
        self.current_player_index = (self.current_player_index + 1) % len(self.players)

    def check_end_round(self) -> bool:
        # Detect when the final round should start or finish
        if not self.final_round_triggered:
            # First detection: a player has revealed all cards
            for player in self.players:
                if player.all_cards_revealed():
                    self.final_round_triggered = True
                    self.final_round_triggered_by = player
                    # Other players each get one more turn
                    self.final_turns_remaining = len(self.players) - 1
                    return False
            return False
        else:
            # Final round already active: check if all remaining turns are done
            return self.final_turns_remaining <= 0

    def reset_round(self):
        # Prepare the next round: new deck, reset flags and grids
        self.deck = Deck()
        self.discard_pile = self.deck.discard_pile

        # Next round starts with the player after the one who triggered final round
        self.next_turn()

        print(self.final_round_triggered_by,self.current_player_index)  # Debug info

        self.phase = "setup"
        self.final_round_triggered = False
        self.final_turns_remaining = 0

        # Rebuild grids and clear held cards
        for player in self.players:
            player.setup_grid(self.deck)
            player.held_card = None

        # Draw the first discard pile card again
        self.start_game()
