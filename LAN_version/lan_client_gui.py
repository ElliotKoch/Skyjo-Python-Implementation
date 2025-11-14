# lan_client_gui.py
import tkinter as tk
import json
import socket
from threading import Thread

CARD_WIDTH = 60
CARD_HEIGHT = 90
MARGIN = 10
GRID_Y_OFFSET = 350
CANVAS_WIDTH = 800
CANVAS_HEIGHT = 650

class LANGameClient(tk.Tk):
    def __init__(self, host, port, player_name):
        super().__init__()
        self.title(f"Skyjo LAN - {player_name}")
        self.player_name = player_name

        # --- Networking ---
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((host, port))
        self.sock.sendall(player_name.encode("utf-8"))

        # Thread to listen to server updates
        self.running = True
        Thread(target=self.receive_loop, daemon=True).start()

        # --- GUI elements ---
        self.canvas = tk.Canvas(self, width=CANVAS_WIDTH, height=CANVAS_HEIGHT)
        self.canvas.pack()
        self.info_label = tk.Label(self, text="", font=("Arial", 14))
        self.info_label.pack(pady=5)

        # Game state from server
        self.game_state = None
        self.action_phase = None
        self.held_card = None
        self.deck_rect = None
        self.discard_rect = None
        self.held_card_rect = None
        self.held_card_text = None

        # Bind clicks
        self.canvas.bind("<Button-1>", self.click_handler)

    # ---------------- Networking ----------------
    def receive_loop(self):
        """Receive game state from server."""
        while self.running:
            try:
                data = self.sock.recv(65536)
                if not data:
                    break
                state = json.loads(data.decode("utf-8"))
                self.game_state = state["game_state"]
                self.action_phase = state.get("phase")
                self.draw_board()
                self.update_info(state.get("message"))
            except Exception as e:
                print("Receive error:", e)
                break

    def send_action(self, action):
        """Send an action to the server."""
        try:
            self.sock.sendall(json.dumps(action).encode("utf-8"))
        except Exception as e:
            print("Send error:", e)

    # ---------------- GUI ----------------
    def draw_board(self):
        self.canvas.delete("all")
        if not self.game_state:
            return

        for i, player in enumerate(self.game_state["players"]):
            y_offset = i * GRID_Y_OFFSET + MARGIN
            name_x = MARGIN + 20
            name_y = y_offset + 50
            self.canvas.create_text(name_x, name_y, text=player["name"], font=("Arial", 16, "bold"), anchor="w")
            self.canvas.create_text(name_x, name_y + 20, text=f"Score: {player['score']}", font=("Arial", 12), anchor="w")

            start_x = (CANVAS_WIDTH - 4 * (CARD_WIDTH + MARGIN)) // 2

            for r, row in enumerate(player["grid"]):
                for c, card in enumerate(row):
                    if card is None:
                        continue
                    x0 = start_x + c * (CARD_WIDTH + MARGIN)
                    y0 = y_offset + r * (CARD_HEIGHT + MARGIN)
                    x1 = x0 + CARD_WIDTH
                    y1 = y0 + CARD_HEIGHT
                    fill = "white" if card["revealed"] else "gray"
                    outline = "red" if player["name"] == self.player_name and self.is_card_clickable(r, c) else "black"
                    self.canvas.create_rectangle(x0, y0, x1, y1, fill=fill, outline=outline, width=2)
                    self.canvas.create_text(x0 + CARD_WIDTH/2, y0 + CARD_HEIGHT/2,
                                            text=str(card["value"]) if card["revealed"] else "?", font=("Arial", 14))

        # Deck and discard
        self.draw_pile_discard()

    def draw_pile_discard(self):
        if not self.game_state:
            return
        start_x = (CANVAS_WIDTH - 4 * (CARD_WIDTH + MARGIN)) // 2
        y_offset = GRID_Y_OFFSET + MARGIN
        # Deck rectangle
        deck_x0 = start_x + 4 * (CARD_WIDTH + MARGIN) + 20
        deck_y0 = y_offset
        deck_x1 = deck_x0 + CARD_WIDTH
        deck_y1 = deck_y0 + CARD_HEIGHT
        deck_color = "red" if self.action_phase == "choose_pile" else "black"
        self.deck_rect = self.canvas.create_rectangle(deck_x0, deck_y0, deck_x1, deck_y1,
                                                      fill="white", outline=deck_color, width=3 if deck_color=="red" else 1)
        self.canvas.create_text(deck_x0 + CARD_WIDTH/2, deck_y0 + CARD_HEIGHT/2, text="Deck")

        # Discard rectangle
        discard_x0 = deck_x0
        discard_y0 = deck_y0 + CARD_HEIGHT + 20
        discard_x1 = discard_x0 + CARD_WIDTH
        discard_y1 = discard_y0 + CARD_HEIGHT
        discard_color = "red" if self.action_phase == "choose_discard" else "black"
        self.discard_rect = self.canvas.create_rectangle(discard_x0, discard_y0, discard_x1, discard_y1,
                                                         fill="white", outline=discard_color, width=3 if discard_color=="red" else 1)
        # Top discard card
        top_discard = self.game_state.get("top_discard")
        if top_discard:
            self.canvas.create_text(discard_x0 + CARD_WIDTH/2, discard_y0 + CARD_HEIGHT/2,
                                    text=str(top_discard["value"]), font=("Arial", 16))

        # Draw held card on side of deck
        self.draw_held_card(deck_x1 + 10, deck_y0)

    def draw_held_card(self, x=0, y=0):
        if not self.game_state:
            return
        held = None
        for p in self.game_state["players"]:
            if p["name"] == self.player_name:
                held = p.get("held_card")
        if self.held_card_rect:
            self.canvas.delete(self.held_card_rect)
        if self.held_card_text:
            self.canvas.delete(self.held_card_text)
        if held:
            x0 = x
            y0 = y
            x1 = x0 + CARD_WIDTH
            y1 = y0 + CARD_HEIGHT
            self.held_card_rect = self.canvas.create_rectangle(x0, y0, x1, y1, fill="yellow")
            self.held_card_text = self.canvas.create_text((x0+x1)/2, (y0+y1)/2, text=str(held["value"]), font=("Arial", 16))

    def update_info(self, msg=None):
        text = f"Your turn: {self.player_name}"
        if msg:
            text += " | " + msg
        self.info_label.config(text=text)

    # ---------------- Click handling ----------------
    def click_handler(self, event):
        if not self.game_state or not self.action_phase:
            return
        x, y = event.x, event.y

        # Check deck click
        if self.deck_rect and self.coords_inside_rect(x, y, self.canvas.coords(self.deck_rect)):
            if self.action_phase == "choose_pile":
                self.send_action({"action": "draw_deck"})
            return

        # Check discard click
        if self.discard_rect and self.coords_inside_rect(x, y, self.canvas.coords(self.discard_rect)):
            if self.action_phase == "choose_discard":
                self.send_action({"action": "draw_discard"})
            return

        # Check grid cards
        start_x = (CANVAS_WIDTH - 4 * (CARD_WIDTH + MARGIN)) // 2
        for r in range(3):
            for c in range(4):
                x0 = start_x + c * (CARD_WIDTH + MARGIN)
                y0 = (GRID_Y_OFFSET + MARGIN if self.player_name != self.game_state["players"][0]["name"] else MARGIN) + r * (CARD_HEIGHT + MARGIN)
                if self.coords_inside_rect(x, y, [x0, y0, x0 + CARD_WIDTH, y0 + CARD_HEIGHT]):
                    if self.is_card_clickable(r, c):
                        self.send_action({"action": "card_click", "row": r, "col": c})
                        return

    def coords_inside_rect(self, x, y, rect):
        x0, y0, x1, y1 = rect
        return x0 <= x <= x1 and y0 <= y <= y1

    def is_card_clickable(self, row, col):
        """Determine if the grid card is clickable for the current phase."""
        # Highlight cards only if player can click them
        return True  # For simplicity; server will validate

if __name__ == "__main__":
    host = "192.168.1.100"  # server LAN IP
    port = 5555
    player_name = input("Enter your player name: ")
    client = LANGameClient(host, port, player_name)
    client.mainloop()