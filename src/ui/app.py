from kivy.app import App
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.animation import Animation
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.properties import ObjectProperty, ListProperty, BooleanProperty, StringProperty
from kivy.graphics import Color, Rectangle, Line
import json
import os

from ..word_list import WordList
from ..game import WordleGame
from .themes import ThemeManager
from .tile import Tile

from kivy.factory import Factory
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout

# Register the Tile template explicitly
Factory.register('Tile', cls=Label)

# Debugging: Print registered templates
print("Templates loaded:", Builder.templates.keys())

# Constants
WORD_LENGTH = 5
NUM_ATTEMPTS = 6

# Color constants
CORRECT_COLOR = (0.416, 0.667, 0.392, 1)  # #6aaa64 (green)
PRESENT_COLOR = (0.788, 0.706, 0.345, 1)  # #c9b458 (yellow)
ABSENT_COLOR = (0.471, 0.486, 0.494, 1)   # #787c7e (gray)
DEFAULT_COLOR = (0.071, 0.071, 0.075, 1)  # #121213 (dark gray/black)
WHITE_COLOR = (1, 1, 1, 1)                # #ffffff (white)
DARK_TEXT_COLOR = (0.1, 0.1, 0.1, 1)      # #1a1a1a (near black)
DEFAULT_KEY_COLOR = (0.82, 0.84, 0.85, 1) # #d3d6da (light gray)

class KeyButton(Button):
    key_id = StringProperty('')

class WordleGameUI(BoxLayout):
    tile_grid = ObjectProperty()
    keyboard = ObjectProperty()

    def on_kv_post(self, base_widget):
        """Populate the tile grid after the KV file is loaded."""
        tile_grid = self.ids.tile_grid
        tile_grid.clear_widgets()

        for _ in range(6 * 5):  # 6 rows x 5 columns
            tile = Tile()  # Create a Tile instance
            tile_grid.add_widget(tile)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Theme manager for color blind mode
        self.theme_manager = ThemeManager()
        
        # Statistics tracking
        self.stats = {
            'games_played': 0,
            'games_won': 0,
            'current_streak': 0,
            'max_streak': 0
        }
        
        # Load saved statistics
        self.load_statistics()
        
        # Game state initialization
        self.word_list = WordList()
        self.answer = self.word_list.get_random_word().upper()
        self.game = WordleGame(self.answer)
        self.guess_index = 0
        self.current_guess = ""
        
        # Explicitly initialize tile_grid as a GridLayout and add it to the layout
        self.tile_grid = GridLayout(cols=5, rows=6, spacing=dp(5), size_hint=(None, None))
        self.tile_grid.size = (dp(325), dp(390))
        self.tile_grid.pos_hint = {'center_x': 0.5, 'center_y': 0.5}
        self.add_widget(self.tile_grid)
        
        # Setup tiles and keyboard
        self.setup_tiles()
        
        # Window resize callback
        Window.bind(on_resize=self._on_window_resize)
    
    def save_statistics(self):
        """Save game statistics to file"""
        stats_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data')
        os.makedirs(stats_dir, exist_ok=True)
        stats_path = os.path.join(stats_dir, 'statistics.json')
        
        try:
            with open(stats_path, 'w') as f:
                json.dump(self.stats, f)
        except Exception as e:
            print(f"Error saving statistics: {e}")
    
    def load_statistics(self):
        """Load game statistics from file if available"""
        stats_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data')
        stats_path = os.path.join(stats_dir, 'statistics.json')
        
        if os.path.exists(stats_path):
            try:
                with open(stats_path, 'r') as f:
                    loaded_stats = json.load(f)
                    self.stats.update(loaded_stats)
            except Exception as e:
                print(f"Error loading statistics: {e}")
    
    def setup_tiles(self):
        """Set up tile grid programmatically"""
        self.tiles = []

        # Clear any existing widgets in the tile grid
        self.tile_grid.clear_widgets()

        # Create tiles
        for row in range(NUM_ATTEMPTS):
            tile_row = []
            for col in range(WORD_LENGTH):
                # Create a visible tile with proper styling
                tile = Label(
                    size_hint=(None, None),
                    size=(dp(56), dp(56)),
                    font_size=dp(32),
                    bold=True,
                    halign='center',
                    valign='middle',
                    text='',
                    color=(1, 1, 1, 1)  # White text color
                )
                # Set tile status attribute
                tile.status = "default"

                # Explicitly set up the canvas to ensure visibility
                with tile.canvas.before:
                    Color(0.12, 0.12, 0.12, 1)  # Dark gray background
                    Rectangle(pos=tile.pos, size=tile.size)
                    Color(0.3, 0.3, 0.3, 1)  # Border color
                    Line(rectangle=(tile.x, tile.y, tile.width, tile.height), width=2)

                tile_row.append(tile)
                self.tile_grid.add_widget(tile)
                print(f"Added tile at row {row}, col {col}")  # Debugging log
            self.tiles.append(tile_row)

        # Force layout update
        self.tile_grid.do_layout()
    
    def _on_window_resize(self, instance, width, height):
        """Handle window resize to maintain proper proportions"""
        # Recalculate tile sizes based on new window width
        tile_grid = self.ids.tile_grid
        tile_size = min(dp(62), (width - dp(100)) / WORD_LENGTH)
        grid_width = (tile_size * WORD_LENGTH) + ((WORD_LENGTH - 1) * dp(5))
        grid_height = (tile_size * NUM_ATTEMPTS) + ((NUM_ATTEMPTS - 1) * dp(5))
        
        # Update grid container size
        tile_grid.size = (grid_width, grid_height)
        
        # Update individual tile sizes
        for row in self.tiles:
            for tile in row:
                tile.size = (tile_size, tile_size)
    
    def on_keyboard_input(self, letter):
        """Handle letter key presses"""
        if len(self.current_guess) < WORD_LENGTH and not self.game.is_over():
            # Add letter to current guess
            self.current_guess += letter
            # Update tile display
            tile = self.tiles[self.guess_index][len(self.current_guess) - 1]
            tile.text = letter
            # Add subtle pop animation
            self._animate_tile_input(tile)
    
    def _animate_tile_input(self, tile):
        """Add a subtle pop animation when letter is entered"""
        orig_size = tile.size[:]
        anim = (
            Animation(size=(orig_size[0] * 1.1, orig_size[1] * 1.1), duration=0.05) + 
            Animation(size=orig_size, duration=0.05)
        )
        anim.start(tile)
    
    def on_backspace(self, instance=None):
        """Handle backspace key press"""
        if self.current_guess and not self.game.is_over():
            # Get tile reference before removing the letter
            tile = self.tiles[self.guess_index][len(self.current_guess) - 1]
            # Remove last letter and clear tile
            self.current_guess = self.current_guess[:-1]
            tile.text = ""
            # Update the tile status
            self._update_tile_status(tile, "default")
    
    def on_enter(self, instance=None):
        """Submit current guess"""
        if len(self.current_guess) == WORD_LENGTH and not self.game.is_over():
            if not self.word_list.is_valid_word(self.current_guess):
                self.show_invalid_word()
                return
                
            # Submit guess to game logic
            result = self.game.make_guess(self.current_guess)
            
            # Ensure result is valid
            if not isinstance(result, list):
                self.show_popup("Error", "Unexpected result from game logic.")
                return
                
            # Animate tiles with delay for flip effect
            self.animate_reveal_tiles(result)
            
            # Move to next row
            self.guess_index += 1
            self.current_guess = ""
            
            # Check game over conditions after animation completes
            Clock.schedule_once(lambda dt: self.check_game_status(), 1.5)
    
    def _update_tile_status(self, tile, status):
        """Update the visual status of a tile"""
        with tile.canvas:
            tile.canvas.clear()
            if status == "correct":
                Color(*CORRECT_COLOR)
            elif status == "present":
                Color(*PRESENT_COLOR)
            elif status == "absent":
                Color(*ABSENT_COLOR)
            else:
                Color(*DEFAULT_COLOR)
            Rectangle(pos=tile.pos, size=tile.size)

            # Add border for default tiles
            if status == "default":
                Color(0.3, 0.3, 0.3, 1)
                Line(rectangle=(tile.x, tile.y, tile.width, tile.height), width=2)
    
    def _animate_tile_flip(self, tile):
        """Animate the tile flipping"""
        anim = Animation(opacity=0, duration=0.15) + Animation(opacity=1, duration=0.15)
        anim.start(tile)
    
    def update_key_status(self, letter, status):
        """Update key status with color change"""
        letter = letter.upper()
        if letter in self.keys:
            key = self.keys[letter]
            # Only update to a "higher" status (correct > present > absent)
            if status == "correct":
                self._set_key_color(key, CORRECT_COLOR)
            elif status == "present" and key.background_color != CORRECT_COLOR:
                self._set_key_color(key, PRESENT_COLOR)
            elif status == "absent" and key.background_color not in [CORRECT_COLOR, PRESENT_COLOR]:
                self._set_key_color(key, ABSENT_COLOR)
    
    def _set_key_color(self, key, color):
        """Set key color with animation"""
        key.background_color = color
        if color != DEFAULT_KEY_COLOR:
            key.color = WHITE_COLOR
        else:
            key.color = DARK_TEXT_COLOR
    
    def show_invalid_word(self):
        """Show animation for invalid word with proper shake and error message"""
        row_tiles = self.tiles[self.guess_index]
        tile_grid = self.tile_grid
        start_pos = tile_grid.pos
        
        # Create a short toast message that appears and fades out
        toast = Label(
            text="Not in word list",
            font_size=dp(16),
            color=DARK_TEXT_COLOR,
            size_hint=(None, None),
            size=(dp(200), dp(40)),
            opacity=0
        )
        
        # Add toast to the layout temporarily
        self.add_widget(toast)
        toast.pos = (self.width/2 - toast.width/2, 
                     tile_grid.y - dp(40))
        
        # Fade in the toast
        anim_in = Animation(opacity=1, duration=0.2)
        # Hold it visible
        anim_hold = Animation(opacity=1, duration=1.0) 
        # Fade it out
        anim_out = Animation(opacity=0, duration=0.5)
        
        # Chain animations
        toast_anim = anim_in + anim_hold + anim_out
        toast_anim.bind(on_complete=lambda *args: self.remove_widget(toast))
        toast_anim.start(toast)
        
        # Shake animation for the grid
        shake_anim = (
            Animation(pos=(start_pos[0] - dp(10), start_pos[1]), duration=0.1) + 
            Animation(pos=(start_pos[0] + dp(10), start_pos[1]), duration=0.1) + 
            Animation(pos=(start_pos[0] - dp(5), start_pos[1]), duration=0.1) + 
            Animation(pos=(start_pos[0] + dp(5), start_pos[1]), duration=0.1) + 
            Animation(pos=start_pos, duration=0.1)
        )
        
        shake_anim.start(tile_grid)
        
        # After shake completes, clear the current guess
        def clear_guess(dt):
            for i in range(len(self.current_guess)):
                tile = row_tiles[i]
                tile.text = ""
                self._update_tile_status(tile, "default")
            self.current_guess = ""
        
        Clock.schedule_once(clear_guess, 1.5)
    
    def check_game_status(self):
        """Check if game is won or lost"""
        if self.game.is_won():
            self.update_stats(won=True)
            self.show_game_over_popup("🎉 You Won!", f"The word was: {self.answer}")
        elif self.game.is_over():
            self.update_stats(won=False)
            self.show_game_over_popup("Game Over", f"The word was: {self.answer}")
    
    def update_stats(self, won):
        """Update game statistics"""
        self.stats['games_played'] += 1
        if won:
            self.stats['games_won'] += 1
            self.stats['current_streak'] += 1
            self.stats['max_streak'] = max(self.stats['max_streak'], self.stats['current_streak'])
        else:
            self.stats['current_streak'] = 0
    
    def show_game_over_popup(self, title, message):
        """Show game over popup with stats and play again option"""
        content = BoxLayout(orientation='vertical', spacing=10, padding=10)
        
        content.add_widget(Label(text=message, font_size=20))
        content.add_widget(Label(text=f"Games Played: {self.stats['games_played']}", font_size=16))
        content.add_widget(Label(text=f"Win Rate: {int(self.stats['games_won']/max(1, self.stats['games_played'])*100)}%", font_size=16))
        content.add_widget(Label(text=f"Current Streak: {self.stats['current_streak']}", font_size=16))
        content.add_widget(Label(text=f"Max Streak: {self.stats['max_streak']}", font_size=16))
        
        from kivy.uix.button import Button
        play_again_btn = Button(text="Play Again", size_hint_y=None, height=50)
        play_again_btn.bind(on_press=lambda x: self.reset_game())
        content.add_widget(play_again_btn)
        
        popup = Popup(title=title, content=content, size_hint=(0.8, 0.6), auto_dismiss=False)
        play_again_btn.bind(on_press=popup.dismiss)
        popup.open()
    
    def show_popup(self, title, message):
        """Show a simple popup message"""
        content = Label(text=message, font_size=18)
        popup = Popup(title=title, content=content, size_hint=(0.8, 0.3))
        popup.open()
    
    def reset_game(self, instance=None):
        """Reset the game with a new word"""
        self.answer = self.word_list.get_random_word().upper()
        self.game = WordleGame(self.answer)
        self.guess_index = 0
        self.current_guess = ""
        
        # Clear all tiles
        for row in self.tiles:
            for tile in row:
                tile.text = ""
                self._update_tile_status(tile, "default")
        
        # Reset keyboard colors
        for letter, key in self.keys.items():
            self._set_key_color(key, DEFAULT_KEY_COLOR)

    def animate_reveal_tiles(self, result):
        """Animate the tiles with the results of the guess"""
        # Ensure the results match the current guess length
        if len(result) != len(self.tiles[self.guess_index]):
            return

        # Update each tile with delay for flip effect
        for i, status in enumerate(result):
            tile = self.tiles[self.guess_index][i]
            # Schedule the update with increasing delay
            Clock.schedule_once(
                lambda dt, tile=tile, status=status: self._animate_reveal_tile(tile, status),
                i * 0.2  # Delay increases for each tile
            )
            # Also update the keyboard key status
            Clock.schedule_once(
                lambda dt, letter=tile.text, status=status: self.update_key_status(letter, status),
                i * 0.2 + 0.1  # Slightly after tile animation
            )
    
    def _animate_reveal_tile(self, tile, status):
        """Animate a single tile flip and reveal"""
        # First half of flip (become invisible)
        anim1 = Animation(opacity=0, duration=0.15)
        
        # Second half of flip (show result and become visible)
        anim2 = Animation(opacity=1, duration=0.15)
        
        # Function to update tile during the middle of the animation
        def update_tile_status(anim, tile):
            self._update_tile_status(tile, status)
        
        # Bind the update to occur after the first animation
        anim1.bind(on_complete=update_tile_status)
        
        # Chain animations
        anim = anim1 + anim2
        anim.start(tile)

class WordleApp(App):
    def build(self):
        try:
            # Load the KV file for the layout
            Builder.load_file("wordle.kv")
            
            # Set window title and background
            self.title = 'Wordle'
            Window.clearcolor = (1, 1, 1, 1)
            
            # Create and return the main UI
            game_ui = WordleGameUI()
            
            # Force an initial layout calculation
            def init_layout(dt):
                game_ui.do_layout()
            Clock.schedule_once(init_layout, 0)
            
            return game_ui
        except Exception as e:
            print(f"Error during app build: {e}")
            raise

    def on_start(self):
        # Populate the tile grid with 30 tile widgets only if it is empty
        tile_grid = self.root.tile_grid
        if not tile_grid.children:
            for row in range(6):
                for col in range(5):
                    tile = Tile()
                    tile_grid.add_widget(tile)

from flask import Flask

app = Flask(__name__)

@app.route("/")
def wordle():
    # Serve the Wordle game page directly as a string
    return """
    <!DOCTYPE html>
    <html lang=\"en\" class=\"pz-dont-touch\">
    <head>
        <meta http-equiv=\"Content-Type\" content=\"text/html; charset=UTF-8\">
        <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">
        <meta name=\"theme-color\" content=\"#000000\">
        <title>Wordle — The New York Times</title>
        <meta property=\"description\" content=\"Guess the hidden word in 6 tries. A new puzzle is available each day.\">
        <meta property=\"og:title\" content=\"Wordle - A daily word game\">
        <meta property=\"og:description\" content=\"Guess the hidden word in 6 tries. A new puzzle is available each day.\">
        <style>
            body {
                font-family: Arial, sans-serif;
                margin: 0;
                padding: 0;
                background-color: #f7fafc;
                color: #333;
            }
            h1 {
                text-align: center;
                margin-top: 20px;
            }
        </style>
    </head>
    <body>
        <h1>Wordle — The New York Times</h1>
        <p style=\"text-align: center;\">Guess the hidden word in 6 tries. A new puzzle is available each day.</p>
    </body>
    </html>
    """

if __name__ == "__main__":
    app.run(debug=True)