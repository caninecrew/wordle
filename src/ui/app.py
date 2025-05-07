from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label  # Add this import
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from ..word_list import WordList
from ..game import WordleGame

class WordleGameUI(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', **kwargs)
        self.word_list = WordList()
        self.answer = self.word_list.get_random_word()
        self.game = WordleGame(self.answer)
        self.add_widget(Label(text="Wordle is loading...", font_size=32))
        self.grid = GridLayout(cols=5, rows=6, size_hint=(1, 0.9))
        for _ in range(30):
            self.grid.add_widget(Label(text="", font_size=24))
        
        self.add_widget(self.grid)
        self.add_widget(Label(text="Type your guess below!", size_hint=(1, 0.1)))

class WordleApp(App):
    def build(self):
        return WordleGameUI()