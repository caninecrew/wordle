from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.graphics import Color, Rectangle
from ..word_list import WordList
from ..game import WordleGame

WORD_LENGTH = 5
NUM_ATTEMPTS = 6

class WordleGameUI(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', padding=10, spacing=10, **kwargs)

        # Load word and game state
        self.word_list = WordList()
        self.answer = self.word_list.get_random_word().upper()
        self.game = WordleGame(self.answer)
        self.guess_index = 0

        # Tile grid
        self.grid = GridLayout(cols=WORD_LENGTH, rows=NUM_ATTEMPTS, spacing=5, size_hint=(1, 0.9))
        self.tiles = [[Label(text="", font_size=32, halign="center", valign="middle") for _ in range(WORD_LENGTH)] for _ in range(NUM_ATTEMPTS)]
        for row in self.tiles:
            for tile in row:
                tile.bind(size=self._update_background)
                self.grid.add_widget(tile)

        self.add_widget(self.grid)

        # Input box
        self.input = TextInput(hint_text="Enter a 5-letter word", multiline=False, size_hint=(1, 0.1), font_size=24)
        self.input.bind(on_text_validate=self.submit_guess)
        self.add_widget(self.input)

    def _update_background(self, instance, value):
        instance.canvas.before.clear()
        with instance.canvas.before:
            Color(0.9, 0.9, 0.9, 1)
            Rectangle(pos=instance.pos, size=instance.size)

    def submit_guess(self, instance):
        if self.guess_index >= NUM_ATTEMPTS:
            return

        guess = self.input.text.strip().upper()
        self.input.text = ""

        if len(guess) != WORD_LENGTH or not self.word_list.is_valid_word(guess):
            self.show_popup("Invalid guess", "Must be a valid 5-letter word.")
            return

        result = self.game.make_guess(guess)  # Returns [(char, status), ...]

        for col, (char, status) in enumerate(result):
            tile = self.tiles[self.guess_index][col]
            tile.text = char
            with tile.canvas.before:
                tile.canvas.before.clear()
                if status == "correct":
                    Color(0.2, 0.8, 0.2, 1)  # green
                elif status == "present":
                    Color(1, 1, 0.4, 1)      # yellow
                else:
                    Color(0.6, 0.6, 0.6, 1)  # gray
                Rectangle(pos=tile.pos, size=tile.size)

        self.guess_index += 1

        if self.game.is_won():
            self.show_popup("🎉 You Win!", f"You guessed it: {self.answer}")
        elif self.game.is_over():
            self.show_popup("Game Over", f"The word was: {self.answer}")

    def show_popup(self, title, message):
        popup = Popup(title=title,
                      content=Label(text=message, font_size=20),
                      size_hint=(0.7, 0.4))
        popup.open()

class WordleApp(App):
    def build(self):
        return WordleGameUI()