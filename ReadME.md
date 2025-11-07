skyjo/
│
├── main.py               # Point d'entrée du programme
├── game.py               # Gestion de la partie (cartes, pioches, tours…)
├── player.py             # Classe Joueur (cartes, score, actions)
├── card.py               # Classe Carte (valeur, état caché/révélé)
└── deck.py               # Classe Paquet (distribution, pioche, défausse)


## ⚙️ Installation & Setup
To run the project, follow these steps with Python version 3.11.9:

1. **Clone the repository**
   ```sh
   git clone https://github.com/ElliotKoch/Skyjo-Python-Implementation-main.git
   cd discord-leetcode-tracker-bot
   ```
   
2. **Setup virtual environment**
   ```sh
   python -m venv .venv
   .venv\Scripts\activate   # For Windows
   source .venv/bin/activate   # For Linux/Mac
   ```

3. **Install dependencies**
   ```sh
   pip install -r requirements.txt
   ```

4. **Run the game**
   ```sh
   python main.py
   ```

5. **Close the virtual environment**
   ```sh
   deactivate
   ```
