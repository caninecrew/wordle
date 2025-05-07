from kivy.uix.label import Label
from kivy.animation import Animation
from kivy.graphics import Color, Rectangle, Line
from kivy.properties import ListProperty, NumericProperty

# Color constants for Wordle feedback
CORRECT_COLOR = (0.416, 0.667, 0.392, 1)  # #6aaa64 (green)
PRESENT_COLOR = (0.788, 0.706, 0.345, 1)  # #c9b458 (yellow)
ABSENT_COLOR = (0.471, 0.486, 0.494, 1)   # #787c7e (gray)
DEFAULT_COLOR = (0.071, 0.071, 0.075, 1)  # #121213 (dark gray/black)
WHITE_COLOR = (1, 1, 1, 1)                # #ffffff (white)
BORDER_COLOR = (0.3, 0.3, 0.3, 1)         # #4c4c4c (darker gray for border)

class Tile(Label):
    bg_color = ListProperty(DEFAULT_COLOR)
    border_width = NumericProperty(2)
    
    def __init__(self, **kwargs):
        # Set text styling before calling super()
        kwargs.update({
            'font_size': 36,
            'bold': True,
            'color': WHITE_COLOR,
            'halign': 'center',
            'valign': 'middle',
            'size_hint': (1, 1),
        })
        super().__init__(**kwargs)
        
        # Set tile properties
        self.status = "default"
        self.bind(size=self._update_canvas, pos=self._update_canvas)
    
    def _update_canvas(self, *args):
        self.canvas.before.clear()
        with self.canvas.before:
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
            size = min(self.width, self.height)
            x = self.center_x - size/2
            y = self.center_y - size/2
            Rectangle(pos=(x, y), size=(size, size))
            
            # Add border for empty tiles
            if self.status == "default":
                Color(*BORDER_COLOR)
                Line(rectangle=(x, y, size, size), width=self.border_width)

    def set_status(self, status):
        """Set the status of the tile and update its background."""
        self.status = status
        self._update_canvas()
        
    def animate_reveal(self):
        """Animate the tile flipping when revealing feedback."""
        # First fade out
        anim1 = Animation(opacity=0, duration=0.15)
        # Then fade back in
        anim2 = Animation(opacity=1, duration=0.15)
        
        # Chain animations
        anim = anim1 + anim2
        anim.start(self)