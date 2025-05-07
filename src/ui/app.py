from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from src.word_list import WordList
from src.game import Game

class WordleGameUI(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', **kwargs)
        self.word_list = WordList()
        self.answer = self.word_list.get_random_answer()
        self.game = Game(self.answer)
        # TODO: Build grid, input, feedback UI

class WordleApp(App):
    def build(self):
        return WordleGameUI()
