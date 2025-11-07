# gui.py
import tkinter as tk
from game import Game

CARD_WIDTH = 60
CARD_HEIGHT = 90
MARGIN = 10
GRID_Y_OFFSET = 350  

class GameWindow(tk.Tk):
    def __init__(self, game: Game):
        super().__init__()
        self.title("Skyjo - 2 Players")
        self.game = game
        self.game.set_gui = self

        self.canvas = tk.Canvas(self, width=700, height=500)
        self.canvas.pack()

        self.info_label = tk.Label(self, text="")
        self.info_label.pack()

        self.action_phase = "initial_reveal"  # Initial reveal
        self.initial_reveals_done = {player.name: 0 for player in self.game.players}
        self.held_card_rect = None
        self.held_card_text = None

        self.draw_board()
        self.update_info()

    def draw_board(self):
        self.canvas.delete("all")
        current = self.game.get_current_player()

        # Draw deck and discard for current player
        deck_color = "red" if self.action_phase in ["choose_pile", "choose_replace_or_discard"] else "black"
        discard_color = "red" if self.action_phase in ["choose_pile", "choose_replace_or_discard"] and self.game.discard_pile else "black"

        self.deck_rect = self.canvas.create_rectangle(550, 50, 610, 110, fill="white", outline=deck_color, width=3 if deck_color=="red" else 1)
        self.discard_rect = self.canvas.create_rectangle(650, 50, 710, 110, fill="white", outline=discard_color, width=3 if discard_color=="red" else 1)
        if self.game.discard_pile:
            top_card = self.game.discard_pile[-1]
            self.canvas.create_text(680, 80, text=str(top_card.value), font=("Arial", 16))

        # Draw player grids
        for i, player in enumerate(self.game.players):
            y_offset = i * GRID_Y_OFFSET + MARGIN
            for r, row in enumerate(player.grid):
                for c, card in enumerate(row):
                    x0 = MARGIN + c * (CARD_WIDTH + MARGIN)
                    y0 = y_offset + r * (CARD_HEIGHT + MARGIN)
                    x1 = x0 + CARD_WIDTH
                    y1 = y0 + CARD_HEIGHT

                    fill = "white" if card.revealed else "gray"
                    outline_color = "black"

                    # Highlight valid cards for current player
                    if player == current:
                        if self.action_phase == "initial_reveal" and not card.revealed:
                            outline_color = "green"
                        elif self.action_phase in ["choose_replace_or_discard","choose_replace_mandatory"] and current.held_card:
                            outline_color = "green"
                        elif self.action_phase == "choose_replace_or_discard_reveal" and not card.revealed:
                            outline_color = "green"

                    rect = self.canvas.create_rectangle(x0, y0, x1, y1, fill=fill, outline=outline_color, width=2)
                    text = self.canvas.create_text(
                        x0 + CARD_WIDTH / 2, y0 + CARD_HEIGHT / 2,
                        text=str(card.value) if card.revealed else "?",
                        font=("Arial", 14)
                    )
                    self.canvas.tag_bind(rect, "<Button-1>",
                                         lambda e, player_idx=i, row=r, col=c: self.card_clicked(player_idx, row, col))
                    self.canvas.tag_bind(text, "<Button-1>",
                                         lambda e, player_idx=i, row=r, col=c: self.card_clicked(player_idx, row, col))

        # Draw held card
        self.draw_held_card()
        # Bind deck/discard clicks
        self.canvas.tag_bind(self.deck_rect, "<Button-1>", lambda e: self.deck_clicked())
        self.canvas.tag_bind(self.discard_rect, "<Button-1>", lambda e: self.discard_clicked())

    def draw_held_card(self):
        if self.held_card_rect:
            self.canvas.delete(self.held_card_rect)
        if self.held_card_text:
            self.canvas.delete(self.held_card_text)
        current = self.game.get_current_player()
        card = current.held_card
        if card:
            self.held_card_rect = self.canvas.create_rectangle(550, 200, 610, 290, fill="yellow")
            self.held_card_text = self.canvas.create_text(580, 245, text=str(card.value), font=("Arial", 16))

    def update_info(self, msg=None):
        current = self.game.get_current_player()
        text = f"{current.name}'s turn"
        if msg:
            text += " | " + msg
        self.info_label.config(text=text)

    # --- Clicks ---
    def deck_clicked(self):
        current = self.game.get_current_player()
        if self.action_phase in ["choose_pile", "initial_reveal"] and current.held_card is None:
            card = current.draw_from_deck(self.game.deck)
            if card:
                self.action_phase = "choose_replace_or_discard"
                self.draw_board()
                self.update_info("Card drawn from deck: choose replace or discard")

    def discard_clicked(self):
        current = self.game.get_current_player()
        if self.action_phase in ["choose_pile", "initial_reveal"] and current.held_card is None and self.game.discard_pile:
            card = current.draw_from_discard(self.game.deck)
            if card:
                self.action_phase = "choose_replace_mandatory"
                self.draw_board()
                self.update_info("Card drawn from discard: must replace a card")

    def card_clicked(self, player_idx, row, col):
        current = self.game.get_current_player()
        if player_idx != self.game.current_player_index:
            return
        card = current.grid[row][col]

        # --- Initial reveal phase ---
        if self.action_phase == "initial_reveal" and not card.revealed:
            current.reveal_card(row, col)
            self.initial_reveals_done[current.name] += 1
            if self.initial_reveals_done[current.name] >= 2:
                # Pass turn to next player if not everyone finished
                if all(v >= 2 for v in self.initial_reveals_done.values()):
                    self.action_phase = "choose_pile"
                else:
                    self.game.next_turn()
            self.draw_board()
            return

        # --- Deck drawn ---
        if self.action_phase == "choose_replace_or_discard" and current.held_card:
            current.replace_card(row, col, self.game)
            self.end_turn()
            return

        # --- Discard drawn ---
        if self.action_phase == "choose_replace_mandatory" and current.held_card:
            current.replace_card(row, col, self.game)
            self.end_turn()
            return

        # --- Discard + reveal ---
        if self.action_phase == "choose_replace_or_discard_reveal":
            if not card.revealed:
                current.reveal_instead_of_replace(row, col)
                self.end_turn()
                return

    def end_turn(self):
        self.action_phase = "choose_pile"
        current = self.game.get_current_player()
        current.held_card = None

        # Check end of round
        if self.game.check_end_round():
            for player in self.game.players:
                for row in player.grid:
                    for card in row:
                        card.reveal()
                player.calculate_score()
            self.draw_board()
            self.update_info("Round ended! Scores updated.")
            if any(p.score >= 100 for p in self.game.players):
                winner = min(self.game.players, key=lambda p: p.score)
                self.update_info(f"Game Over! Winner: {winner.name}")
                return
        else:
            self.game.next_turn()
            self.draw_board()
            self.update_info()
