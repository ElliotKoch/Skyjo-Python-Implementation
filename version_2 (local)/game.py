# game.py
from deck import Deck
from player import Player

class Game:
    def __init__(self, player_names: list[str]):
        self.deck = Deck()
        self.discard_pile = self.deck.discard_pile
        self.players = [Player(name) for name in player_names]
        self.current_player_index = 0
        self.final_round_triggered_by = None
        self.final_round_triggered = False
        self.final_turns_remaining = 0
        self.phase = "setup"

    def start_game(self):
        for player in self.players:
            player.setup_grid(self.deck)
            player.held_card = None
        # Draw first card for discard pile
        first_card = self.deck.draw_card()
        if first_card:
            first_card.reveal()
            self.discard_pile.append(first_card)

    def get_current_player(self):
        return self.players[self.current_player_index]

    def next_turn(self):
        self.current_player_index = (self.current_player_index + 1) % len(self.players)

    def check_end_round(self) -> bool:
        if not self.final_round_triggered:
            for player in self.players:
                if player.all_cards_revealed():
                    self.final_round_triggered = True
                    self.final_round_triggered_by = player
                    self.final_turns_remaining = len(self.players) - 1
                    return False
            return False
        else:
            return self.final_turns_remaining <= 0

    def reset_round(self):
        self.deck = Deck()
        self.discard_pile = self.deck.discard_pile
        self.current_player_index = self.players.index(self.final_round_triggered_by)
        self.next_turn()
        print(self.current_player_index)
        self.phase = "setup"
        self.final_round_triggered = False
        self.final_turns_remaining = 0
        for player in self.players:
            player.setup_grid(self.deck)
            player.held_card = None
        self.start_game()
