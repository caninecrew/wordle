from .word_list import WordList

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
            tuple containing:
                bool: True if the guess is correct, False otherwise
                list[tuple[str, str]]: List of (letter, status) pairs where status is:
                    - 'correct' - right letter, right position
                    - 'present' - right letter, wrong position
                    - 'absent' - letter not in word
                bool: Game over status
        """

        # Check if the game is already over
        if self.game_over:
            return False, [], True
        
        # Validate the guess
        valid = self.is_valid_guess(guess)
        if not valid:
            print(f"Debug - Validation failed for guess: '{guess}'")
            return False, [], False
        
        # Convert guess to lowercase
        guess = guess.lower()
        
        self.attempts.append(guess) # Add the guess to the attempts list

        # Process each letter in the guess
        result = []
        for i, letter in enumerate(guess): # Iterate through each letter in the guess
            if letter == self.word[i]:
                result.append((letter, 'correct'))
            elif letter in self.word:
                result.append((letter, 'present'))
            else:
                result.append((letter, 'absent'))

        # Update game state
        is_won = guess == self.word
        is_lost = len(self.attempts) >= self.max_attempts
        self.game_over = is_won or is_lost 

        return True, result, self.game_over

    def is_valid_guess(self, guess: str) -> bool:
        """
        Validate if the guess meets the game requirements
        """
        if not guess:
            return False
            
        guess = guess.lower()
        
        if len(guess) != len(self.word):
            return False
            
        if not guess.isalpha():
            return False
            
        # Check if the word is in our valid word list
        if not self.word_list.is_valid_word(guess):
            print("Not a valid word!")
            return False
            
        return True
    
    def display_guess(self, guess_result: list[tuple[str, str]]) -> None:
        """ 
        Display the result of the guess in a formatted string.
        
        Args:
            guess_result (list[tuple[str, str]]): List of (letter, status) pairs
        
        Returns:
            str: Formatted string showing the guess result
        """
        
        for letter, status in guess_result:
            if status == 'correct':
                print(f"[{letter.upper()}]", end=" ")
            elif status == 'present':
                print(f"({letter})", end=" ")
            else:
                print(f' {letter}', end=" ")

        print() # Print a newline at the end of the guess result

    