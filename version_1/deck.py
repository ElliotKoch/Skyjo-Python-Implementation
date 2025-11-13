# deck.py
import random
from card import Card

class Deck:
    def __init__(self):
        # Create and shuffle the full Skyjo deck
        self.cards = []
        self.discard_pile = []
        self._generate_deck()
        self.shuffle()

    def _generate_deck(self):
        # Define the card distribution according to Skyjo rules
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

        # Create all cards based on distribution
        for value, count in distribution.items():
            self.cards.extend([Card(value) for _ in range(count)])

    def shuffle(self):
        # Randomly shuffle the deck
        random.shuffle(self.cards)

    def draw_card(self):
        # Draw one card from the deck
        if not self.cards:
            self.reshuffle_discard()
        return self.cards.pop() if self.cards else None

    def top_discard(self):
        # Return the top visible card from the discard pile
        return self.discard_pile[-1] if self.discard_pile else None

    def discard(self, card: Card):
        # Place a card on top of the discard pile
        self.discard_pile.append(card)

    def reshuffle_discard(self):
        # When the draw pile is empty, reshuffle the discard pile
        if len(self.discard_pile) > 1:
            top_card = self.discard_pile.pop()
            self.cards = self.discard_pile
            self.discard_pile = [top_card]
            self.shuffle()
