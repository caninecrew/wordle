from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from ..word_list import WordList
from ..game import WordleGame  # Changed from Game to WordleGame

class WordleGameUI(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', **kwargs)
        self.word_list = WordList()
        self.answer = self.word_list.get_random_word()  # Changed from get_random_answer to get_random_word
        self.game = WordleGame(self.answer)  # Changed from Game to WordleGame
        # TODO: Build grid, input, feedback UI

class WordleApp(App):
    def build(self):
        return WordleGameUI()