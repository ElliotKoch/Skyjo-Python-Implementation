# gui.py
import tkinter as tk
from game import Game

CARD_WIDTH = 60
CARD_HEIGHT = 90
MARGIN = 10
GRID_Y_OFFSET = 350  # espace vertical entre les deux joueurs
CANVAS_WIDTH = 800
CANVAS_HEIGHT = 650

class GameWindow(tk.Tk):
    def __init__(self, game: Game):
        super().__init__()
        self.title("Skyjo - 2 Players")
        self.game = game
        self.game.set_gui = self

        self.canvas = tk.Canvas(self, width=CANVAS_WIDTH, height=CANVAS_HEIGHT)
        self.canvas.pack()

        self.info_label = tk.Label(self, text="", font=("Arial", 14))
        self.info_label.pack(pady=5)

        self.continue_button = tk.Button(self, text="CONTINUE", font=("Arial", 14, "bold"), bg="green", fg="white",
                                         command=self.start_new_round)
        self.continue_button.pack(pady=10)
        self.continue_button.pack_forget()

        self.action_phase = "initial_reveal"
        self.initial_reveals_done = {player.name: 0 for player in self.game.players}
        self.held_card_rect = None
        self.held_card_text = None

        self.draw_board()
        self.update_info()

    def draw_board(self):
        self.canvas.delete("all")
        current = self.game.get_current_player()

        for i, player in enumerate(self.game.players):
            y_offset = i * GRID_Y_OFFSET + MARGIN

            # Player name to the left, centered vertically with grid
            grid_height = 3 * (CARD_HEIGHT + MARGIN) - MARGIN
            name_x = MARGIN + 20
            name_y = y_offset + grid_height / 2
            self.canvas.create_text(name_x, name_y, text=player.name, font=("Arial", 16, "bold"), anchor="w")

            # Draw score just below name
            score_y = name_y + 20
            self.canvas.create_text(
                name_x, score_y,
                text=f"Score: {player.score}",
                font=("Arial", 12),
                anchor="w"
            )

            # Grid placement
            grid_width = 4 * (CARD_WIDTH + MARGIN)
            start_x = (CANVAS_WIDTH - grid_width - 2*(CARD_WIDTH + MARGIN)) // 2 + 50  # shift a bit to right

            # Draw player grid
            for r, row in enumerate(player.grid):
                for c, card in enumerate(row):
                    x0 = start_x + c * (CARD_WIDTH + MARGIN)
                    y0 = y_offset + r * (CARD_HEIGHT + MARGIN)
                    x1 = x0 + CARD_WIDTH
                    y1 = y0 + CARD_HEIGHT

                    fill = "white" if card.revealed else "gray"
                    outline_color = "black"

                    if player == current:
                        # Initial reveal phase: highlight cards that can be flipped
                        if self.action_phase == "initial_reveal" and not card.revealed:
                            outline_color = "red"
                        # Deck-drawn card: highlight grid cards and discard pile that can be chosen
                        elif self.action_phase == "choose_replace_or_discard" and current.held_card:
                            outline_color = "red"
                        # Discard-drawn card: highlight grid cards that must be replaced
                        elif self.action_phase == "choose_replace_mandatory" and current.held_card:
                            outline_color = "red"
                        # Reveal phase after discarding: highlight hidden grid cards that can be revealed
                        elif self.action_phase == "choose_replace_or_discard_reveal" and not card.revealed:
                            outline_color = "red"

                    rect = self.canvas.create_rectangle(x0, y0, x1, y1, fill=fill, outline=outline_color, width=2)
                    text = self.canvas.create_text(
                        x0 + CARD_WIDTH / 2, y0 + CARD_HEIGHT / 2,
                        text=str(card.value) if card.revealed else "?",
                        font=("Arial", 14)
                    )
                    self.canvas.tag_bind(rect, "<Button-1>", lambda e, pi=i, row=r, col=c: self.card_clicked(pi, row, col))
                    self.canvas.tag_bind(text, "<Button-1>", lambda e, pi=i, row=r, col=c: self.card_clicked(pi, row, col))
            
            # Deck
            if self.action_phase == "choose_pile" and current.held_card is None:
                deck_color = "red"
            else:
                deck_color = "black"

            # Discard
            if (self.action_phase == "choose_pile" and current.held_card is None and self.game.discard_pile) or (self.action_phase == "choose_replace_or_discard" and current.held_card and self.game.discard_pile):
                discard_color = "red"
            else:
                discard_color = "black"

            # Draw deck/discard for active player
            if player == current:
                deck_x0 = start_x + 4 * (CARD_WIDTH + MARGIN) + 20
                deck_y0 = y_offset
                deck_x1 = deck_x0 + CARD_WIDTH
                deck_y1 = deck_y0 + CARD_HEIGHT
                self.deck_rect = self.canvas.create_rectangle(deck_x0, deck_y0, deck_x1, deck_y1,
                                                              fill="white", outline=deck_color, width=3 if deck_color=="red" else 1)
                self.canvas.tag_bind(self.deck_rect, "<Button-1>", lambda e: self.deck_clicked())
                self.canvas.create_text(deck_x0 + CARD_WIDTH//2, deck_y0 + CARD_HEIGHT//2, text="Deck")

                discard_x0 = deck_x0
                discard_y0 = deck_y0 + CARD_HEIGHT + 20
                discard_x1 = discard_x0 + CARD_WIDTH
                discard_y1 = discard_y0 + CARD_HEIGHT
                self.discard_rect = self.canvas.create_rectangle(discard_x0, discard_y0, discard_x1, discard_y1,
                                                                 fill="white", outline=discard_color, width=3 if discard_color=="red" else 1)
                # bind pour la discard pile
                self.canvas.tag_bind(self.discard_rect, "<Button-1>", lambda e: self.discard_held_card() if self.action_phase=="choose_replace_or_discard" else self.discard_clicked())

                if self.game.discard_pile:
                    top_card = self.game.discard_pile[-1]
                    self.canvas.create_text(discard_x0 + CARD_WIDTH//2, discard_y0 + CARD_HEIGHT//2,
                                            text=str(top_card.value), font=("Arial", 16))
        # Draw held card next to deck/discard
        self.draw_held_card()

    def draw_held_card(self):
        if self.held_card_rect:
            self.canvas.delete(self.held_card_rect)
        if self.held_card_text:
            self.canvas.delete(self.held_card_text)

        current = self.game.get_current_player()
        card = current.held_card
        if card:
            # Place held card next to deck or discard
            if self.action_phase in ["choose_replace_or_discard","choose_replace_or_discard_reveal"]:
                ref_coords = self.canvas.coords(self.deck_rect)
            elif self.action_phase == "choose_replace_mandatory":
                ref_coords = self.canvas.coords(self.discard_rect)
            else:
                ref_coords = [CANVAS_WIDTH - 120, 50, CANVAS_WIDTH - 60, 140]

            x0 = ref_coords[2] + 10
            y0 = ref_coords[1]
            x1 = x0 + CARD_WIDTH
            y1 = y0 + CARD_HEIGHT

            self.held_card_rect = self.canvas.create_rectangle(x0, y0, x1, y1, fill="yellow")
            self.held_card_text = self.canvas.create_text((x0+x1)/2, (y0+y1)/2, text=str(card.value), font=("Arial", 16))

    def discard_held_card(self):
        current = self.game.get_current_player()
        if current.held_card:
            # Déplace la carte piochée dans la discard pile
            self.game.discard_pile.append(current.held_card)
            current.held_card = None
            # Passer en phase révélation obligatoire
            self.action_phase = "choose_replace_or_discard_reveal"
            self.draw_board()
            self.update_info("Card discarded. Reveal one hidden card from your grid.")

    def update_info(self, msg=None):
        current = self.game.get_current_player()
        text = f"{current.name}'s turn"
        if msg:
            text += " | " + msg
        self.info_label.config(text=text)

    # --- Clicks ---
    def deck_clicked(self):
        current = self.game.get_current_player()
        if self.action_phase == "choose_pile" and current.held_card is None:
            card = current.draw_from_deck(self.game.deck)
            if card:
                self.action_phase = "choose_replace_or_discard"
                self.draw_board()
                self.update_info("Card drawn from deck: choose replace or discard")

    def discard_clicked(self):
        current = self.game.get_current_player()
        if self.action_phase == "choose_pile" and current.held_card is None and self.game.discard_pile:
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
                if all(v >= 2 for v in self.initial_reveals_done.values()):
                    # All players finished initial reveal
                    self.action_phase = "choose_pile"
                    self.game.current_player_index = 0  # reset to first player
                else:
                    self.game.next_turn()
            self.draw_board()
            self.update_info()
            return

        # --- Deck drawn: replace or discard phase ---
        if self.action_phase == "choose_replace_or_discard" and current.held_card:
            current.replace_card(row, col, self.game)
            self.end_turn()
            return

        # --- Discard drawn: must replace ---
        if self.action_phase == "choose_replace_mandatory" and current.held_card:
            current.replace_card(row, col, self.game)
            self.end_turn()
            return

        # --- Player discarded drawn card: reveal a hidden card ---
        if self.action_phase == "choose_replace_or_discard_reveal" and not card.revealed:
            current.reveal_instead_of_replace(row, col)
            self.end_turn()
            return

    def end_turn(self):
        current = self.game.get_current_player()
        current.held_card = None

        # Check end of round
        if self.game.check_end_round():
            # Reveal all cards and update scores
            for player in self.game.players:
                for row in player.grid:
                    for card in row:
                        card.reveal()
                player.calculate_score()

            # Check if someone has 100 or more points
            if any(p.score >= 100 for p in self.game.players):
                winner = min(self.game.players, key=lambda p: p.score)
                self.action_phase = "game_over"  # 🔴 Prevent any further interaction
                self.draw_board()
                self.update_info(f"Game Over! Winner: {winner.name}")
                return

            # If game not over → show continue button for next round
            else:
                self.action_phase = "round_end"  # 🟡 Disable input except Continue
                self.draw_board()
                self.update_info("Round ended! Scores updated.")
                self.continue_button.pack()  # show CONTINUE button

        else:
            # Normal next turn
            self.action_phase = "choose_pile"
            self.game.next_turn()
            self.draw_board()
            self.update_info()
        
        

    def start_new_round(self):
        # Restart a new round
        self.continue_button.pack_forget()
        self.game.reset_round()
        self.initial_reveals_done = {player.name: 0 for player in self.game.players}
        self.action_phase = "initial_reveal"
        self.draw_board()
        self.update_info("New round started! Reveal 2 cards.")