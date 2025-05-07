from .word_list import WordList

class WordleGame:
    def __init__(self, word: str): # Constructor to initialize the game with a word
        self.word = word.lower() # The word to be guessed
        self.attempts = [] # List to store the attempts made by the player
        self.max_attempts = 6 # Maximum number of attempts allowed
        self.game_over = False # Flag to indicate if the game is over
        self.games_played = 0 # Number of games played
        self.games_won = 0 # Number of games won
        self.current_streak = 0 # Current winning streak
        self.max_streak = 0 # Maximum winning streak
        self.word_list = WordList() # Instance of WordList to access the word lists

    def make_guess(self, guess: str) -> list[tuple[str, str]]:
        """
        Process the player's guess and return feedback for each letter.
        Returns:
            list[tuple[str, str]]: A list of (char, status) where status is:
                'correct' - Letter is correct and in the correct position
                'present' - Letter is in the word but in the wrong position
                'absent' - Letter is not in the word
        """
        guess = guess.lower()
        result = []

        for i, letter in enumerate(guess):
            if letter == self.word[i]:
                result.append((letter.upper(), 'correct'))
            elif letter in self.word:
                result.append((letter.upper(), 'present'))
            else:
                result.append((letter.upper(), 'absent'))

        self.attempts.append(guess)
        return result

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
        """Display the result of a guess with colored formatting"""
        result_string = ""
        for letter, status in guess_result:
            if status == 'correct':
                result_string += f"[{letter}] "
            elif status == 'present':
                result_string += f"({letter}) "
            else:
                result_string += f"{letter} "
        print(result_string.strip())
        print(f"Attempts remaining: {self.max_attempts - len(self.attempts)}")

    def is_won(self) -> bool:
        """
        Check if the game is won.
        Returns:
            bool: True if the player has guessed the word correctly, False otherwise.
        """
        return self.word in self.attempts

    def is_over(self) -> bool:
        """
        Check if the game is over (either won or max attempts reached).
        Returns:
            bool: True if the game is over, False otherwise.
        """
        return self.is_won() or len(self.attempts) >= self.max_attempts

