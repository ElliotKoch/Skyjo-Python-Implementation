# Skyjo - 2 Players - Python Implementation

A complete Python implementation of **Skyjo**, a popular card game where players aim to minimize their points by revealing, replacing, and discarding cards on a 3×4 grid. This project includes the full game logic, player management, deck handling, and a GUI interface using **Tkinter**.

---

## 📂 Project Structure

```
skyjo-Python-Implementation/source
│
├── main.py               # Entry point of the program
├── game.py               # Game logic (turns, deck, discard pile, final round)
├── player.py             # Player class (grid, score, actions)
├── card.py               # Card class (value, revealed/hidden state)
├── deck.py               # Deck class (card distribution, draw, discard)
└── gui.py                # Tkinter GUI for interactive gameplay
```

---

## 🎮 Features

* Full **Skyjo game logic** with:

  * 3×4 player grid
  * Card drawing from deck or discard pile
  * Card replacement and discarding
  * Triple-column elimination rule
  * Round scoring
  * Final round detection
* **Graphical User Interface**:

  * Display player grids
  * Highlight current player
  * Interactive card selection
  * Real-time score updates
* Supports **2 players** (expandable to more)
* Automatic **deck reshuffling** when empty
* Easy-to-extend architecture for additional rules or players

---

## ⚙️ Installation & Setup

Make sure you have **Python 3.12.10** installed.

1. **Clone the repository**

   ```bash
   git clone https://github.com/ElliotKoch/Skyjo-Python-Implementation-main.git
   cd Skyjo-Python-Implementation-main
   ```

2. **Create a virtual environment**

   ```bash
   python -m venv .venv
   # Windows
   .venv\Scripts\activate
   # Linux/Mac
   source .venv/bin/activate
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Run the game**

   ```bash
   python main.py
   ```

5. **Deactivate the virtual environment (optional)**

   ```bash
   deactivate
   ```

---

## 📝 How to Play

1. Each player starts with a 3×4 grid of face-down cards.
2. Players take turns drawing a card from the **deck** or the **discard pile**.
3. The drawn card can **replace a card in the grid** or be discarded.
4. After discarding, the player can **reveal a hidden card** instead.
5. Revealing all cards triggers the **final round**:

   * Other players get one more turn.
   * Scores are tallied at the end.
6. Columns with **3 identical revealed cards** are removed automatically.
7. The player with the **lowest total score** at the end of the round wins.

---

## 🛠️ Dependencies

The project relies on the following Python packages (as per `requirements.txt`):

* Tkinter (built-in GUI library)
* asttokens, attrs, beautifulsoup4, bleach, docopt, executing, fastjsonschema, ipython, jedi, Jinja2, jsonschema, matplotlib-inline, nbclient, nbconvert, nbformat, packaging, pipreqs, prompt_toolkit, Pygments, requests, tornado, typing_extensions, and more.

> See full `requirements.txt` for all dependencies.

---

## 🔧 Contributing

Contributions are welcome! You can:

* Add more players or AI opponents
* Improve GUI visuals
* Add new game rules or modes
* Optimize game logic or card handling

---

## 🏆 License

This project is **MIT licensed** – feel free to use and modify it freely.

---

## ⚡ Notes

* The game is currently tested for **2 players**.
* Ensure your terminal or IDE supports Tkinter GUI windows.
* Python 3.12.10 is recommended for full compatibility with `requirements.txt`.
