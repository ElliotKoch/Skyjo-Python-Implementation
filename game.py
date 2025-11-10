# game.py

from deck import Deck
from player import Player

class Game:
    def __init__(self, player_names):
        # Initialize deck and discard pile
        self.deck = Deck()
        self.discard_pile = self.deck.discard_pile

        # Create players
        self.players = [Player(name) for name in player_names]
        self.current_player_index = 0

        # Game phase: 'setup' (initial reveal) or 'play'
        self.phase = "setup"

    def start_game(self):
        # Deal cards to each player
        for player in self.players:
            player.setup_grid(self.deck)

        # Draw first card for discard pile
        first_card = self.deck.draw_card()
        first_card.reveal()
        if first_card:
            self.discard_pile.append(first_card)

    def get_current_player(self):
        return self.players[self.current_player_index]

    def next_turn(self):
        # Switch to next player
        self.current_player_index = (self.current_player_index + 1) % len(self.players)

    def draw_from_deck(self):
        # Draw top card from deck
        card = self.deck.draw_card()
        return card

    def draw_from_discard(self):
        # Draw top card from discard pile if not empty
        if self.discard_pile:
            return self.discard_pile.pop()
        return None

    def discard_card(self, card):
        # Add card to discard pile
        self.discard_pile.append(card)

    def reveal_card(self, player, row, col):
        # Reveal a hidden card in the player's grid
        player.reveal_card(row, col)

    def replace_card(self, player, row, col, new_card):
        # Replace a card in player's grid with new one, discarding the old one
        old_card = player.replace_card(row, col, new_card)
        self.discard_card(old_card)

    def check_end_round(self):
        # Check if any player has all cards revealed
        for player in self.players:
            if player.all_cards_revealed():
                return True
        return False
