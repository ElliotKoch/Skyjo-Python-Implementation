# game.py
from deck import Deck
from player import Player
from typing import List, Optional
from card import Card

class Game:
    def __init__(self, player_names: List[str]):
        self.deck = Deck()
        self.discard_pile = self.deck.discard_pile
        self.players = [Player(name) for name in player_names]
        self.current_player_index = 0

        self.final_round_triggered_by: Optional[Player] = None
        self.final_round_triggered = False
        self.final_turns_remaining = 0

        self.phase = "setup"  # "setup" or "play"

    def start_game(self):
        # Setup player grids
        for player in self.players:
            player.setup_grid(self.deck)
            player.held_card = None

        # First discard card
        first_card = self.deck.draw_card()
        if first_card:
            first_card.reveal()
            self.discard_pile.append(first_card)

    def get_current_player(self) -> Player:
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

    def apply_move_draw_deck(self, player_index: int) -> Optional[dict]:
        player = self.players[player_index]
        card = player.draw_from_deck(self.deck)
        if card:
            return {"value": card.value}
        return None

    def apply_move_draw_discard(self, player_index: int) -> Optional[dict]:
        player = self.players[player_index]
        card = player.draw_from_discard(self.deck)
        if card:
            return {"value": card.value}
        return None

    def apply_move_replace(self, player_index: int, row: int, col: int) -> Optional[dict]:
        player = self.players[player_index]
        old_card = player.replace_card(row, col)
        if old_card:
            self.discard_pile.append(old_card)
            return {"discarded_value": old_card.value}
        return None

    def apply_move_discard(self, player_index: int) -> bool:
        player = self.players[player_index]
        return player.discard_held_card(self.deck)

    def apply_move_reveal(self, player_index: int, row: int, col: int) -> bool:
        player = self.players[player_index]
        return player.reveal_instead_of_replace(row, col)

    def check_triples(self) -> List[str]:
        messages = []
        for player in self.players:
            messages.extend(player.check_triple_columns(self.discard_pile))
        return messages

    def serialize_state(self) -> dict:
        """
        Convert the full game state to JSON-friendly format for network transmission.
        """
        return {
            "deck_count": len(self.deck.cards),
            "discard_top": self.discard_pile[-1].value if self.discard_pile else None,
            "players": [
                {
                    "name": p.name,
                    "score": p.score,
                    "grid": p.serialize_grid(),
                    "held_card": {"value": p.held_card.value} if p.held_card else None
                } for p in self.players
            ],
            "current_player_index": self.current_player_index,
            "phase": self.phase,
            "final_round_triggered": self.final_round_triggered,
            "final_turns_remaining": self.final_turns_remaining
        }

    def deserialize_state(self, state: dict):
        """
        Load the full game state from network data.
        """
        self.current_player_index = state["current_player_index"]
        self.phase = state["phase"]
        self.final_round_triggered = state["final_round_triggered"]
        self.final_turns_remaining = state["final_turns_remaining"]

        # Deck count
        deck_count = state.get("deck_count", 0)
        if deck_count != len(self.deck.cards):
            # regenerate placeholder cards if needed
            self.deck.cards = [Card(0) for _ in range(deck_count)]

        # Discard pile top card
        if state.get("discard_top") is not None:
            self.discard_pile = [Card(state["discard_top"])]
        else:
            self.discard_pile = []

        for p_state, player in zip(state["players"], self.players):
            player.score = p_state["score"]
            player.deserialize_grid(p_state["grid"])
            if p_state.get("held_card"):
                player.held_card = Card(p_state["held_card"]["value"])
            else:
                player.held_card = None
