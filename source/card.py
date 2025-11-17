# card.py

class Card:
    def __init__(self, value: int):
        # Store the card's numeric value and whether it is currently revealed
        self.value = value
        self.revealed = False

    def reveal(self):
        # Set the card to face-up (visible)
        self.revealed = True

    def hide(self):
        # Set the card to face-down (hidden)
        self.revealed = False

    def __repr__(self):
        # String representation: show the value if revealed, otherwise "?"
        return f"[{self.value if self.revealed else '?'}]"
