from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.graphics import Color, Rectangle
from kivy.animation import Animation
from ..word_list import WordList
from ..game import WordleGame
from .keyboard import OnScreenKeyboard
from kivy.uix.image import Image
from .tile import Tile
from .themes import ThemeManager

WORD_LENGTH = 5
NUM_ATTEMPTS = 6

class WordleGameUI(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', padding=10, spacing=10, **kwargs)

        self.theme_manager = ThemeManager()

        # Header Bar
        header_bar = BoxLayout(size_hint=(1, 0.1), orientation='horizontal', spacing=10, padding=[10, 10, 10, 10])
        header_bar.add_widget(Button(text="❓", size_hint=(0.1, 1), on_press=self.show_help))
        header_bar.add_widget(Label(text="WORDLE", font_size=32, bold=True, halign="center", size_hint=(0.8, 1)))
        header_bar.add_widget(Button(text="📊", size_hint=(0.1, 1), on_press=self.show_stats))
        header_bar.add_widget(Button(text="⚙️", size_hint=(0.1, 1), on_press=self.open_settings))
        self.add_widget(header_bar)

        # Header
        header = BoxLayout(size_hint=(1, 0.1))
        header.add_widget(Label(text="Wordle", font_size=32, bold=True))
        new_game_button = Button(text="New Game", size_hint=(0.2, 1))
        new_game_button.bind(on_press=lambda instance: self.reset_game())
        header.add_widget(new_game_button)
        self.add_widget(header)

        # Load word and game state
        self.word_list = WordList()
        self.answer = self.word_list.get_random_word().upper()
        self.game = WordleGame(self.answer)
        self.guess_index = 0

        # Tile grid
        self.grid = GridLayout(cols=WORD_LENGTH, rows=NUM_ATTEMPTS, spacing=5, size_hint=(1, 0.9))
        self.tiles = [[Tile() for _ in range(WORD_LENGTH)] for _ in range(NUM_ATTEMPTS)]
        for row in self.tiles:
            for tile in row:
                self.grid.add_widget(tile)

        self.add_widget(self.grid)

        # Input box
        self.input = TextInput(hint_text="Enter a 5-letter word", multiline=False, size_hint=(1, 0.1), font_size=24)
        self.input.bind(on_text_validate=self.submit_guess)
        self.add_widget(self.input)

        # Add on-screen keyboard
        self.keyboard = OnScreenKeyboard()
        self.keyboard.bind(on_key_press=self.on_keyboard_input)
        self.add_widget(self.keyboard)

        self.stats = {
            'games_played': 0,
            'games_won': 0,
            'current_streak': 0,
            'max_streak': 0
        }

    def _update_background(self, instance, value):
        instance.canvas.before.clear()
        with instance.canvas.before:
            Color(0.9, 0.9, 0.9, 1)
            Rectangle(pos=instance.pos, size=instance.size)

    def _update_tile_background(self, tile, status):
        """Update the background color of a tile based on its status."""
        tile.canvas.before.clear()
        with tile.canvas.before:
            if status == "correct":
                Color(0.2, 0.8, 0.2, 1)  # green
            elif status == "present":
                Color(1, 1, 0.4, 1)      # yellow
            else:
                Color(0.6, 0.6, 0.6, 1)  # gray
            Rectangle(pos=tile.pos, size=tile.size)

    def _animate_tile(self, tile):
        """Animate a tile to flip when revealing feedback."""
        anim = Animation(opacity=0, duration=0.2) + Animation(opacity=1, duration=0.2)
        anim.start(tile)

    def on_keyboard_input(self, letter):
        if len(self.input.text) < WORD_LENGTH:
            self.input.text += letter

    def on_backspace(self):
        """Handle the BACKSPACE key to delete the last letter in the current guess."""
        if self.input.text:
            self.input.text = self.input.text[:-1]

    def submit_guess(self, instance):
        if self.guess_index >= NUM_ATTEMPTS:
            return

        guess = self.input.text.strip().upper()
        self.input.text = ""

        if len(guess) != WORD_LENGTH or not self.word_list.is_valid_word(guess):
            self.show_popup("Invalid guess", "Must be a valid 5-letter word.")
            return

        result = self.game.make_guess(guess)

        # Ensure result is iterable and valid
        if not isinstance(result, list):
            self.show_popup("Error", "Unexpected result from game logic.")
            return

        for col, (char, status) in enumerate(result):
            tile = self.tiles[self.guess_index][col]
            tile.text = char
            tile.set_status(status)
            tile.animate_flip()

            # Update keyboard key color
            self.keyboard.update_key_status(char, status)

        self.guess_index += 1

        if self.game.is_won():
            self.update_stats(won=True)
            self.show_popup("🎉 You Win!", f"You guessed it: {self.answer}")
        elif self.game.is_over():
            self.update_stats(won=False)
            self.show_popup("Game Over", f"The word was: {self.answer}")

    def on_size(self, *args):
        """Ensure tile colors are preserved when the window is resized."""
        for row in self.tiles:
            for tile in row:
                if tile.text:
                    # Determine the status based on the tile's text
                    if tile.text in self.answer:
                        if self.answer.index(tile.text) == self.tiles.index(row):
                            status = "correct"
                        else:
                            status = "present"
                    else:
                        status = "absent"
                    self._update_tile_background(tile, status)

    def reset_game(self):
        """Reset the game for a new round."""
        self.answer = self.word_list.get_random_word().upper()
        self.game = WordleGame(self.answer)
        self.guess_index = 0

        for row in self.tiles:
            for tile in row:
                tile.text = ""
                self._update_tile_background(tile, "default")

    def show_popup(self, title, message):
        popup = Popup(
            title=title,
            content=Label(text=message, halign="center"),
            size_hint=(0.8, 0.4),
        )
        popup.open()

    def update_stats(self, won):
        self.stats['games_played'] += 1
        if won:
            self.stats['games_won'] += 1
            self.stats['current_streak'] += 1
            self.stats['max_streak'] = max(self.stats['max_streak'], self.stats['current_streak'])
        else:
            self.stats['current_streak'] = 0

    def show_stats(self, instance=None):
        stats_message = (f"Games Played: {self.stats['games_played']}\n"
                         f"Games Won: {self.stats['games_won']}\n"
                         f"Current Streak: {self.stats['current_streak']}\n"
                         f"Max Streak: {self.stats['max_streak']}")
        self.show_popup("Statistics", stats_message)

    def open_settings(self, instance):
        """Open the settings menu."""
        content = BoxLayout(orientation='vertical', spacing=10, padding=10)

        dark_mode_button = Button(text="Toggle Dark Mode")
        dark_mode_button.bind(on_press=lambda x: self.toggle_dark_mode())
        content.add_widget(dark_mode_button)

        colorblind_mode_button = Button(text="Toggle Colorblind Mode")
        colorblind_mode_button.bind(on_press=lambda x: self.toggle_colorblind_mode())
        content.add_widget(colorblind_mode_button)

        popup = Popup(title="Settings", content=content, size_hint=(0.8, 0.4))
        popup.open()

    def toggle_dark_mode(self):
        self.theme_manager.toggle_dark_mode()
        # Apply dark mode changes (e.g., background color)
        if self.theme_manager.dark_mode:
            self.canvas.before.clear()
            with self.canvas.before:
                Color(0.07, 0.07, 0.07, 1)  # dark background
                Rectangle(pos=self.pos, size=self.size)
        else:
            self.canvas.before.clear()
            with self.canvas.before:
                Color(1, 1, 1, 1)  # light background
                Rectangle(pos=self.pos, size=self.size)

    def toggle_colorblind_mode(self):
        self.theme_manager.toggle_colorblind_mode()
        # Update tile colors based on the new mode
        for row in self.tiles:
            for tile in row:
                tile.set_status(tile.status)

    def show_help(self, instance):
        """Open the help section."""
        self.show_popup("Help", "Instructions and tips coming soon!")

class WordleApp(App):
    def build(self):
        return WordleGameUI()