class WordleGame:
    def __init__(self, word: str): # Constructor to initialize the game with a word
        self.word = word.lower() # The word to be guessed
        self.attempts = [] # List to store the attempts made by the player
        self.max_attempts = 6 # Maximum number of attempts allowed
        self.game_over = False # Flag to indicate if the game is over

    