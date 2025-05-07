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

        