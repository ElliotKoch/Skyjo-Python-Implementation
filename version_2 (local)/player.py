# player.py
from __future__ import annotations
from typing import Optional
from card import Card
from deck import Deck

class Player:
    def __init__(self, name: str):
        self.name = name
        self.grid: list[list[Optional[Card]]] = []
        self.score: int = 0
        self.held_card: Optional[Card] = None  # Temporary card drawn during the turn

    def setup_grid(self, deck: Deck):
        # Deal 12 face-down cards (3 rows x 4 cols)
        self.grid = [[deck.draw_card() for _ in range(4)] for _ in range(3)]

    def reveal_card(self, row: int, col: int) -> bool:
        card = self.grid[row][col]
        if card and not card.revealed:
            card.reveal()
            return True
        return False

    def draw_from_deck(self, deck: Deck) -> Optional[Card]:
        if self.held_card is None:
            self.held_card = deck.draw_card()
        return self.held_card

    def draw_from_discard(self, deck: Deck) -> Optional[Card]:
        if self.held_card is None and deck.discard_pile:
            self.held_card = deck.discard_pile.pop()
        return self.held_card

    def replace_card(self, row: int, col: int, deck: Deck) -> bool:
        # Replace card in grid with held_card
        if self.held_card is None:
            return False
        target_card = self.grid[row][col]
        if target_card is not None:
            target_card.reveal()
            deck.discard_card(target_card)
        self.grid[row][col] = self.held_card
        self.grid[row][col].reveal()
        self.held_card = None
        return True

    def discard_drawn_card(self, deck: Deck) -> bool:
        if self.held_card is None:
            return False
        deck.discard_card(self.held_card)
        self.held_card = None
        return True

    def reveal_instead_of_replace(self, row: int, col: int) -> bool:
        if self.held_card is not None:
            return False
        return self.reveal_card(row, col)

    def calculate_score(self) -> int:
        # Calculate current score (not cumulative)
        total = 0
        for row in self.grid:
            for card in row:
                if card and card.revealed:
                    total += card.value
        self.score = total
        return total

    def all_cards_revealed(self) -> bool:
        return all(card.revealed for row in self.grid for card in row if card is not None)

    def check_triple_columns(self, discard_pile) -> list[str]:
        # Check for columns with 3 identical revealed cards
        messages = []
        for col in range(4):
            column_cards = [self.grid[row][col] for row in range(3)]
            if all(card and card.revealed for card in column_cards):
                values = [card.value for card in column_cards]
                if len(set(values)) == 1:
                    value = values[0]
                    for card in column_cards:
                        discard_pile.insert(0, card)
                    for row in range(3):
                        self.grid[row][col] = None
                    messages.append(f"{self.name} eliminated a column of 3 cards {value}!")
        return messages

    def __repr__(self) -> str:
        display = "\n".join(" ".join(str(card) if card else "[ ]" for card in row) for row in self.grid)
        held = f"Held: {self.held_card}" if self.held_card else "Held: None"
        return f"{self.name}:\n{display}\n{held}\nScore: {self.score}"
