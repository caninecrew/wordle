from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.graphics import Color, RoundedRectangle
from kivy.properties import ListProperty

# Color constants for Wordle feedback (matching tile.py)
CORRECT_COLOR = (0.416, 0.667, 0.392, 1)  # #6aaa64 (green)
PRESENT_COLOR = (0.788, 0.706, 0.345, 1)  # #c9b458 (yellow)
ABSENT_COLOR = (0.471, 0.486, 0.494, 1)   # #787c7e (gray)
DEFAULT_KEY_COLOR = (0.82, 0.84, 0.85, 1) # #d3d6da (light gray)
WHITE_COLOR = (1, 1, 1, 1)                # #ffffff (white)

class KeyboardKey(Button):
    bg_color = ListProperty(DEFAULT_KEY_COLOR)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_color = (0, 0, 0, 0)  # Transparent background, we'll draw our own
        self.background_normal = ''
        self.background_down = ''
        self.font_size = 18
        self.bold = True
        self.color = (0.1, 0.1, 0.1, 1)  # Dark text color
        self.bind(size=self._update_canvas, pos=self._update_canvas)
        
        # For hover effect
        self.bind(on_touch_down=self._on_touch_down)
        self.bind(on_touch_up=self._on_touch_up)
        
    def _update_canvas(self, *args):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(*self.bg_color)
            RoundedRectangle(pos=self.pos, size=self.size, radius=[6])
    
    def _on_touch_down(self, instance, touch):
        if self.collide_point(*touch.pos):
            self.bg_color = tuple(c * 0.9 for c in self.bg_color[:3]) + (1,)  # Darken on press
        return super().on_touch_down(touch)
    
    def _on_touch_up(self, instance, touch):
        if self.collide_point(*touch.pos):
            self.bg_color = DEFAULT_KEY_COLOR
        return super().on_touch_up(touch)
    
    def set_status(self, status):
        if status == "correct":
            self.bg_color = CORRECT_COLOR
            self.color = WHITE_COLOR
        elif status == "present":
            self.bg_color = PRESENT_COLOR
            self.color = WHITE_COLOR
        elif status == "absent":
            self.bg_color = ABSENT_COLOR
            self.color = WHITE_COLOR
        self._update_canvas()

class OnScreenKeyboard(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.spacing = 8
        self.padding = [10, 10, 10, 10]
        self.size_hint_y = 0.3
        
        self.keys = {}
        self.create_keyboard_layout()
    
    def create_keyboard_layout(self):
        # Top row: Q-P
        top_row = BoxLayout(spacing=4, size_hint=(1, 0.33))
        for letter in "QWERTYUIOP":
            key = KeyboardKey(text=letter, size_hint_x=1/10)
            key.bind(on_press=self.on_key_press)
            self.keys[letter] = key
            top_row.add_widget(key)
        self.add_widget(top_row)
        
        # Middle row: A-L with some padding to center
        mid_row = BoxLayout(spacing=4, size_hint=(1, 0.33))
        mid_row.add_widget(BoxLayout(size_hint_x=0.05))  # Left padding
        for letter in "ASDFGHJKL":
            key = KeyboardKey(text=letter, size_hint_x=0.1)
            key.bind(on_press=self.on_key_press)
            self.keys[letter] = key
            mid_row.add_widget(key)
        mid_row.add_widget(BoxLayout(size_hint_x=0.05))  # Right padding
        self.add_widget(mid_row)
        
        # Bottom row: ENTER, Z-M, BACKSPACE
        bottom_row = BoxLayout(spacing=4, size_hint=(1, 0.33))
        
        # Enter key
        enter_key = KeyboardKey(text="ENTER", size_hint_x=0.15)
        enter_key.bind(on_press=self.on_enter)
        bottom_row.add_widget(enter_key)
        
        # Letter keys
        for letter in "ZXCVBNM":
            key = KeyboardKey(text=letter, size_hint_x=0.1)
            key.bind(on_press=self.on_key_press)
            self.keys[letter] = key
            bottom_row.add_widget(key)
        
        # Backspace key
        back_key = KeyboardKey(text="⌫", size_hint_x=0.15)
        back_key.bind(on_press=self.on_backspace)
        bottom_row.add_widget(back_key)
        
        self.add_widget(bottom_row)
    
    def on_key_press(self, instance):
        """Handle letter key presses and pass to parent"""
        if self.parent and hasattr(self.parent, 'on_keyboard_input'):
            self.parent.on_keyboard_input(instance.text)
    
    def on_enter(self, instance):
        if self.parent and hasattr(self.parent, 'on_enter'):
            self.parent.on_enter(instance)
    
    def on_backspace(self, instance):
        if self.parent and hasattr(self.parent, 'on_backspace'):
            self.parent.on_backspace()
    
    def update_key_status(self, letter, status):
        letter = letter.upper()
        if letter in self.keys:
            key = self.keys[letter]
            # Only update to a "higher" status (correct > present > absent)
            if status == "correct":
                key.set_status("correct")
            elif status == "present" and key.bg_color != CORRECT_COLOR:
                key.set_status("present")
            elif status == "absent" and key.bg_color not in [CORRECT_COLOR, PRESENT_COLOR]:
                key.set_status("absent")