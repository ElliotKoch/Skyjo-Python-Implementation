# player.py
from __future__ import annotations
from typing import Optional
from card import Card

class Player:
    def __init__(self, name: str):
        self.name = name
        self.grid: list[list[Optional[Card]]] = []  # 3x4 grid of cards
        self.score: int = 0
        self.held_card: Optional[Card] = None  # card drawn from deck/discard

    def setup_grid(self, deck: "Deck"):
        """Deal 12 face-down cards (3 rows x 4 columns)."""
        self.grid = [[deck.draw_card() for _ in range(4)] for _ in range(3)]

    def reveal_card(self, row: int, col: int) -> bool:
        """Reveal a card in the grid."""
        card = self.grid[row][col]
        if card and not card.revealed:
            card.reveal()
            return True
        return False

    def draw_from_deck(self, deck: "Deck") -> Optional[Card]:
        """Draw a card from the draw pile and hold it."""
        if self.held_card:
            return None
        self.held_card = deck.draw_card()
        return self.held_card

    def draw_from_discard(self, deck: "Deck") -> Optional[Card]:
        """Draw the top card from the discard pile."""
        if self.held_card:
            return None
        top_card = deck.top_discard()
        if top_card:
            self.held_card = deck.discard_pile.pop()
        return self.held_card

    def replace_card(self, row: int, col: int, deck: "Deck") -> bool:
        """Replace a grid card with held card and discard the replaced one."""
        if not self.held_card:
            return False
        target_card = self.grid[row][col]
        if target_card:
            target_card.reveal()
            deck.discard(target_card)
        self.grid[row][col] = self.held_card
        self.grid[row][col].reveal()
        self.held_card = None
        return True

    def discard_held_card(self, deck: "Deck") -> bool:
        """Discard the held card without replacing."""
        if not self.held_card:
            return False
        deck.discard(self.held_card)
        self.held_card = None
        return True

    def reveal_instead_of_replace(self, row: int, col: int) -> bool:
        """Reveal a hidden card when player discards drawn card."""
        if self.held_card:
            return False
        return self.reveal_card(row, col)

    def all_cards_revealed(self) -> bool:
        """Check if all cards in the grid are revealed."""
        return all(card.revealed for row in self.grid for card in row if card)

    def calculate_score(self) -> int:
        """Compute current score from revealed cards only."""
        total = sum(card.value for row in self.grid for card in row if card and card.revealed)
        self.score = total
        return total

    def check_triple_columns(self, discard_pile):
        """Check columns with 3 identical revealed cards and remove them."""
        messages = []
        for col in range(4):
            column_cards = [self.grid[row][col] for row in range(3)]
            if all(card and card.revealed for card in column_cards):
                values = [card.value for card in column_cards]
                if len(set(values)) == 1:
                    same_value = values[0]
                    for card in column_cards:
                        discard_pile.insert(0, card)
                    for row in range(3):
                        self.grid[row][col] = None
                    messages.append(f"{self.name} eliminated a column of 3 cards {same_value}!")
        return messages

    # --- Serialization for LAN ---
    def serialize_grid(self):
        """Return a JSON-serializable grid."""
        return [
            [
                {"value": card.value, "revealed": card.revealed} if card else None
                for card in row
            ]
            for row in self.grid
        ]

    def serialize(self):
        """Return full player state including held card."""
        return {
            "name": self.name,
            "grid": self.serialize_grid(),
            "score": self.score,
            "held_card": {"value": self.held_card.value, "revealed": self.held_card.revealed} if self.held_card else None
        }
