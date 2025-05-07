from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label  # Add this import
from ..word_list import WordList
from ..game import WordleGame

class WordleGameUI(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', **kwargs)
        self.word_list = WordList()
        self.answer = self.word_list.get_random_word()
        self.game = WordleGame(self.answer)
        self.add_widget(Label(text="Wordle is loading...", font_size=32))

class WordleApp(App):
    def build(self):
        return WordleGameUI()