class WordleGame:
    def __init__(self, word: str): # Constructor to initialize the game with a word
        self.word = word.lower() # The word to be guessed
        self.attempts = [] # List to store the attempts made by the player
        self.max_attempts = 6 # Maximum number of attempts allowed
        self.game_over = False # Flag to indicate if the game is over

    def is_valid_guess(self, guess: str) -> bool:
        """
        Validate if the guess meets the game requirements:
        - Length of the guess should be equal to the length of the word
        - The guess should only contain alphabetic characters
        
        Args:
            guess (str): The player's guess
        
        Returns:
            bool: True if the guess is valid, False otherwise
        """

        # Check if guess is empty or None
        if not guess:
            return False
        
        # Convert guess to lowercase
        guess = guess.lower()

        # Check if guess is of the same length as the word
        if len(guess) != len(self.word):
            return False
        
        # Check if guess contains only alphabetic characters (letters)
        if not guess.isalpha():
            return False
        
        return True # If all checks pass, return True

        

