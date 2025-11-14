# deck.py
import random
from card import Card
from typing import Optional

class Deck:
    def __init__(self):
        self.cards: list[Card] = []  # draw pile
        self.discard_pile: list[Card] = []
        self._generate_deck()
        self.shuffle()

    def _generate_deck(self):
        """Generate Skyjo deck according to official distribution."""
        distribution = {
            -2: 5,
            -1: 10,
            0: 15,
            1: 10,
            2: 10,
            3: 10,
            4: 10,
            5: 10,
            6: 10,
            7: 10,
            8: 10,
            9: 10,
            10: 10,
            11: 10,
            12: 10
        }
        for value, count in distribution.items():
            self.cards.extend([Card(value) for _ in range(count)])

    def shuffle(self):
        random.shuffle(self.cards)

    def draw_card(self) -> Optional[Card]:
        """Draw a card from draw pile; reshuffle discard if empty."""
        if not self.cards:
            self.reshuffle_discard()
        return self.cards.pop() if self.cards else None

    def top_discard(self) -> Optional[Card]:
        """Get top card of discard pile."""
        return self.discard_pile[-1] if self.discard_pile else None

    def discard(self, card: Card):
        """Place a card on the discard pile."""
        self.discard_pile.append(card)

    def reshuffle_discard(self):
        """Reshuffle discard pile into draw pile if draw pile empty (except top card)."""
        if len(self.discard_pile) > 1:
            top_card = self.discard_pile.pop()
            self.cards = self.discard_pile
            self.discard_pile = [top_card]
            self.shuffle()

    # --- Serialization for LAN ---
    def serialize(self):
        """Return JSON-serializable deck state."""
        return {
            "draw_pile": [{"value": c.value, "revealed": c.revealed} for c in self.cards],
            "discard_pile": [{"value": c.value, "revealed": c.revealed} for c in self.discard_pile]
        }
