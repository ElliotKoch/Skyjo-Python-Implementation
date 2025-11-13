# gui.py
import tkinter as tk
from game import Game
from deck import Deck

CARD_WIDTH = 60
CARD_HEIGHT = 90
MARGIN = 10
GRID_Y_OFFSET = 350
CANVAS_WIDTH = 800
CANVAS_HEIGHT = 650

class GameWindow(tk.Tk):
    def __init__(self, game: Game):
        super().__init__()
        self.title("Skyjo - 2 Players")
        self.game = game
        self.held_card_rect = None
        self.held_card_text = None

        self.canvas = tk.Canvas(self, width=CANVAS_WIDTH, height=CANVAS_HEIGHT)
        self.canvas.pack()
        self.info_label = tk.Label(self, text="", font=("Arial", 14))
        self.info_label.pack(pady=5)
        self.continue_button = tk.Button(self, text="CONTINUE", font=("Arial", 14, "bold"),
                                         bg="green", fg="white", command=self.start_new_round)
        self.continue_button.pack_forget()

        self.action_phase = "initial_reveal"
        self.initial_reveals_done = {player.name: 0 for player in self.game.players}

        self.deck_rect = None
        self.discard_rect = None

        self.draw_board()
        self.update_info("Reveal 2 cards each")

    def draw_board(self):
        self.canvas.delete("all")
        current = self.game.get_current_player()
        for i, player in enumerate(self.game.players):
            y_offset = i * GRID_Y_OFFSET + MARGIN
            grid_height = 3 * (CARD_HEIGHT + MARGIN) - MARGIN
            name_x = MARGIN + 20
            name_y = y_offset + grid_height / 2
            self.canvas.create_text(name_x, name_y, text=player.name, font=("Arial", 16, "bold"), anchor="w")
            self.canvas.create_text(name_x, name_y + 20, text=f"Score: {player.score}", font=("Arial", 12), anchor="w")

            start_x = (CANVAS_WIDTH - 4 * (CARD_WIDTH + MARGIN)) // 2
            for r, row in enumerate(player.grid):
                for c, card in enumerate(row):
                    if card is None:
                        continue
                    x0 = start_x + c * (CARD_WIDTH + MARGIN)
                    y0 = y_offset + r * (CARD_HEIGHT + MARGIN)
                    x1 = x0 + CARD_WIDTH
                    y1 = y0 + CARD_HEIGHT
                    fill = "white" if card.revealed else "gray"

                    outline = "black"
                    # --- Highlight logic per phase ---
                    if player == current:
                        if self.action_phase == "choose_replace_or_discard":
                            outline = "red"
                        elif self.action_phase == "choose_replace_mandatory":
                            outline = "red"  # Only grid cards, discard NOT highlighted
                        elif self.action_phase == "choose_replace_or_discard_reveal":
                            if not card.revealed:
                                outline = "red"
                        elif self.action_phase == "initial_reveal" and not card.revealed:
                            outline = "red"

                    rect = self.canvas.create_rectangle(x0, y0, x1, y1, fill=fill, outline=outline, width=2)
                    text = self.canvas.create_text((x0+x1)/2, (y0+y1)/2, text=str(card.value) if card.revealed else "?")
                    self.canvas.tag_bind(rect, "<Button-1>", lambda e, pi=i, row=r, col=c: self.card_clicked(pi, row, col))
                    self.canvas.tag_bind(text, "<Button-1>", lambda e, pi=i, row=r, col=c: self.card_clicked(pi, row, col))

            # Draw deck/discard for current player
            if player == current:
                deck_color = "red" if self.action_phase == "choose_pile" and current.held_card is None else "black"
                discard_color = "red" if self.action_phase == "choose_pile" and current.held_card is None else "black"

                deck_x0 = start_x + 4 * (CARD_WIDTH + MARGIN) + 20
                deck_y0 = y_offset
                deck_x1 = deck_x0 + CARD_WIDTH
                deck_y1 = deck_y0 + CARD_HEIGHT
                self.deck_rect = self.canvas.create_rectangle(deck_x0, deck_y0, deck_x1, deck_y1,
                                                              fill="white", outline=deck_color, width=3 if deck_color=="red" else 1)
                self.canvas.create_text(deck_x0 + CARD_WIDTH//2, deck_y0 + CARD_HEIGHT//2, text="Deck")
                self.canvas.tag_bind(self.deck_rect, "<Button-1>", lambda e: self.deck_clicked())

                discard_x0 = deck_x0
                discard_y0 = deck_y0 + CARD_HEIGHT + 20
                discard_x1 = discard_x0 + CARD_WIDTH
                discard_y1 = discard_y0 + CARD_HEIGHT
                self.discard_rect = self.canvas.create_rectangle(discard_x0, discard_y0, discard_x1, discard_y1,
                                                                 fill="white", outline=discard_color, width=3 if discard_color=="red" else 1)
                if self.game.discard_pile:
                    top_card = self.game.discard_pile[-1]
                    self.canvas.create_text(discard_x0 + CARD_WIDTH//2, discard_y0 + CARD_HEIGHT//2,
                                            text=str(top_card.value), font=("Arial", 16))
                self.canvas.tag_bind(self.discard_rect, "<Button-1>", lambda e: self.discard_clicked())

        self.draw_held_card()

    def draw_held_card(self):
        if self.held_card_rect:
            self.canvas.delete(self.held_card_rect)
        if self.held_card_text:
            self.canvas.delete(self.held_card_text)
        current = self.game.get_current_player()
        card = current.held_card
        if card:
            # Always position held card next to deck
            deck_coords = self.canvas.coords(self.deck_rect)
            x0 = deck_coords[2] + 10
            y0 = deck_coords[1]
            x1 = x0 + CARD_WIDTH
            y1 = y0 + CARD_HEIGHT
            self.held_card_rect = self.canvas.create_rectangle(x0, y0, x1, y1, fill="yellow")
            self.held_card_text = self.canvas.create_text((x0+x1)/2, (y0+y1)/2, text=str(card.value))

    def update_info(self, msg=""):
        current = self.game.get_current_player()
        self.info_label.config(text=f"{current.name}'s turn | {msg}")

    # --- Clicks ---
    def deck_clicked(self):
        current = self.game.get_current_player()
        if self.action_phase == "choose_pile" and current.held_card is None:
            card = current.draw_from_deck(self.game.deck)
            if card:
                self.action_phase = "choose_replace_or_discard"
                self.draw_board()
                self.update_info("Card drawn: choose to replace or discard")

    def discard_clicked(self):
        current = self.game.get_current_player()
        if self.action_phase == "choose_pile" and current.held_card is None and self.game.discard_pile:
            card = current.draw_from_discard(self.game.deck)
            if card:
                self.action_phase = "choose_replace_mandatory"
                self.draw_board()
                self.update_info("Card drawn from discard: must replace a card")
        elif self.action_phase == "choose_replace_or_discard" and current.held_card:
            current.discard_drawn_card(self.game.deck)
            self.action_phase = "choose_replace_or_discard_reveal"
            self.draw_board()
            self.update_info("Card discarded: reveal one hidden card")

    def card_clicked(self, player_idx, row, col):
        current = self.game.get_current_player()
        if player_idx != self.game.current_player_index:
            return
        card = current.grid[row][col]

        if self.action_phase == "initial_reveal" and not card.revealed:
            current.reveal_card(row, col)
            self.initial_reveals_done[current.name] += 1
            if self.initial_reveals_done[current.name] >= 2:
                if all(v >= 2 for v in self.initial_reveals_done.values()):
                    self.action_phase = "choose_pile"
                    self.game.current_player_index = 0
                else:
                    self.game.next_turn()
            self.draw_board()
            self.update_info("Reveal 2 cards each")
            return

        if self.action_phase.startswith("choose_replace") and current.held_card:
            current.replace_card(row, col, self.game.deck)
            current.held_card = None
            self.end_turn()
            return

        if self.action_phase == "choose_replace_or_discard_reveal" and not card.revealed:
            current.reveal_instead_of_replace(row, col)
            self.end_turn()

    def end_turn(self):
        current = self.game.get_current_player()
        for player in self.game.players:
            player.check_triple_columns(self.game.discard_pile)

        if not self.game.final_round_triggered:
            if current.all_cards_revealed():
                self.game.final_round_triggered = True
                self.game.final_round_triggered_by = current
                self.game.final_turns_remaining = len(self.game.players) - 1
        else:
            if current != self.game.final_round_triggered_by:
                self.game.final_turns_remaining -= 1

        if self.game.check_end_round():
            self.end_round()
        else:
            self.game.next_turn()
            self.action_phase = "choose_pile"
            self.draw_board()
            self.update_info("Next turn")

    def end_round(self):
        for player in self.game.players:
            for row in player.grid:
                for card in row:
                    if card:
                        card.reveal()
            player.check_triple_columns(self.game.discard_pile)
            player.calculate_score()
        winner = min(self.game.players, key=lambda p: p.score)
        self.update_info(f"Round ended. Winner: {winner.name}")
        self.continue_button.pack()
        self.draw_board()

    def start_new_round(self):
        self.continue_button.pack_forget()
        self.game.reset_round()
        self.initial_reveals_done = {player.name: 0 for player in self.game.players}
        self.action_phase = "initial_reveal"
        self.draw_board()
        self.update_info("New round started! Reveal 2 cards.")
