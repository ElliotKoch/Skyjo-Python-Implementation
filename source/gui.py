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

        # Main canvas
        self.canvas = tk.Canvas(self, width=CANVAS_WIDTH, height=CANVAS_HEIGHT)
        self.canvas.pack()

        # Information label (turn, instructions, etc.)
        self.info_label = tk.Label(self, text="", font=("Arial", 14))
        self.info_label.pack(pady=5)

        # Continue button (shown only at end of round)
        self.continue_button = tk.Button(
            self, text="CONTINUE", font=("Arial", 14, "bold"),
            bg="green", fg="white", command=self.start_new_round
        )
        self.continue_button.pack_forget()

        # Track game state
        self.action_phase = "initial_reveal"
        self.initial_reveals_done = {player.name: 0 for player in self.game.players}

        self.deck_rect = None
        self.discard_rect = None

        self.draw_board()
        self.update_info("Reveal 2 cards each")

    def draw_board(self):
        # Clear canvas before redrawing
        self.canvas.delete("all")
        current = self.game.get_current_player()

        for i, player in enumerate(self.game.players):
            # Vertical positioning for each player
            y_offset = i * GRID_Y_OFFSET + MARGIN
            grid_height = 3 * (CARD_HEIGHT + MARGIN) - MARGIN

            # Player name and score
            name_x = MARGIN + 20
            name_y = y_offset + grid_height / 2
            self.canvas.create_text(name_x, name_y, text=player.name,
                                    font=("Arial", 16, "bold"), anchor="w")
            self.canvas.create_text(name_x, name_y + 20, text=f"Score: {player.score}",
                                    font=("Arial", 12), anchor="w")

            # Horizontal alignment for the 4×3 grid
            start_x = (CANVAS_WIDTH - 4 * (CARD_WIDTH + MARGIN)) // 2

            # Draw all cards in player's grid
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

                    # Highlight logic depending on phase and state
                    if player == current:
                        if self.action_phase == "choose_replace_or_discard":
                            outline = "red"
                        elif self.action_phase == "choose_replace_mandatory":
                            outline = "red"
                        elif self.action_phase == "choose_replace_or_discard_reveal" and not card.revealed:
                            outline = "red"
                        elif self.action_phase == "initial_reveal" and not card.revealed:
                            outline = "red"

                    rect = self.canvas.create_rectangle(
                        x0, y0, x1, y1, fill=fill, outline=outline, width=2
                    )
                    text = self.canvas.create_text(
                        (x0+x1)/2, (y0+y1)/2, font=("Purisa", 20),
                        text=str(card.value) if card.revealed else "?"
                    )

                    # Bind card clicks
                    self.canvas.tag_bind(rect, "<Button-1>",
                                         lambda e, pi=i, row=r, col=c: self.card_clicked(pi, row, col))
                    self.canvas.tag_bind(text, "<Button-1>",
                                         lambda e, pi=i, row=r, col=c: self.card_clicked(pi, row, col))

            # Draw deck and discard only for current player
            if player == current:
                # Determine highlight colors
                deck_color = "red" if self.action_phase == "choose_pile" else "black"
                discard_color = "red" if self.action_phase in ("choose_pile", "choose_replace_or_discard") else "black"

                # Deck position
                deck_x0 = start_x + 4 * (CARD_WIDTH + MARGIN) + 20
                deck_y0 = y_offset
                deck_x1 = deck_x0 + CARD_WIDTH
                deck_y1 = deck_y0 + CARD_HEIGHT

                # Draw deck
                self.deck_rect = self.canvas.create_rectangle(
                    deck_x0, deck_y0, deck_x1, deck_y1,
                    fill="white", outline=deck_color,
                    width=3 if deck_color == "red" else 1
                )
                self.canvas.create_text(deck_x0 + CARD_WIDTH//2,
                                        deck_y0 + CARD_HEIGHT//2, font=("Purisa", 16), text="Deck")
                self.canvas.tag_bind(self.deck_rect, "<Button-1>",
                                     lambda e: self.deck_clicked())

                # Draw discard pile
                discard_x0 = deck_x0
                discard_y0 = deck_y0 + CARD_HEIGHT + 20
                discard_x1 = discard_x0 + CARD_WIDTH
                discard_y1 = discard_y0 + CARD_HEIGHT

                self.discard_rect = self.canvas.create_rectangle(
                    discard_x0, discard_y0, discard_x1, discard_y1,
                    fill="white", outline=discard_color,
                    width=3 if discard_color == "red" else 1
                )

                # Display top card of discard pile
                if self.game.discard_pile:
                    top_card = self.game.discard_pile[-1]
                    self.canvas.create_text(
                        discard_x0 + CARD_WIDTH//2,
                        discard_y0 + CARD_HEIGHT//2,
                        text=str(top_card.value), font=("Purisa", 20)
                    )

                self.canvas.tag_bind(self.discard_rect, "<Button-1>",
                                     lambda e: self.discard_clicked())

        # Draw the held (drawn) card visually on the side
        self.draw_held_card()

    def draw_held_card(self):
        # Remove old held card graphics
        if self.held_card_rect:
            self.canvas.delete(self.held_card_rect)
        if self.held_card_text:
            self.canvas.delete(self.held_card_text)

        current = self.game.get_current_player()
        card = current.held_card

        # Display held card next to deck
        if card:
            deck_coords = self.canvas.coords(self.deck_rect)
            x0 = deck_coords[2] + 10
            y0 = deck_coords[1]
            x1 = x0 + CARD_WIDTH
            y1 = y0 + CARD_HEIGHT

            self.held_card_rect = self.canvas.create_rectangle(
                x0, y0, x1, y1, fill="yellow"
            )
            self.held_card_text = self.canvas.create_text(
                (x0+x1)/2, (y0+y1)/2, text=str(card.value), font=("Purisa", 20) 
            )

    def update_info(self, msg=""):
        # Update instruction/status label
        current = self.game.get_current_player()
        self.info_label.config(text=f"{current.name}'s turn | {msg}")

    # ---------- User Interaction ----------

    def deck_clicked(self):
        # Handle drawing from the deck
        current = self.game.get_current_player()
        if self.action_phase == "choose_pile" and current.held_card is None:
            card = current.draw_from_deck(self.game.deck)
            if card:
                self.action_phase = "choose_replace_or_discard"
                self.draw_board()
                self.update_info("Card drawn: choose to replace or discard")

    def discard_clicked(self):
        # Handle drawing or discarding to the discard pile
        current = self.game.get_current_player()

        # Draw from discard pile
        if self.action_phase == "choose_pile" and current.held_card is None and self.game.discard_pile:
            card = current.draw_from_discard(self.game.deck)
            if card:
                self.action_phase = "choose_replace_mandatory"
                self.draw_board()
                self.update_info("Card drawn from discard: must replace a card")

        # Discard held card
        elif self.action_phase == "choose_replace_or_discard" and current.held_card:
            current.discard_drawn_card(self.game.deck)
            self.action_phase = "choose_replace_or_discard_reveal"
            self.draw_board()
            self.update_info("Card discarded: reveal one hidden card")

    def card_clicked(self, player_idx, row, col):
        # Handle card click inside grid
        current = self.game.get_current_player()
        if player_idx != self.game.current_player_index:
            return

        card = current.grid[row][col]

        # Initial 2-card reveal phase
        if self.action_phase == "initial_reveal" and not card.revealed:
            current.reveal_card(row, col)
            self.initial_reveals_done[current.name] += 1

            # Move to next player or into normal play
            if self.initial_reveals_done[current.name] >= 2:
                if all(v >= 2 for v in self.initial_reveals_done.values()):
                    self.action_phase = "choose_pile"
                else:
                    self.game.next_turn()

            self.draw_board()
            self.update_info("Reveal 2 cards each")
            return

        # Replace card using drawn card
        if self.action_phase.startswith("choose_replace") and current.held_card:
            current.replace_card(row, col, self.game.deck)
            current.held_card = None
            self.end_turn()
            return

        # Reveal instead of replacing (after discarding)
        if self.action_phase == "choose_replace_or_discard_reveal" and not card.revealed:
            current.reveal_instead_of_replace(row, col)
            self.end_turn()

    def end_turn(self):
        # Apply triple-column rule for each player
        current = self.game.get_current_player()
        for player in self.game.players:
            player.check_triple_columns(self.game.discard_pile)

        # Trigger final round if needed
        if not self.game.final_round_triggered:
            if current.all_cards_revealed():
                self.game.final_round_triggered = True
                self.game.final_round_triggered_by = current
                self.game.final_turns_remaining = len(self.game.players) - 1
        else:
            if current != self.game.final_round_triggered_by:
                self.game.final_turns_remaining -= 1

        # End round or continue play
        if self.game.check_end_round():
            self.end_round()
        else:
            self.game.next_turn()
            self.action_phase = "choose_pile"
            self.draw_board()
            self.update_info("Next turn")

    def end_round(self):
        # Reveal remaining cards, apply triples, and calculate scores
        for player in self.game.players:
            for row in player.grid:
                for card in row:
                    if card:
                        card.reveal()

            player.check_triple_columns(self.game.discard_pile)
            player.calculate_score()

        # Determine winner of this round
        winner = min(self.game.players, key=lambda p: p.score)
        self.update_info(f"Round ended. Winner: {winner.name}")

        # Show continue button to proceed to next round
        self.continue_button.pack()
        self.draw_board()

    def start_new_round(self):
        # Reset UI and game state for the next round
        self.continue_button.pack_forget()
        self.game.reset_round()
        self.initial_reveals_done = {player.name: 0 for player in self.game.players}
        self.action_phase = "initial_reveal"
        self.draw_board()
        self.update_info("New round started! Reveal 2 cards.")
