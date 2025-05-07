class WordleGame:
    def __init__(self, word: str): # Constructor to initialize the game with a word
        self.word = word.lower() # The word to be guessed
        self.attempts = [] # List to store the attempts made by the player
        self.max_attempts = 6 # Maximum number of attempts allowed
        self.game_over = False # Flag to indicate if the game is over

    def make_guess(self, guess: str) -> str:
        """
        Process the plaer's guess and provide feedback.
        
        Args:
            guess (str): The player's guess
            
        Returns:
            str: Feedback on the guess (correct, incorrect, or game over)
        """

        # Check if the game is already over
        if self.game_over:
            return "Game is already over. Please start a new game."
        
        # Validate the guess
        if not self.is_valid_guess(guess):
            return "Invalid guess. Please try again."
        
        # Convert guess to lowercase
        guess = guess.lower()

        # Add the guess to the attempts list
        self.attempts.append(guess)

        # Check if the guess is correct
        if guess == self.word:
            self.game_over = True
            return "Congratulations! You've guessed the word correctly."

        # Check if maximum attempts have been reached
        if len(self.attempts) >= self.max_attempts:
            self.game_over = True
            return f"Game over! The correct word was '{self.word}'."

        return "Incorrect guess. Try again."


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

    