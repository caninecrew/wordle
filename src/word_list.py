from pathlib import Path
import random

class WordList:
    def __init__(self):
        """
        Initialize the WordList class.
        """
        self.answers = []
        self.allowed_guesses = []
        self.load_words()

    def load_words(self):
        data_dir = Path(__file__).parent / "data"

        # Load answer words
        with open(data_dir / "wordle-answers-alphabetical.txt", "r") as f:
            self.answers = [word.strip().lower() for word in f.readlines()]

        # Load allowed guesses
        with open(data_dir / "wordle-allowed-guesses.txt", "r") as f:
            self.allowed_guesses = [word.strip().lower() for word in f.readlines()]

        # Combine both lists for valid guesses
        self.valid_words = set(self.answers + self.allowed_guesses)


        