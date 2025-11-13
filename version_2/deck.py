# deck.py
import random
from card import Card

class Deck:
    def __init__(self):
        # Initialize deck and discard pile
        self.cards = []
        self.discard_pile = []
        self._generate_deck()
        self.shuffle()

    def _generate_deck(self):
        # Skyjo card distribution
        distribution = {
            -2: 5, -1: 10, 0: 15, 1: 10, 2: 10, 3: 10,
            4: 10, 5: 10, 6: 10, 7: 10, 8: 10, 9: 10,
            10: 10, 11: 10, 12: 10
        }
        for value, count in distribution.items():
            self.cards.extend([Card(value) for _ in range(count)])

    def shuffle(self):
        random.shuffle(self.cards)

    def draw_card(self):
        # Draw card from deck; reshuffle discard if empty
        if not self.cards:
            self.reshuffle_discard()
        if self.cards:
            return self.cards.pop()
        return None

    def top_discard(self):
        return self.discard_pile[-1] if self.discard_pile else None

    def discard_card(self, card: Card):
        self.discard_pile.append(card)

    def reshuffle_discard(self):
        # Reshuffle discard pile if deck empty, keeping top card
        if len(self.discard_pile) > 1:
            top_card = self.discard_pile.pop()
            self.cards = self.discard_pile
            self.discard_pile = [top_card]
            self.shuffle()
