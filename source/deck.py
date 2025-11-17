# deck.py
import random
from card import Card

class Deck:
    def __init__(self):
        # Create the full deck and the discard pile
        self.cards = []
        self.discard_pile = []
        self._generate_deck()
        self.shuffle()

    def _generate_deck(self):
        # Generate the official Skyjo deck based on card distribution
        distribution = {
            -2: 5, -1: 10, 0: 15, 1: 10, 2: 10, 3: 10,
            4: 10, 5: 10, 6: 10, 7: 10, 8: 10, 9: 10,
            10: 10, 11: 10, 12: 10
        }
        # Create card instances according to distribution
        for value, count in distribution.items():
            self.cards.extend([Card(value) for _ in range(count)])

    def shuffle(self):
        # Shuffle the main deck
        random.shuffle(self.cards)

    def draw_card(self):
        # Draw the top card of the deck
        # If the deck is empty, the discard pile is reshuffled back into the deck
        if not self.cards:
            self.reshuffle_discard()
        # Return a card only if deck has cards after reshuffling
        if self.cards:
            return self.cards.pop()
        return None

    def top_discard(self):
        # Get the top card of the discard pile without removing it
        return self.discard_pile[-1] if self.discard_pile else None

    def discard_card(self, card: Card):
        # Place a card onto the top of the discard pile
        self.discard_pile.append(card)

    def reshuffle_discard(self):
        # If the deck is empty, reshuffle the discard pile back into the deck
        # The top card of the discard pile must stay as the visible discard
        if len(self.discard_pile) > 1:
            top_card = self.discard_pile.pop()   # Keep the visible discard
            self.cards = self.discard_pile       # Move remaining cards back into the deck
            self.discard_pile = [top_card]       # Reset discard pile with only the top card
            self.shuffle()                        # Shuffle the new deck
