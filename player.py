# player.py
from __future__ import annotations
from typing import Optional

class Player:
    def __init__(self, name: str):
        # Initialize player name, grid (4x3), score, and current hand
        self.name = name
        self.grid: list[list["Card"]] = []
        self.score: int = 0
        self.held_card: Optional["Card"] = None  # Temporary card drawn during the turn

    def setup_grid(self, deck: "Deck"):
        # Deal 12 face-down cards (4 columns x 3 rows)
        self.grid = [[deck.draw_card() for _ in range(4)] for _ in range(3)]

    def reveal_card(self, row: int, col: int) -> bool:
        # Reveal a specific card chosen by the player
        card = self.grid[row][col]
        if not card.revealed:
            card.reveal()
            return True
        return False

    def draw_from_deck(self, deck: "Deck") -> Optional["Card"]:
        # Draw a card from the draw pile and hold it temporarily
        if self.held_card is not None:
            return None  # Cannot draw twice in the same turn
        self.held_card = deck.draw_card()
        return self.held_card

    def draw_from_discard(self, deck: "Deck") -> Optional["Card"]:
        # Draw the top card from the discard pile
        # Must be replaced with one from the player's grid
        if self.held_card is not None:
            print("top card is held")
            return None
        top_card = deck.top_discard()
        print("top card", top_card)
        if top_card is None:
            return None
        self.held_card = deck.discard_pile.pop()
        return self.held_card

    def replace_card(self, row: int, col: int, deck: "Deck") -> bool:
        # Replace one of the player's cards with the held card
        if self.held_card is None:
            return False

        target_card = self.grid[row][col]
        self.reveal_card(row,col)
        deck.discard_card(target_card)

        self.grid[row][col] = self.held_card
        self.grid[row][col].reveal()
        self.held_card = None
        return True

    def discard_drawn_card(self, deck: "Deck") -> bool:
        # Discard the held card without replacing
        if self.held_card is None:
            return False
        deck.discard_card(self.held_card)
        self.held_card = None
        return True

    def reveal_instead_of_replace(self, row: int, col: int) -> bool:
        # Reveal one hidden card if player discards the drawn card
        if self.held_card is not None:
            return False
        return self.reveal_card(row, col)

    def calculate_score(self) -> int:
        # Calculate total score of revealed cards
        total = 0
        for row in self.grid:
            for card in row:
                if card.revealed:
                    total += card.value
        self.score += total
        return total

    def all_cards_revealed(self) -> bool:
        # Check if all cards are face up
        return all(card.revealed for row in self.grid for card in row)

    def __repr__(self) -> str:
        # Print grid representation for debugging
        display = "\n".join(" ".join(str(card) for card in row) for row in self.grid)
        held = f"Held: {self.held_card}" if self.held_card else "Held: None"
        return f"{self.name}:\n{display}\n{held}\nScore: {self.score}"
