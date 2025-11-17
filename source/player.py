# player.py
from __future__ import annotations
from typing import Optional
from card import Card
from deck import Deck

class Player:
    def __init__(self, name: str):
        self.name = name
        self.grid: list[list[Optional[Card]]] = []   # 3×4 grid holding the player's cards
        self.score: int = 0                          # Total score after each round
        self.held_card: Optional[Card] = None        # Card temporarily held during a turn

    def setup_grid(self, deck: Deck):
        # Deal 12 face-down cards into a 3×4 grid
        self.grid = [[deck.draw_card() for _ in range(4)] for _ in range(3)]

    def reveal_card(self, row: int, col: int) -> bool:
        # Reveal a specific card if it is still hidden
        card = self.grid[row][col]
        if card and not card.revealed:
            card.reveal()
            return True
        return False

    def draw_from_deck(self, deck: Deck) -> Optional[Card]:
        # Draw a card from the deck if the player is not already holding one
        if self.held_card is None:
            self.held_card = deck.draw_card()
        return self.held_card

    def draw_from_discard(self, deck: Deck) -> Optional[Card]:
        # Take the top card from the discard pile if available
        if self.held_card is None and deck.discard_pile:
            self.held_card = deck.discard_pile.pop()
        return self.held_card

    def replace_card(self, row: int, col: int, deck: Deck) -> bool:
        # Replace a grid card using the held card, sending the old one to the discard pile
        if self.held_card is None:
            return False
        target_card = self.grid[row][col]
        if target_card is not None:
            target_card.reveal()              # Reveal replaced card before discarding
            deck.discard_card(target_card)    # Old card goes to the discard pile
        self.grid[row][col] = self.held_card  # Insert the held card
        self.grid[row][col].reveal()          # New card becomes revealed
        self.held_card = None
        return True

    def discard_drawn_card(self, deck: Deck) -> bool:
        # Discard the currently held card without replacing any grid card
        if self.held_card is None:
            return False
        deck.discard_card(self.held_card)
        self.held_card = None
        return True

    def reveal_instead_of_replace(self, row: int, col: int) -> bool:
        # Reveal a card when the drawn card was discarded (special rule)
        if self.held_card is not None:
            return False
        return self.reveal_card(row, col)

    def calculate_score(self) -> int:
        # Compute the player's score by summing all revealed card values
        total = 0
        for row in self.grid:
            for card in row:
                if card and card.revealed:
                    total += card.value
        self.score = total
        return total

    def all_cards_revealed(self) -> bool:
        # Check whether the player has no hidden cards left
        return all(card.revealed for row in self.grid for card in row if card is not None)

    def check_triple_columns(self, discard_pile) -> list[str]:
        # Detect columns containing 3 identical revealed cards
        messages = []
        for col in range(4):
            column_cards = [self.grid[row][col] for row in range(3)]
            # Column must contain only revealed cards
            if all(card and card.revealed for card in column_cards):
                values = [card.value for card in column_cards]
                # All three cards must match
                if len(set(values)) == 1:
                    value = values[0]
                    # Send all three cards to the *bottom* of the discard pile
                    for card in column_cards:
                        discard_pile.insert(0, card)
                    # Remove the entire column from the grid
                    for row in range(3):
                        self.grid[row][col] = None
                    messages.append(f"{self.name} eliminated a column of 3 cards {value}!")
        return messages

    def __repr__(self) -> str:
        # Developer-friendly representation of the grid and player state
        display = "\n".join(
            " ".join(str(card) if card else "[ ]" for card in row)
            for row in self.grid
        )
        held = f"Held: {self.held_card}" if self.held_card else "Held: None"
        return f"{self.name}:\n{display}\n{held}\nScore: {self.score}"
