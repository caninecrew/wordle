from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.graphics import Color, RoundedRectangle
from kivy.properties import ListProperty, StringProperty
from kivy.animation import Animation

# Color constants for Wordle feedback (matching tile.py)
CORRECT_COLOR = (0.416, 0.667, 0.392, 1)  # #6aaa64 (green)
PRESENT_COLOR = (0.788, 0.706, 0.345, 1)  # #c9b458 (yellow)
ABSENT_COLOR = (0.471, 0.486, 0.494, 1)   # #787c7e (gray)
DEFAULT_KEY_COLOR = (0.82, 0.84, 0.85, 1) # #d3d6da (light gray)
WHITE_COLOR = (1, 1, 1, 1)                # #ffffff (white)
DARK_TEXT_COLOR = (0.1, 0.1, 0.1, 1)      # #1a1a1a (near black)

class KeyboardKey(Button):
    bg_color = ListProperty(DEFAULT_KEY_COLOR)
    key_text = StringProperty('')
    
    def __init__(self, **kwargs):
        # Extract key_text if provided
        if 'key_text' in kwargs:
            self.key_text = kwargs.pop('key_text')
            
        # Set default properties
        kwargs.update({
            'size_hint': (None, None),
            'size': (40, 60),
            'background_color': (0, 0, 0, 0),  # Transparent background
            'background_normal': '',
            'background_down': '',
            'font_name': 'Roboto',
            'font_size': 18,
            'bold': True,
            'color': DARK_TEXT_COLOR,
            'text': self.key_text
        })
        super().__init__(**kwargs)
        
        # Bind events
        self.bind(size=self._update_canvas, pos=self._update_canvas)
        self.bind(on_press=self._on_press, on_release=self._on_release)
    
    def _update_canvas(self, *args):
        """Update key canvas with rounded rectangle and proper color"""
        self.canvas.before.clear()
        with self.canvas.before:
            Color(*self.bg_color)
            RoundedRectangle(pos=self.pos, size=self.size, radius=[6])
    
    def _on_press(self, instance):
        """Darken the key when pressed"""
        self.orig_color = self.bg_color[:]
        self.bg_color = tuple(c * 0.9 for c in self.bg_color[:3]) + (1,)
    
    def _on_release(self, instance):
        """Restore color when released (unless it's been set to a status color)"""
        if hasattr(self, 'orig_color') and self.bg_color != CORRECT_COLOR and \
           self.bg_color != PRESENT_COLOR and self.bg_color != ABSENT_COLOR:
            self.bg_color = self.orig_color
    
    def set_status(self, status):
        """Set the key status with animation"""
        target_color = DEFAULT_KEY_COLOR
        if status == "correct":
            target_color = CORRECT_COLOR
            self.color = WHITE_COLOR
        elif status == "present":
            target_color = PRESENT_COLOR
            self.color = WHITE_COLOR
        elif status == "absent":
            target_color = ABSENT_COLOR
            self.color = WHITE_COLOR
            
        # Animate color change
        anim = Animation(bg_color=target_color, duration=0.2)
        anim.start(self)

class OnScreenKeyboard(BoxLayout):
    def __init__(self, **kwargs):
        kwargs.update({
            'orientation': 'vertical',
            'spacing': 8,
            'padding': [10, 10, 10, 10],
            'size_hint': (1, None),
            'height': 200  # Will be adjusted based on key sizes
        })
        super().__init__(**kwargs)
        
        self.keys = {}
        self.create_keyboard_layout()
    
    def create_keyboard_layout(self):
        # Top row: Q-P
        top_row = BoxLayout(spacing=4, size_hint=(1, None), height=60)
        for letter in "QWERTYUIOP":
            key = KeyboardKey(key_text=letter)
            key.bind(on_press=self.on_key_press)
            self.keys[letter] = key
            top_row.add_widget(key)
        self.add_widget(top_row)
        
        # Middle row: A-L with some padding to center
        mid_row = BoxLayout(spacing=4, size_hint=(1, None), height=60)
        mid_row.add_widget(BoxLayout(size_hint_x=0.05))  # Left padding
        for letter in "ASDFGHJKL":
            key = KeyboardKey(key_text=letter)
            key.bind(on_press=self.on_key_press)
            self.keys[letter] = key
            mid_row.add_widget(key)
        mid_row.add_widget(BoxLayout(size_hint_x=0.05))  # Right padding
        self.add_widget(mid_row)
        
        # Bottom row: ENTER, Z-M, BACKSPACE
        bottom_row = BoxLayout(spacing=4, size_hint=(1, None), height=60)
        
        # Enter key (wider)
        enter_key = KeyboardKey(key_text="ENTER", size=(65, 60))
        enter_key.bind(on_press=self.on_enter)
        bottom_row.add_widget(enter_key)
        
        # Letter keys
        for letter in "ZXCVBNM":
            key = KeyboardKey(key_text=letter)
            key.bind(on_press=self.on_key_press)
            self.keys[letter] = key
            bottom_row.add_widget(key)
        
        # Backspace key (wider with icon)
        back_key = KeyboardKey(key_text="⌫", size=(65, 60))
        back_key.bind(on_press=self.on_backspace)
        bottom_row.add_widget(back_key)
        
        self.add_widget(bottom_row)
    
    def on_key_press(self, instance):
        """Handle letter key presses and pass to parent"""
        if self.parent and hasattr(self.parent, 'on_keyboard_input'):
            self.parent.on_keyboard_input(instance.key_text)
    
    def on_enter(self, instance):
        """Handle ENTER key press"""
        if self.parent and hasattr(self.parent, 'on_enter'):
            self.parent.on_enter(instance)
    
    def on_backspace(self, instance):
        """Handle BACKSPACE key press"""
        if self.parent and hasattr(self.parent, 'on_backspace'):
            self.parent.on_backspace()
    
    def update_key_status(self, letter, status):
        """Update key status with color change"""
        letter = letter.upper()
        if letter in self.keys:
            key = self.keys[letter]
            # Only update to a "higher" status (correct > present > absent)
            current_color = tuple(key.bg_color)
            if (status == "correct" or 
                (status == "present" and current_color != CORRECT_COLOR) or
                (status == "absent" and current_color not in [CORRECT_COLOR, PRESENT_COLOR])):
                key.set_status(status)