from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.graphics import Color, Rectangle, Line, RoundedRectangle
from kivy.properties import StringProperty, ListProperty, NumericProperty
from kivy.animation import Animation

# Color constants for Wordle feedback
CORRECT_COLOR = (0.416, 0.667, 0.392, 1)  # #6aaa64 (green)
PRESENT_COLOR = (0.788, 0.706, 0.345, 1)  # #c9b458 (yellow)
ABSENT_COLOR = (0.471, 0.486, 0.494, 1)   # #787c7e (gray)
DEFAULT_COLOR = (0.071, 0.071, 0.075, 1)  # #121213 (dark gray/black)
WHITE_COLOR = (1, 1, 1, 1)                # #ffffff (white)
BORDER_COLOR = (0.3, 0.3, 0.3, 1)         # #4c4c4c (darker gray for border)

class Tile(Label):
    letter = StringProperty('')
    bg_color = ListProperty(DEFAULT_COLOR)
    border_color = ListProperty(BORDER_COLOR)
    border_width = NumericProperty(2)
    
    def __init__(self, **kwargs):
        # Set default properties
        kwargs.update({
            'size_hint': (None, None),
            'size': (62, 62),
            'font_name': 'Roboto-Bold',
            'font_size': 36,
            'bold': True,
            'color': WHITE_COLOR,
            'halign': 'center',
            'valign': 'middle'
        })
        super().__init__(**kwargs)
        
        # Enable text size to ensure centering works
        self.bind(size=self._update_text_size)
        
        # Set tile properties
        self.status = "default"
        self.bind(size=self._update_canvas, pos=self._update_canvas)
    
    def _update_text_size(self, instance, value):
        """Ensure text is properly centered in the tile"""
        self.text_size = value
        
    def _update_canvas(self, *args):
        """Update tile canvas drawing with proper colors and shape"""
        self.canvas.before.clear()
        with self.canvas.before:
            # Draw shadow effect (subtle drop shadow)
            Color(0, 0, 0, 0.2)
            Rectangle(pos=(self.x + 2, self.y - 2), size=self.size)
            
            # Set background color based on status
            if self.status == "correct":
                Color(*CORRECT_COLOR)
            elif self.status == "present":
                Color(*PRESENT_COLOR)
            elif self.status == "absent":
                Color(*ABSENT_COLOR)
            else:
                Color(*DEFAULT_COLOR)
            
            # Draw perfectly square background
            Rectangle(pos=self.pos, size=self.size)
            
            # Add border for empty tiles
            if self.status == "default":
                Color(*self.border_color)
                Line(rectangle=(self.x, self.y, self.width, self.height), width=self.border_width)

    def set_status(self, status):
        """Set the status of the tile and update its background."""
        self.status = status
        self._update_canvas()
        
    def animate_flip(self):
        """Animate the tile flipping when revealing feedback."""
        # First scale down vertically (flip down)
        anim1 = Animation(size_hint_y=0.1, duration=0.15)
        # Then scale back up with the new color (flip up)
        anim2 = Animation(size_hint_y=1, duration=0.15)
        
        # Use opacity as fallback if scaling doesn't work well
        backup_anim = Animation(opacity=0, duration=0.15) + Animation(opacity=1, duration=0.15)
        
        # Try scale animation first, fallback to opacity
        try:
            anim = anim1 + anim2
            anim.start(self)
        except:
            backup_anim.start(self)