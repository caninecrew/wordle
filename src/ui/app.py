from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.uix.popup import Popup
from kivy.graphics import Color, Rectangle
from kivy.animation import Animation
from kivy.clock import Clock
from kivy.core.window import Window

from ..word_list import WordList
from ..game import WordleGame
from .keyboard import OnScreenKeyboard, DEFAULT_KEY_COLOR
from .tile import Tile
from .themes import ThemeManager

# Constants
WORD_LENGTH = 5
NUM_ATTEMPTS = 6
WHITE_COLOR = (1, 1, 1, 1)
DARK_TEXT_COLOR = (0.1, 0.1, 0.1, 1)

class WordleGameUI(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', padding=15, spacing=15, **kwargs)
        
        # Set up white background for the entire app
        with self.canvas.before:
            Color(*WHITE_COLOR)
            self.background = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self._update_background, size=self._update_background)
        
        # Theme manager for color blind mode
        self.theme_manager = ThemeManager()
        
        # Game state initialization
        self.word_list = WordList()
        self.answer = self.word_list.get_random_word().upper()
        self.game = WordleGame(self.answer)
        self.guess_index = 0
        self.current_guess = ""
        
        # Statistics tracking
        self.stats = {
            'games_played': 0,
            'games_won': 0,
            'current_streak': 0,
            'max_streak': 0
        }
        
        # Title Bar - Clean and minimal
        self.title_bar = BoxLayout(size_hint=(1, 0.1), minimum_height=60)
        title_label = Label(
            text="WORDLE", 
            font_size=38, 
            bold=True,
            color=DARK_TEXT_COLOR,
            halign='center'
        )
        self.title_bar.add_widget(title_label)
        self.add_widget(self.title_bar)
        
        # Spacer to center content vertically
        self.add_widget(BoxLayout(size_hint=(1, 0.05)))
        
        # Tile grid - Perfectly square tiles with space between
        self.grid = GridLayout(
            cols=WORD_LENGTH,
            rows=NUM_ATTEMPTS,
            spacing=6,
            size_hint=(1, 0.5),
            padding=[20, 20, 20, 20]
        )
        
        # Create tiles with the new design
        self.tiles = [[Tile() for _ in range(WORD_LENGTH)] for _ in range(NUM_ATTEMPTS)]
        for row in self.tiles:
            for tile in row:
                self.grid.add_widget(tile)
        
        self.add_widget(self.grid)
        
        # Spacer between grid and keyboard
        self.add_widget(BoxLayout(size_hint=(1, 0.05)))
        
        # Keyboard with new design
        self.keyboard = OnScreenKeyboard(size_hint=(1, 0.3))
        self.add_widget(self.keyboard)
        
        # Bind keyboard callbacks
        self.keyboard.bind(
            on_key_press=self.on_keyboard_input,
            on_enter=self.on_enter,
            on_backspace=self.on_backspace
        )
    
    def _update_background(self, instance, value):
        """Keep background updated when window size changes"""
        self.background.pos = instance.pos
        self.background.size = instance.size
    
    def on_keyboard_input(self, letter):
        """Handle letter key presses on the virtual keyboard"""
        if len(self.current_guess) < WORD_LENGTH and not self.game.is_over():
            # Add letter to current guess
            self.current_guess += letter
            # Update tile display
            tile = self.tiles[self.guess_index][len(self.current_guess) - 1]
            tile.text = letter
    
    def on_backspace(self, instance=None):
        """Handle backspace key press"""
        if self.current_guess and not self.game.is_over():
            # Remove last letter
            self.current_guess = self.current_guess[:-1]
            # Clear tile display
            tile = self.tiles[self.guess_index][len(self.current_guess)]
            tile.text = ""
    
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
    
    def animate_reveal_tiles(self, result):
        """Animate tile reveals one by one with delay"""
        for col, (char, status) in enumerate(result):
            tile = self.tiles[self.guess_index][col]
            # Schedule animation with delay based on position
            delay = col * 0.2  # Delay each tile by 0.2s
            Clock.schedule_once(lambda dt, t=tile, s=status: self.reveal_tile(t, s), delay)
            # Update keyboard status after all tiles are revealed
            Clock.schedule_once(lambda dt, c=char, s=status: self.keyboard.update_key_status(c, s), 
                                delay + 0.2)
    
    def reveal_tile(self, tile, status):
        """Reveal a single tile with animation"""
        tile.set_status(status)
        tile.animate_reveal()
    
    def show_invalid_word(self):
        """Show animation for invalid word with proper shake and error message"""
        row_tiles = self.tiles[self.guess_index]
        start_pos = self.grid.pos
        
        # Create a short toast message that appears and fades out
        toast = Label(
            text="Not in word list",
            font_size=16,
            color=(0, 0, 0, 1),
            size_hint=(None, None),
            size=(200, 40),
            pos_hint={'center_x': 0.5},
            opacity=0
        )
        
        # Add toast to the layout temporarily
        self.add_widget(toast)
        toast.pos = (self.width/2 - toast.width/2, self.grid.y - 40)
        
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
            Animation(pos=(start_pos[0] - 10, start_pos[1]), duration=0.1) + 
            Animation(pos=(start_pos[0] + 10, start_pos[1]), duration=0.1) + 
            Animation(pos=(start_pos[0] - 5, start_pos[1]), duration=0.1) + 
            Animation(pos=(start_pos[0] + 5, start_pos[1]), duration=0.1) + 
            Animation(pos=start_pos, duration=0.1)
        )
        
        shake_anim.start(self.grid)
        
        # After shake completes, clear the current guess
        def clear_guess(dt):
            for i in range(len(self.current_guess)):
                tile = row_tiles[i]
                tile.text = ""
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
        
    def show_settings(self, instance=None):
        """Show settings popup with theme options"""
        content = BoxLayout(orientation='vertical', spacing=10, padding=10)
        
        from kivy.uix.button import Button
        colorblind_btn = Button(
            text="Toggle Colorblind Mode",
            size_hint_y=None,
            height=50
        )
        colorblind_btn.bind(on_press=lambda x: self.toggle_colorblind_mode())
        content.add_widget(colorblind_btn)
        
        popup = Popup(title="Settings", content=content, size_hint=(0.8, 0.3))
        close_btn = Button(text="Close", size_hint_y=None, height=50)
        close_btn.bind(on_press=popup.dismiss)
        content.add_widget(close_btn)
        popup.open()
    
    def toggle_colorblind_mode(self):
        """Toggle colorblind mode"""
        self.theme_manager.toggle_colorblind_mode()
        # Update all tiles and keyboard colors based on new mode
        self.refresh_all_colors()
    
    def refresh_all_colors(self):
        """Refresh colors for all UI elements based on current theme"""
        # Update tiles
        for row_idx, row in enumerate(self.tiles):
            for col_idx, tile in enumerate(row):
                if tile.status != "default":
                    tile._update_canvas()
        
        # Update keyboard
        for letter, key in self.keyboard.keys.items():
            if key.bg_color != DEFAULT_KEY_COLOR:
                key._update_canvas()
    
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
                tile.status = "default"
                tile._update_canvas()
        
        # Reset keyboard colors
        for letter, key in self.keyboard.keys.items():
            key.bg_color = DEFAULT_KEY_COLOR
            key.color = DARK_TEXT_COLOR
            key._update_canvas()

class WordleApp(App):
    def build(self):
        # Set window title
        self.title = 'Wordle'
        # White background for the app window
        Window.clearcolor = (1, 1, 1, 1)
        return WordleGameUI()