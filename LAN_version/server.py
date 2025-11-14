# lan_server.py
import socket
import json
import threading
from game import Game
from player import Player
from deck import Deck

HOST = "192.168.1.100"  # Listen on all interfaces for LAN
PORT = 5555       # TCP port
MAX_PLAYERS = 2

# ---------------- Game Server ----------------
class LANGameServer:
    def __init__(self):
        self.game = Game([f"Player{i+1}" for i in range(MAX_PLAYERS)])
        self.clients = {}  # socket -> player_name
        self.lock = threading.Lock()
        self.player_sockets = {}  # player_name -> socket

    def start(self):
        # Start TCP server
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind((HOST, PORT))
        self.sock.listen(MAX_PLAYERS)
        print(f"Server listening on {HOST}:{PORT}")

        # Accept connections
        while len(self.clients) < MAX_PLAYERS:
            client_sock, addr = self.sock.accept()
            print(f"Client connected from {addr}")
            # Receive player name
            player_name = client_sock.recv(1024).decode("utf-8")
            self.clients[client_sock] = player_name
            self.player_sockets[player_name] = client_sock
            print(f"Player registered: {player_name}")

        print("All players connected. Starting game.")
        self.game.start_game()
        self.game.current_player_index = 0
        self.broadcast_state("Game started!")

        # Start listening threads
        for client_sock in self.clients:
            threading.Thread(target=self.handle_client, args=(client_sock,), daemon=True).start()

    # ---------------- Client handler ----------------
    def handle_client(self, client_sock):
        player_name = self.clients[client_sock]
        while True:
            try:
                data = client_sock.recv(65536)
                if not data:
                    break
                action = json.loads(data.decode("utf-8"))
                self.handle_action(player_name, action)
            except Exception as e:
                print(f"Error with {player_name}: {e}")
                break
        print(f"{player_name} disconnected.")
        client_sock.close()

    # ---------------- Handle actions ----------------
    def handle_action(self, player_name, action):
        with self.lock:
            player = next(p for p in self.game.players if p.name == player_name)
            phase = self.game.phase

            msg = None

            # --- Initial reveal ---
            if phase == "setup" and action.get("action") == "card_click":
                row, col = action["row"], action["col"]
                player.reveal_card(row, col)
                msg = f"{player_name} revealed a card."
                # Check if each player revealed 2 cards
                revealed_count = sum(card.revealed for row in player.grid for card in row)
                if all(all(card.revealed for card in p.grid[:2]) for p in self.game.players):
                    self.game.phase = "play"

            # --- Main phase ---
            elif phase == "play":
                if action.get("action") == "draw_deck":
                    card = player.draw_from_deck(self.game.deck)
                    msg = f"{player_name} drew a card from deck."
                elif action.get("action") == "draw_discard":
                    card = player.draw_from_discard(self.game.deck)
                    msg = f"{player_name} drew a card from discard pile."
                elif action.get("action") == "card_click":
                    row, col = action["row"], action["col"]
                    # Check if player has held card
                    if player.held_card:
                        player.replace_card(row, col, self.game.deck)
                        msg = f"{player_name} replaced a card."
                    else:
                        player.reveal_instead_of_replace(row, col)
                        msg = f"{player_name} revealed a card."

            # --- End turn ---
            # Check columns
            for p in self.game.players:
                p.check_triple_columns(self.game.discard_pile)

            # Check if round ended
            if self.game.check_end_round():
                for p in self.game.players:
                    for row in p.grid:
                        for card in row:
                            if card:
                                card.reveal()
                    p.calculate_score()
                msg = "Round ended!"

            # Move to next player
            self.game.next_turn()
            self.broadcast_state(msg)

    # ---------------- Broadcast state ----------------
    def broadcast_state(self, message=None):
        state = self.serialize_game(message)
        for sock in self.clients:
            try:
                sock.sendall(json.dumps(state).encode("utf-8"))
            except:
                pass

    # ---------------- Serialize game ----------------
    def serialize_game(self, message=None):
        players_data = []
        for player in self.game.players:
            grid_data = []
            for row in player.grid:
                grid_data.append([
                    {"value": card.value, "revealed": card.revealed} if card else None
                    for card in row
                ])
            players_data.append({
                "name": player.name,
                "score": player.score,
                "grid": grid_data,
                "held_card": {"value": player.held_card.value} if player.held_card else None
            })

        top_discard = {"value": self.game.discard_pile[-1].value} if self.game.discard_pile else None

        return {
            "players": players_data,
            "top_discard": top_discard,
            "phase": self.game.phase,
            "message": message
        }

# ---------------- Main ----------------
if __name__ == "__main__":
    server = LANGameServer()
    server.start()
