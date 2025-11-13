# card.py
class Card: 
    def __init__(self, value: int):
        # Each card has a numeric value and a visibility state
        self.value = value
        self.revealed = False

    def reveal(self):
        # Turn the card face up
        self.revealed = True

    def hide(self):
        # Turn the card face down
        self.revealed = False

    def __repr__(self):
        # Display value if revealed, otherwise "?"
        return f"[{self.value if self.revealed else '?'}]"
